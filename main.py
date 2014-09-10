#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

from models import Student, Assignment, GradeEntry
import logging
import utils
import csv_handlers
import delete_handlers


# Jinja environment instance necessary to use Jinja templates.
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)), autoescape=True)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        assignments, assignments_map = utils.get_assignments(user)
        students, students_map, teams = utils.get_students(user)
        grade_entries = utils.get_grade_entries(user, assignments_map, students_map)
        # Optional adding some meta data about the assignments for the badge icon.
        assignment_badge_data = {}
        for assignment in assignments:
            assignment_badge_data[assignment.key] = [0, 0]  # Count, Score Accumulator
        for grade_entry in grade_entries:
            assignment_badge_data[grade_entry.assignment_key][0] += 1
            assignment_badge_data[grade_entry.assignment_key][1] += grade_entry.score
        for assignment in assignments:
            metadata = assignment_badge_data[assignment.key]
            if metadata[0] > 0:
                metadata.append(metadata[1] / metadata[0])  # Average
            else:
                metadata.append("na")  # Average is NA
        template = jinja_env.get_template("templates/graderecorder.html")
        self.response.out.write(template.render({'assignments': assignments,
                                                 'active_assignemnt': self.request.get('active_assignemnt'),
                                                 'students': students,
                                                 'teams': teams,
                                                 'grade_entries': grade_entries,
                                                 'assignment_badge_data': assignment_badge_data,
                                                 'user_email': user.email(),
                                                 'logout_url': users.create_logout_url("/")}))

    def post(self):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
            return
        next_active_assignemnt = None
        if (self.request.get('type') == 'Student'):
            rose_username = self.request.get('rose_username')
            new_student = Student(parent=utils.get_parent_key(user),
                                  id=rose_username,
                                  first_name=self.request.get('first_name'),
                                  last_name=self.request.get('last_name'),
                                  rose_username=rose_username,
                                  team=self.request.get('team'))
            new_student.put()
        elif (self.request.get('type') == 'Assignment'):
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
            next_active_assignemnt = active_assignment.key.urlsafe()
        elif (self.request.get('type') == 'SingleGradeEntry'):
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
            next_active_assignemnt = assignment_key.urlsafe()
        elif (self.request.get('type') == 'TeamGradeEntry'):
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
            next_active_assignemnt = assignment_key.urlsafe()
        if next_active_assignemnt:
          self.redirect("/?active_assignemnt=" + next_active_assignemnt)
        else:
          self.redirect("/")

app = webapp2.WSGIApplication([
    ("/", MainHandler),
    ("/bulk_student_import", csv_handlers.BulkStudentImportAction),
    ("/delete_student", delete_handlers.DeleteStudentAction),
    ("/delete_assignment", delete_handlers.DeleteAssignmentAction),
    ("/delete_grade_entry", delete_handlers.DeleteGradeEntryAction),
    ("/grade_recorder_grades.csv", csv_handlers.ExportCsvAction)
], debug=True)
