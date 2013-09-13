import cgi
import jinja2
import logging
import os
import webapp2
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

###openID providers
providers = {
	'NUS': 'openid.nus.edu.sg'
}

###admin emails
admins = ['cyq@nus.edu.sg']

###defaults
default_name = 'Name'
default_matric = 'Matric No.'
default_mobile = 'Contact No.'

###helper functions
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

class Slot(ndb.Model):
	startTime = ndb.DateTimeProperty()
	totalSpaces = ndb.IntegerProperty()
	registrants = ndb.KeyProperty(kind='Account', repeated=True)

class Account(ndb.Model):
	name = ndb.StringProperty()
	email = ndb.StringProperty()
	matric = ndb.StringProperty()
	mobile = ndb.StringProperty()
	slots = ndb.KeyProperty(kind='Slot', repeated=True)

class Admin(Account):
 pass

#returns all slots.
def getSlots():
	q = Slot.query()
	q_sorted = q.order(Slot.startTime)
	return q_sorted.fetch()

#returns upcoming slots
def getUpcomingSlots():
	now = datetime.datetime.utcnow()
	q = Slot.query(Slot.startTime > now)
	q_sorted = q.order(Slot.startTime)
	return q_sorted.fetch()

#creates Account if new user
#creates Admin and Account if new admin
def checkUser(user):
	key = user.user_id()
	if user.email() in admins:
		admin = Admin.get_by_id(key)
		if not admin:
			newAdmin = Admin(
				id=key,
				email=user.email(),
				name=default_name,
				matric=default_matric,
				mobile=default_mobile)
			newAdmin.put()
	acc = Account.get_by_id(key)
	if not acc:
		newUser = Account(
			id=key,
			email=user.email(),
			name=default_name,
			matric=default_matric,
			mobile=default_mobile)
		newUser.put()

class MainHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			LoggedInHandler().get(self)
		else:
			LoginHandler().get(self)

###if user is not logged in, show slots and timings etc but don't allow booking
class LoginHandler(webapp2.RequestHandler):
	def get(self, page):
		template = jinja_environment.get_template('templates/login.html')
		template_values = {
			'logInOut': users.create_login_url(federated_identity=providers['NUS']),
			'logInOut_linkText': 'Login',
			'now': datetime.datetime.now(),
			'slots': getUpcomingSlots()
			}
		page.response.write(template.render(template_values))

####if user is logged in, show stuff and allowing booking
###'want to book a slot? login here with NUS openID'
class LoggedInHandler(webapp2.RequestHandler):
	def get(self, page):
		user = users.get_current_user()
		if user:
			checkUser(user)
			acc = Account.get_by_id(user.user_id())
			template = jinja_environment.get_template('templates/logged_in.html')
			template_values = {
				'userAcc': acc,
				'slots': getUpcomingSlots(),
				'now': datetime.datetime.now(),
				'logInOut': users.create_logout_url(page.request.uri),
				'logInOut_linkText': 'Logout',
				'userName': acc.name,
				'userMatric': acc.matric,
				'userMobile': acc.mobile,
				'registeredSlots': acc.slots,
				'loggedIn': True
			}
			page.response.write(template.render(template_values))
		else:
			self.redirect('/')

	def post(self):
		pass

###must login to GAE and manually add admin
###for adding / editing slots and viewing registrants
class AdminHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			checkUser(user)
			adminAcc = Admin.get_by_id(user.user_id())
			if adminAcc:
				template = jinja_environment.get_template('templates/admin.html')
				template_values = {
					'userAcc': adminAcc,
					'slots': getSlots(),
					'now': datetime.datetime.now(),
					'logInOut': users.create_logout_url(self.request.uri),
					'logInOut_linkText': 'Logout'
				}
				self.response.write(template.render(template_values))

		else:
			self.redirect('/')

	def post(self):
		inputDate = convert(self.request.get('date')) #DD/MM/YYYY
		inputStart = convert(self.request.get('start'))
		inputSpaces = convert(self.request.get('spaces'))
		year = int(inputDate[6:])
		month = int(inputDate[3:5])
		day = int(inputDate[0:2])
		hour = int(inputStart[0:2])
		minute = int(inputStart[2:])
		newSlot = Slot(
			startTime= datetime.datetime(year, month, day, hour, minute),
			totalSpaces= int(inputSpaces))
		newSlot.put()
		self.redirect('/admin')

class UpdateHandler(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		acc = Account.get_by_id(user.user_id())
		inputName = convert(self.request.get('name'))
		inputMatric = convert(self.request.get('matric'))
		inputMobile = convert(self.request.get('contact'))
		if inputName:
			acc.name = inputName
		if inputMatric:
			acc.matric = inputMatric
		if inputMobile:
			acc.mobile = inputMobile
		acc.put()
		self.redirect('/')

class SignUpHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		checkUser(user)
		acc = Account.get_by_id(user.user_id())
		if acc.name == default_name or acc.matric == default_matric or acc.mobile == default_mobile:
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
			checkUser(user)
			acc = Account.get_by_id(user.user_id())
			template = jinja_environment.get_template('templates/logged_in.html')
			template_values = {
				'userAcc': acc,
				'slots': getUpcomingSlots(),
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
		checkUser(user)
		acc = Account.get_by_id(user.user_id())
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

class RemoveHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		checkUser(user)
		acc = Account.get_by_id(user.user_id())
		q_string = self.request.query_string
		q_list = q_string.split('&')
		if len(q_list) > 1:
			pass #error
		else:
			slot_key = ndb.Key(urlsafe=q_list[0])
			slot = slot_key.get()
			if slot:
				for registrant in slot.registrants:
					registrant.remove(slot_key)
					registrant.put()
				slot_key.delete()
			else:
				pass #error
		self.redirect('/admin')

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/admin', AdminHandler),
	('/remove', RemoveHandler),
	('/update', UpdateHandler),
	('/signup', SignUpHandler),
	('/deregister', DeregisterHandler),
	('/signup_error', SignUpErrorHandler)],
  debug=True)