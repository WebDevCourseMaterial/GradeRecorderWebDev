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
import os

from google.appengine.api import users
from handlers import base_handlers, insert_handlers, delete_handlers, csv_handlers
import jinja2
import utils
import webapp2

# Jinja environment instance necessary to use Jinja templates.
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                               autoescape=True)

class MainHandler(base_handlers.BasePage):
    def get_for_user(self, user):
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


app = webapp2.WSGIApplication([
    ("/", MainHandler),
    ("/add_student", insert_handlers.AddStudentAction),
    ("/insert_assignment", insert_handlers.InsertAssignmentAction),
    ("/add_single_grade_entry", insert_handlers.AddSingleGradeEntryAction),
    ("/add_team_grade_entry", insert_handlers.AddTeamGradeEntryAction),
    ("/delete_student", delete_handlers.DeleteStudentAction),
    ("/delete_assignment", delete_handlers.DeleteAssignmentAction),
    ("/delete_grade_entry", delete_handlers.DeleteGradeEntryAction),
    ("/bulk_student_import", csv_handlers.BulkStudentImportAction),
    ("/grade_recorder_grades.csv", csv_handlers.ExportCsvAction)
], debug=True)
