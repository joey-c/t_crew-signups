import entities
import datetime
import defaults

#converts unicode to ascii for inputs
def convert(input):
  if isinstance(input, dict):
    return {convert(key): convert(value) for key, value in input.iteritems()}
  elif isinstance(input, list):
    return [convert(element) for element in input]
  elif isinstance(input, unicode):
    return input.encode('ascii')
  else:
    return input

#returns all slots.
def getSlots():
	q = entities.Slot.query()
	q_sorted = q.order(entities.Slot.startTime)
	return q_sorted.fetch()

#returns upcoming slots
def getUpcomingSlots():
	now = datetime.datetime.utcnow()
	q = entities.Slot.query(entities.Slot.startTime > now)
	q_sorted = q.order(entities.Slot.startTime)
	return q_sorted.fetch()

#creates Account if new user
def checkUser(user):
	key = user.user_id()
	acc = entities.Account.get_by_id(key)
	if not acc:
		newUser = entities.Account(
			id=key,
			email=user.email(),
			name=defaults.name,
			matric=defaults.matric,
			mobile=defaults.mobile)
		newUser.put()