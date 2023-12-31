from myflaskapp.validation import TextValidation
from myflaskapp.runPHP import RunPHP
from datetime import datetime
import requests
import os
import random
from pathlib import Path
from myflaskapp.config import config
import threading
import time
import re
import sys
import json

from zipfile import ZipFile
from io import BytesIO

class getAssignmentInfo:

    def __init__(self, canvas, cohort, assignment_id, test):
        self.canvas = canvas
        self.test = test
        self.threads = []
        self.json_data = []
        self.rating_data = []
        self.warnings = []

        self.start_time = time.time()

        self.json_data = self.getAssignmentDataFromCmon(cohort, assignment_id)

        # ToDo do we realy need this, we get one assignment back right?
        for json_item in self.json_data:
            if int(assignment_id) == int(json_item["assignment_id"]):
                self.getListAssignments(json_item)
                self.print_time('Waiting for threads to finish')
                self.wait_for_all_threads()
                return

    
    def print_time(self, message=''):
        end = time.time()
        elapsed_time_ms = (end - self.start_time) * 1000  # Convert seconds to milliseconds
        if (message):
            print(f"{message}, ", end="")
        print(f"time elapsed: {elapsed_time_ms} ms")
    
    
    def getAssignmentDataFromCmon(self, cohort, assignment_id):
        url = "http://" + cohort + ".cmon.ovh/api/nakijken?aid=" + assignment_id
        print(f"\n\n----\nGet assignment data from: {url}")
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
        else:
            print(f"Error: {response.status_code}")
            return f"Error: {response.status_code}"

        return json_data

        if not json_data:
            return None
        
        # ToDo do we realy need this, we get one assignment back right?
        for json_item in json_data:
            if int(assignment_id) == int(json_item["assignment_id"]):
                results = self.listUnratedAssignments(json_item)
                return results


    def getDayMonth(self, date_string):
        date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        month = date_object.strftime("%m")  # Full month name
        day = date_object.strftime("%d")  # Zero-padded day
        return day + "-" + month


    def getInitials(self, name):
        name = name.split()
        return name[0][:1].upper() + name[1][:1].upper()

    def strip_html_tags(self, html_string):
        # Match HTML tags
        tags = re.findall(r'<.*?>', html_string)
        
        # Replace each tag with a stripped version (remove <, /, and >)
        for tag in tags:
            stripped_tag = tag.replace("<", "").replace(">", "").replace("/", "")
            html_string = html_string.replace(tag, stripped_tag)
            
        return html_string

    def getComments(self, submission):
        comments = "" # get all comments
        for comment in reversed(submission.submission_comments):
            this_date = self.getDayMonth(comment["created_at"])
            this_initials = self.getInitials(comment["author_name"])
            stripped_comments = self.strip_html_tags(comment["comment"])
            comments += (
                f'•<i>{this_date} {this_initials}</i>: {stripped_comments} <br><br>'
            )
        return comments


    def downloadPicture(self, url, file_name): #  multi threaded
        page = requests.get(url)
        with open(file_name, "wb") as f:
            f.write(page.content)


    def loadPicture(self, url, picture_file_name):
        path = "temp_att/"  # save file to temp directory, ToDo when and how to clean temp dir?

        if not os.path.exists(path):
            os.makedirs(path)

        file_name = path + picture_file_name

        if not os.path.isfile(file_name):
            thread = threading.Thread(target=self.downloadPicture, args=(url, file_name))
            thread.start()
            self.threads.append(thread)
            # self.downloadPicture(url, file_name)

        return file_name


    def loadZip(self, url, picture_file_name):
        response  = requests.get(url)
        zip_buffer = BytesIO(response.content)
        with ZipFile(zip_buffer, 'r') as zip_ref:
            return zip_ref.namelist()


    def wait_for_all_threads(self):
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join()


    # Formatting the online entries
    # does not work becuase the content is not clean and contains HTML meta information. Needs to be investigated further.
    def format_text(self, text):
        return(text)
        words = text.split(" ")
        current_line = ""
        result = ""
        
        for word in words:
            if len(current_line + word) > 160:
                result += current_line + "\n"
                current_line = ""
            
            if current_line:
                current_line += " "
            current_line += word
        
        if current_line:
            result += current_line
        
        return result

    
    def getAttachments(self, submission, file_type, words_in_order, points_possible, file_name_match, php_exe):

        list_of_dicts = []

        for attachment in submission.attachments:
            att_file_type = Path(attachment.filename).suffix.lower()[1:]

            rating = None
            file_name = None
            file_content = None
            words_correct = None
            rating = None 
            sort_order=9
            feedback = self.getFeedback(True)

            file_name = ( str(submission.id) + "-" + str(attachment.id) + "." + att_file_type )
            file_name = self.loadPicture( attachment.url, file_name )  # return file name with path

            if att_file_type in ["png", "pdf", "jpg", "zip", "jpeg", "webp", "mp4"]:  # no word matching, no auto rating
                sort_order = 2
                if att_file_type == "zip":
                    file_content = "click on file name (left)"
                    sort_order = 1

            else:  # anything else, do the word matching
                response = requests.get(attachment.url, allow_redirects=True)
                file_content = response.content.decode('utf-8', errors='replace')
                if (att_file_type == file_type and (file_name_match is None or file_name_match in attachment.filename) ): # only perform matching (auto-correct) if file type is requested file type, ToDo test this!
                    validation = TextValidation(file_content, words_in_order)
                    words_correct = validation.wordsMatched
                    match = validation.match
                    if match: #  if (position > 1): # position of last found word and will be -1 when a word is not found.
                        rating = points_possible
                    else:
                        rating = 0
                        feedback = self.getFeedback(False)
            
            if att_file_type == "php" and int(php_exe):
                ran_PHP = RunPHP(file_content)
                php_output = ran_PHP.output
            else:
                php_output = None


            list_of_dicts.append(
                {
                    "att_file_type": att_file_type,
                    "org_file_name": attachment.filename,
                    "file_name": file_name,
                    "file_content": file_content,
                    "rating": rating,
                    "feedback": feedback,
                    "words_correct": words_correct,
                    "words_in_order": words_in_order,
                    "number_of_words": len(words_in_order),
                    "sort_order": sort_order,
                    "php_output" : php_output,
                }
            )

        #  sort
        list_of_dicts = sorted( list_of_dicts, key=lambda x: (x["sort_order"]) )

        return list_of_dicts


    def getOnlineText(self, submission, words_in_order, points_possible):
    
        list_of_dicts = []
        sort_order=9

        file_content = self.format_text(submission.body)
        validation = TextValidation(file_content, words_in_order)
        words_correct = validation.wordsMatched
        match = validation.match
        if match: #  if (position > 1): # position of last found word and will be -1 when a word is not found.
            rating = points_possible
            feedback = self.getFeedback(True)
        else:
            rating = 0
            feedback = self.getFeedback(False)

        list_of_dicts.append(
            {
                "att_file_type": "online",
                "org_file_name": "\"online\"",
                "file_name": None,
                "file_content": file_content,
                "rating": rating,
                "feedback": feedback,
                "words_correct": words_correct,
                "words_in_order": words_in_order,
                "number_of_words": len(words_in_order),
                "sort_order": sort_order,
            }
        )

        return list_of_dicts


    def getFeedback(self, positief):
        # ToDo check if config exists and if it is a list.
        if positief:
            selected_feedback = random.choice(config["default_feedback_pos"])
        else:
            selected_feedback = random.choice(config["default_feedback_neg"])

        return selected_feedback


    def getOneAssignment(self, course, assignment, submission, params): #  multi threaded
        course_id = params["course_id"]
        assignment_id = params["assignment_id"]
        words_in_order = params['words_in_order']
        file_type = params['file_type']
        file_name_match = params['file_name']
        att_expected = params["attachments"]
        hint = params.get("hint", "")
        config_string = params.get("config")

        if (config_string):
            php_exe = int( json.loads( config_string )['php_exe'] )
        else:
            php_exe = 0

        # print(f"PHP_EXE: {php_exe}")

        if self.test:
            user = submission.user["name"]
            print(f"Checking {user} {submission.submitted_at} - {submission.workflow_state}")

        if submission.submitted_at is None: #  no submission present, continue
            return
        if not self.test and submission.workflow_state == "graded": #  if graded (and not in testmode), continue
            return

        comments = self.getComments(submission)

        if (submission.submission_type == "online_text_entry" ):
            json_attachments = self.getOnlineText(submission, words_in_order, assignment.points_possible)
        else:
            json_attachments = self.getAttachments(submission, file_type, words_in_order, assignment.points_possible, file_name_match, php_exe) #  submission object, file_type to check, words to check, max score possible, file_name to match

        #  determine lowest rated attachment and promote rating and feedback to overall rating and feedback
        try:
            max_points = int(assignment.points_possible) 
        except Exception as e:
            raise Exception("An error occurred: assignment is not configured to be rated with point. Check assignment definition in Canvas.") from e

        overall_rating = max_points
        overall_feedback = self.getFeedback(True)
        if att_expected is not None and int(len(submission.attachments)) != int(att_expected):
            overall_rating = 0
            overall_feedback = "Opdracht kan niet worden beoordeeld omdat het aantal bijlagen (attachments) niet correct is."

        for att in json_attachments:
            #  if file_type == att['att_file_type']:
            if att['rating'] is not None and att['rating'] < overall_rating:
                overall_rating =  att['rating']
                overall_feedback = att['feedback']

        if submission.attempt > 3:
            overall_rating = int(int(overall_rating) * 0.8)
            max_points = int(int(max_points) * 0.8)


        self.rating_data.append(
             {
                "assignment_id": assignment_id,
                "assignment_name": assignment.name,
                "course_id": course_id,
                "course_name": course.name,
                "submission_id": submission.id,
                "attempt": submission.attempt,
                "points_possible": int(assignment.points_possible),
                "max_points": max_points,
                "alt_feedback": self.getFeedback(True),
                "user": submission.user["name"],
                "user_id": submission.user["id"],
                "number_of_words": len(words_in_order),
                "hint": hint,
                "comments": comments,
                "test": self.test,
                "attachements": json_attachments,
                "att_expected": att_expected,
                "number_of_att": len(submission.attachments),
                "rating": overall_rating,
                "feedback": overall_feedback
            }
        )
        return
        

    def getListAssignments(self, params):
        #  all properties in item are delivered by the API from CMON, we will find allunrated items from the assignment specified in item (json)
        course_id = params["course_id"]
        assignment_id = params["assignment_id"]

        try:
            course = self.canvas.get_course(course_id)
            assignment = course.get_assignment(assignment_id)
        except:
            print(f"No access to course {course_id} and/or assignment {assignment_id}")
            return "No API access to course {course_id} and/or assignment {assignment_id}"

        # Get all submissions
        submissions = assignment.get_submissions(bucket="ungraded", include=["user", "submission_comments"])
        submission_count = sum(1 for _ in submissions)

        # removeTempFiles() # ToDo remove files when rating is done!?

        print(f"Checking course {course_id} assignment {assignment_id}, found {submission_count} submissions")

        for i, submission in enumerate(submissions):

            if self.test and i > 20: #  if we are testing we could have too many (graded) submissions so stop (break) after 6
                break

            # each assignment is processed in a seperate thread
            # self.getOneAssignment(course, assignment, submission, item)
            thread = threading.Thread(target=self.getOneAssignment, args=(course, assignment, submission, params))
            thread.start()
            self.threads.append(thread)

        return