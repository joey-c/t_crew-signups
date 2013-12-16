import cgi
import jinja2
import logging
import os
import webapp2
import helpers
import entities
import adminFunctions
import userFunctions
from google.appengine.api import users

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

###openID providers
providers = {
	'NUS': 'openid.nus.edu.sg'
}

###admin emails
admins = ['cyq@nus.edu.sg']

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
			helpers.checkUser(user)
			adminAcc = entities.Admin.get_by_id(user.user_id())
			if adminAcc:
				template_values = adminFunctions.getTemplateValues(adminAcc, page)
				template = jinja_environment.get_template('templates/edit_sessions.html')
			else:
				acc = entities.Account.get_by_id(user.user_id())
				test = userFunctions.SignUpHandler()
				template_values = userFunctions.getTemplateValues(acc, page)
				template = jinja_environment.get_template('templates/logged_in.html')

			page.response.write(template.render(template_values))
		else:
			self.redirect('/')

class UpdateProfileHandler(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		acc = entities.Account.get_by_id(user.user_id())
		inputName = helpers.convert(self.request.get('name'))
		inputMatric = helpers.convert(self.request.get('matric'))
		inputMobile = helpers.convert(self.request.get('contact'))
		if inputName:
			acc.name = inputName
		if inputMatric:
			acc.matric = inputMatric
		if inputMobile:
			acc.mobile = inputMobile
		acc.put()
		self.redirect('/')

app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/update', UpdateProfileHandler),

	#regular users' functions
	('/signup', userFunctions.SignUpHandler),
	('/deregister', userFunctions.DeregisterHandler),
	('/signup_error', userFunctions.SignUpErrorHandler),

	#admin functions
	('/remove', adminFunctions.RemoveSessionsHandler),
	('/edit_sessions', adminFunctions.EditSessionsHandler),
	('/edit_front', adminFunctions.EditFrontHandler),
	('/admin_settings', adminFunctions.SettingsHandler),
	('/admin_acc_settings', adminFunctions.AccSettingsHandler)],
  debug=True)