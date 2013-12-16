from google.appengine.ext import ndb

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