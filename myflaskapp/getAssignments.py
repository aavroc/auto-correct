from myflaskapp.validation import TextValidation
from datetime import datetime
import requests
import os
import random
from pathlib import Path
from myflaskapp.config import config


class getAssignmentInfo:
    def __init__(self, canvas, cohort, assignment_id):
        self.canvas=canvas
        self.assignment_data = self.getAssignmentDataFromCmon(cohort, assignment_id)
        return 
        self.unrated_assignment_data = self.listUnratedAssignments(self.assignment_data)
        return 

    
    def getAssignmentDataFromCmon(self, cohort, assignment_id):
        url = "http://" + cohort + ".cmon.ovh/api/nakijken?aid=" + assignment_id
        print(f"url: {url}")
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
        else:
            print(f"Error: {response.status_code}")
            return f"Error: {response.status_code}"

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


    def getComments(self, submission):
        comments = "" # get all comments
        for comment in reversed(submission.submission_comments):
            this_date = getDayMonth(comment["created_at"])
            this_initials = getInitials(comment["author_name"])
            comments += (
                f'<i>{this_date} {this_initials}</i>: {comment["comment"]}<br><br>'
            )
        return comments


    def loadPicture(self, url, picture_file_name):
        path = "static/temp/img"  # save file to temp directory, ToDo when and how to clean temp dir?

        if not os.path.exists(path):
            os.makedirs(path)

        file_name = path + picture_file_name

        if not os.path.isfile(file_name):
            page = requests.get(url)
            with open(file_name, "wb") as f:
                f.write(page.content)

        return file_name


    def getAttachments(self, submission):

        list_of_dicts = []

        for attachment in submission.attachments:

            att_file_type = Path(attachment.filename).suffix.lower()[1:]

            if att_file_type not in ["png", "pdf", "jpg"]: # this are the unrated file types
                if ( att_file_type != file_type.lower() ):  # does the filename extentsion mach the required one?
                    print(f"Skipping {attachment.filename}")
                    continue

                if ( file_name_match != None and file_name_match not in attachment.filename ):  # when defined, check if the filename is correct.
                    continue

            response = requests.get(attachment.url, allow_redirects=True)
            if response.status_code != 200:
                print(f"Failed to download file: {attachment['url']}")
                continue

            rating = None
            file_name = None

            if att_file_type in ["png", "pdf", "jpg"]:  # no word matching, no auto rating
                file_name = ( str(submission.id) + "-" + str(attachment.id) + "." + att_file_type )
                file_name = self.loadPicture( attachment.url, file_name )  # return file name with path

                file_content = ( "fn:" + file_name )  # file content refers to a filename fn: <filename> which is the file name to the picture downloaded
                feedback = self.getFeedback(True)
                words_correct = -99
                rating = ( assignment.points_possible )  # png is not rated automattically, propose higest score.

            else:  # anything but a png file, do the word matching
                file_name = None
                file_content = response.content.decode()
                # words_correct, position = validateWords(words_in_order, file_content) #validate text(file_conten) with words (words must appear in text in order and !words may not exists in text)
                validation = TextValidation(file_content, words_in_order)
                words_correct = validation.wordsMatched
                match = validation.match

                # if (position > 1): # position of last found word and will be -1 when a word is not found.
                if match:
                    rating = assignment.points_possible
                    feedback = self.getFeedback(True)
                else:
                    rating = 0
                    feedback = self.getFeedback(False)

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
                }
            )

            #  We could have more ratings and more feedback at this point.

        return list_of_dicts


    def getFeedback(self, positief):
        # ToDo check if config exists and if it is a list.
        if positief:
            selected_feedback = random.choice(config["default_feedback_pos"])
        else:
            selected_feedback = random.choice(config["default_feedback_neg"])

        return selected_feedback


    def listUnratedAssignments(self, item, TEST=False):
        #  all properties in item are delivered by the API from CMON, we will find allunrated items from the assignment specified in item (json)
        course_id = item["course_id"]
        assignment_id = item["assignment_id"]
        words_in_order = item["words_in_order"]
        file_type = item["file_type"]
        file_name_match = item["file_name"]
        attachments = item["attachments"]

        list_of_dicts = []

        try:
            course = self.canvas.get_course(course_id)
            assignment = course.get_assignment(assignment_id)
        except:
            print(f"No access to course {course_id} and/or assignment {assignment_id}")
            return "No API access to course {course_id} and/or assignment {assignment_id}"

        # Get all submissions
        submissions = assignment.get_submissions(include=["user", "submission_comments"])

        # removeTempFiles() # ToDo remove files when rating is done!?

        print(f"Checking course {course_id} assignment {assignment_id}")

        for i, submission in enumerate(submissions):
            if TEST:
                user = submission.user["name"]
                print(f"Checking {user} {submission.submitted_at} - {submission.workflow_state}")

            if submission.submitted_at is None: #  no submission present, continue
                continue
            if not TEST and submission.workflow_state == "graded": #  if graded (and not in testmode), continue
                continue
            if TEST and i > 6: #  if we are testing we could have too many (graded) submissions so stop (break) after 6
                break

            comments = "" # get all comments
            for comment in reversed(submission.submission_comments):
                this_date = getDayMonth(comment["created_at"])
                this_initials = getInitials(comment["author_name"])
                comments += (
                    f'<i>{this_date} {this_initials}</i>: {comment["comment"]}<br><br>'
                )

            comments = self.getComments(submission)
            json_attachments = self.getAttachments(submission)

            max_points = assignment.points_possible
            if submission.attempt > 3:
                rating = int(int(rating) * 0.8)
                max_points = int(int(max_points) * 0.8)

            json_result=(
                {
                    "assignment_id": assignment_id,
                    "assignment_name": assignment.name,
                    "course_id": course.id,
                    "course_name": course.name,
                    "submission_id": submission.id,
                    "attempt": submission.attempt,
                    "points_possible": int(assignment.points_possible),
                    "max_points": max_points,
                    "alt_feedback": getFeedback(True),
                    "user": submission.user["name"],
                    "user_id": submission.user["id"],
                    "number_of_words": len(words_in_order),
                    "hint": item.get("hint", ""),
                    "comments": comments,
                    "test": TEST,
                    "attachements": json_attachments
                }
            )