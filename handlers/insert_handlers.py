import base_handlers
from google.appengine.ext import ndb
from models import Student, Assignment, GradeEntry
import utils


class AddStudentAction(base_handlers.BaseAction):
  def post_for_user(self, user):
    rose_username = self.request.get('rose_username')
    new_student = Student(parent=utils.get_parent_key(user),
                          id=rose_username,
                          first_name=self.request.get('first_name'),
                          last_name=self.request.get('last_name'),
                          rose_username=rose_username,
                          team=self.request.get('team'))
    new_student.put()


class InsertAssignmentAction(base_handlers.BaseAction):
  def post_for_user(self, user):
    active_assignment = Assignment(parent=utils.get_parent_key(user),
                                   name=self.request.get('assignment_name'))
    if len(self.request.get('assignment_entity_key')) > 0:
        assignment_key = ndb.Key(urlsafe=self.request.get('assignment_entity_key'))
        if assignment_key:
            assignment = assignment_key.get()
            if assignment:
                active_assignment = assignment
                active_assignment.name = self.request.get('assignment_name')
    active_assignment.put()
    return active_assignment.key.urlsafe()


class AddSingleGradeEntryAction(base_handlers.BaseAction):
  def post_for_user(self, user):
    assignment_key = ndb.Key(urlsafe=self.request.get('assignment_key'))
    student_key = ndb.Key(urlsafe=self.request.get('student_key'))
    student = student_key.get()
    score = int(self.request.get('score'))
    new_grade_entry = GradeEntry(parent=assignment_key,
                                 id=student.rose_username,
                                 assignment_key=assignment_key,
                                 student_key=student_key,
                                 score=score)
    new_grade_entry.put()
    return assignment_key.urlsafe()


class AddTeamGradeEntryAction(base_handlers.BaseAction):
  def post_for_user(self, user):
    assignment_key = ndb.Key(urlsafe=self.request.get('assignment_key'))
    score = int(self.request.get('score'))
    team = self.request.get('team')
    student_query = Student.query(Student.team==team, ancestor=utils.get_parent_key(user))
    for student in student_query:
        new_grade_entry = GradeEntry(parent=assignment_key,
                                     id=student.rose_username,
                                     assignment_key=assignment_key,
                                     student_key=student.key,
                                     score=score)
        new_grade_entry.put()
    return assignment_key.urlsafe()

