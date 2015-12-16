import defaults
import helpers
import webapp2
import datetime
from google.appengine.api import users

def getTemplateValues(adminAcc, origRequest):
	return {'userAcc': adminAcc,
					'now': datetime.datetime.now(),
					'logInOut': users.create_logout_url(origRequest.request.uri),
					'logInOut_linkText': 'Logout',
					'userName': acc.name,
					'userMatric': acc.matric,
					'userMobile': acc.mobile,
					'admin': True,
					'adminSessions': '/admin_sessions',
					'adminEditFront': '/admin_edit_front',
					'adminSettings': '/admin_settings',
					'accSettings': '/acc_settings'
					}

###must login to GAE and manually add admin
###for adding / editing slots and viewing registrants
class EditSessionsHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			helpers.checkUser(user)
			adminAcc = Admin.get_by_id(user.user_id())
			if adminAcc:
				template = jinja_environment.get_template('templates/admin_sessions.html')
				template_values = getTemplateValues(adminAcc, self)
				template_values.update({'slots': helpers.getSlots()})
				self.response.write(template.render(template_values))
		else:
			self.redirect('/')

	def post(self):
		inputDate = helpers.convert(self.request.get('date')) #DD/MM/YYYY
		inputStart = helpers.convert(self.request.get('start'))
		inputSpaces = helpers.convert(self.request.get('spaces'))
		year = int(inputDate[6:])
		month = int(inputDate[3:5])
		day = int(inputDate[0:2])
		hour = int(inputStart[0:2])
		minute = int(inputStart[2:])
		newSlot = Slot(
			startTime= datetime.datetime(year, month, day, hour, minute),
			totalSpaces= int(inputSpaces))
		newSlot.put()
		self.redirect('/admin_sessions')

class RemoveSessionsHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		helpers.checkUser(user)
		acc = Account.get_by_id(user.user_id())
		q_string = self.request.query_string
		q_list = q_string.split('&')
		if len(q_list) > 1:
			pass #error
		else:
			slot_key = ndb.Key(urlsafe=q_list[0])
			slot = slot_key.get()
			if slot:
				for registrant_key in slot.registrants:
					registrant = registrant_key.get()
					registrant.slots.remove(slot_key)
					registrant.put()
				slot_key.delete()
			else:
				pass #error
		self.redirect('/admin_sessions')

class EditFrontHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			helpers.checkUser(user)
			adminAcc = Admin.get_by_id(user.user_id())
			if adminAcc:
				template = jinja_environment.get_template('templates/admin_front.html')
				template_values = getTemplateValues(adminAcc, self)
				self.response.write(template.render(template_values))
		else:
			self.redirect('/')

class SettingsHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			helpers.checkUser(user)
			adminAcc = Admin.get_by_id(user.user_id())
			if adminAcc:
				template = jinja_environment.get_template('templates/admin_settings.html')
				template_values = getTemplateValues(adminAcc, self)
				self.response.write(template.render(template_values))
		else:
			self.redirect('/')

class AccSettingsHandler(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			helpers.checkUser(user)
			adminAcc = Admin.get_by_id(user.user_id())
			if adminAcc:
				template = jinja_environment.get_template('templates/account_settings.html')
				template_values = getTemplateValues(adminAcc, self)
				self.response.write(template.render(template_values))
		else:
			self.redirect('/')
