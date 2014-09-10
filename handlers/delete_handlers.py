import base_handlers
from google.appengine.ext import ndb
import utils


class DeleteStudentAction(base_handlers.BaseAction):
    def post_for_user(self, user):
        if self.request.get('student_to_delete_key') == "AllStudents":
          utils.remove_all_students(user)
        else:
          student_key = ndb.Key(urlsafe=self.request.get('student_to_delete_key'))
          utils.remove_all_grades_for_student(user, student_key)
          student_key.delete();


class DeleteAssignmentAction(base_handlers.BaseAction):
    def post_for_user(self, user):
        assignment_key = ndb.Key(urlsafe=self.request.get('assignment_to_delete_key'))
        utils.remove_all_grades_for_assignment(user, assignment_key)
        assignment_key.delete();


class DeleteGradeEntryAction(base_handlers.BaseAction):
    def post_for_user(self, user):
        grade_entry_key = ndb.Key(urlsafe=self.request.get('grade_entry_to_delete_key'))
        grade = grade_entry_key.get()
        next_active_assignemnt = grade.assignment_key.urlsafe()
        grade_entry_key.delete();
        return next_active_assignemnt

