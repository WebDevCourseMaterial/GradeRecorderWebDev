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
  def post(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))
      return
    next_active_assignemnt = self.post_for_user(user)
    if next_active_assignemnt:
      self.redirect("/?active_assignemnt=" + next_active_assignemnt)
    else:
      self.redirect("/")

  def post_for_user(self, user):
    raise Exception("Subclasses must override this method")