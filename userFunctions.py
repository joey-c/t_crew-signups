import datetime
import defaults
import entities
import helpers
import webapp2
from google.appengine.api import users

def getTemplateValues(acc, origRequest):
	return {'userAcc': acc,
					'slots': helpers.getUpcomingSlots(),
					'now': datetime.datetime.now(),
					'logInOut': users.create_logout_url(origRequest.request.uri),
					'logInOut_linkText': 'Logout',
					'userName': acc.name,
					'userMatric': acc.matric,
					'userMobile': acc.mobile,
					'registeredSlots': acc.slots,
					'loggedIn': True,
					'admin': False,
					}

class SignUpHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		helpers.checkUser(user)
		acc = entities.Account.get_by_id(user.user_id())
		if acc.name == defaults.name or acc.matric == defaults.matric or acc.mobile == defaults.mobile:
			self.redirect('/signup_error')
		else:
			q_string = self.request.query_string
			q_list = q_string.split('&')
			if len(q_list) > 1:
				pass #error
			else:
				slot_key = ndb.Key(urlsafe=q_list[0])
				slot = slot_key.get()
				if slot:
					if acc.key not in slot.registrants:
						slot.registrants.append(acc.key)
						slot.put()
					if slot.key not in acc.slots:
						acc.slots.append(slot_key)
						acc.put()
				else:
					pass #error
			self.redirect('/')

class SignUpErrorHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			helpers.checkUser(user)
			acc = entities.Account.get_by_id(user.user_id())
			template = jinja_environment.get_template('templates/logged_in.html')
			template_values = {
				'userAcc': acc,
				'slots': helpers.getUpcomingSlots(),
				'now': datetime.datetime.now(),
				'logInOut': users.create_logout_url(self.request.uri),
				'logInOut_linkText': 'Logout',
				'userName': acc.name,
				'userMatric': acc.matric,
				'userMobile': acc.mobile,
				'registeredSlots': acc.slots,
				'loggedIn': True,
				'signupError': True
			}
			self.response.write(template.render(template_values))
		else:
			self.redirect('/')

class DeregisterHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		helpers.checkUser(user)
		acc = entities.Account.get_by_id(user.user_id())
		q_string = self.request.query_string
		q_list = q_string.split('&')
		if len(q_list) > 1:
			pass #error
		else:
			slot_key = ndb.Key(urlsafe=q_list[0])
			slot = slot_key.get()
			if slot:
				if acc.key in slot.registrants:
					slot.registrants.remove(acc.key)
					slot.put()
				if slot.key in acc.slots:
					acc.slots.remove(slot_key)
					acc.put()
			else:
				pass #error
		self.redirect('/')