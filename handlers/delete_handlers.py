import base_handlers
from google.appengine.api import users
from google.appengine.ext import ndb
import utils


class DeleteStudentAction(base_handlers.BaseAction):
    def post_for_user(self, user):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        if self.request.get('student_to_delete_key') == "AllStudents":
          utils.remove_all_students(user)
        else:
          student_key = ndb.Key(urlsafe=self.request.get('student_to_delete_key'))
          utils.remove_all_grades_for_student(user, student_key)
          student_key.delete();
        self.redirect(self.request.referer)


class DeleteAssignmentAction(base_handlers.BaseAction):
    def post_for_user(self, user):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        assignment_key = ndb.Key(urlsafe=self.request.get('assignment_to_delete_key'))
        utils.remove_all_grades_for_assignment(user, assignment_key)
        assignment_key.delete();
        self.redirect("/")

class DeleteGradeEntryAction(base_handlers.BaseAction):
    def post_for_user(self, user):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        grade_entry_key = ndb.Key(urlsafe=self.request.get('grade_entry_to_delete_key'))
        grade = grade_entry_key.get()
        next_active_assignemnt = grade.assignment_key.urlsafe()
        grade_entry_key.delete();
        self.redirect("/?active_assignemnt=" + next_active_assignemnt)

