from google.appengine.api import users
import webapp2

class BasePage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    self.get_for_user(user)

  def get_for_user(self, user):
    raise Exception("Subclasses must override this method")


class BaseAction(webapp2.RequestHandler):
  pass
  # TODO: Implement