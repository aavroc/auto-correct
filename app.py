# app.py
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from canvasapi import Canvas
import sys, os, json, glob, random, requests

from myflaskapp.myForms import ValidationForm
from myflaskapp.config import config
from myflaskapp.validation import TextValidation
from datetime import datetime

app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.config["SECRET_KEY"] = "083rhejwfdnslag9348uerfdijkcs398qCD"

# Canvas API URL
API_URL = config["API_URL"]
# Canvas API key
API_KEY = config["API_KEY"]

file_path_form_data = (
    "static/temp/formdata.json"  # Global variable for the cached form data
)

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


def _removeTempFiles():
    path = "static/temp/*"
    files = glob.glob(path)
    for f in files:
        os.remove(f)


def loadPicture(url, picture_file_name):
    path = "static/temp/"  # save file to temp directory, ToDo when and how to clean temp dir?

    if not os.path.exists(path):
        os.makedirs(path)

    file_name = path + picture_file_name

    if not os.path.isfile(file_name):
        page = requests.get(url)
        with open(file_name, "wb") as f:
            f.write(page.content)

    return file_name


def _validateWords(words, text):
    pos = 0
    negative_search = -1
    words_correct = 0

    for word in words:
        if word and word[0] == "!":
            negative_search = text.lower().find(word[1:].lower(), pos)
        else:
            pos = text.lower().find(word.lower(), pos)

        if pos == -1 or negative_search != -1:
            # Word not found, stop searching
            break
        else:
            words_correct += 1

    return words_correct, pos


def saveFormData(data):
    if os.path.isfile(file_path_form_data):
        # Rename the existing file with a sequence number
        sequence_number = 1
        name, extension = os.path.splitext(file_path_form_data)
        while True:
            new_file_path = f"{name}-{sequence_number}{extension}"
            if not os.path.isfile(new_file_path):
                os.rename(file_path_form_data, new_file_path)
                break
            sequence_number += 1

    with open(file_path_form_data, "w") as file:
        json.dump(data, file)


def loadFormData(file_name=""):
    if file_name == "":
        file_name = file_path_form_data
    else:
        directory = os.path.dirname(file_path_form_data)
        file_name = os.path.join(directory, file_name)

    if not os.path.isfile(file_name):  # Check if file exists
        return False
    with open(file_name, "r") as file:
        data = json.load(file)
    return data


def getFormdataFiles():
    directory = os.path.dirname(
        file_path_form_data
    )  # Replace with the actual directory path

    # Get all files in the directory
    files = os.listdir(directory)

    # Filter JSON files with names starting with 'formdata'
    formdata_files = [
        f
        for f in files
        if f.lower().startswith("formdata") and f.lower().endswith(".json")
    ]

    # Get file creation dates
    file_data = []
    for file in formdata_files:
        file_path = os.path.join(directory, file)
        creation_date = os.path.getctime(file_path)
        file_data.append({"name": file, "creation_date": creation_date})

    # Sort files by creation date
    file_data.sort(key=lambda x: x["creation_date"])

    return file_data


def getFeedback():
    # ToDo check if config exists and if it is a list.
    selected_feedback = random.choice(config["default_feedback"])

    return selected_feedback

def getDayMonth(date_string):
    date_object = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")

    month = date_object.strftime("%m")  # Full month name
    day = date_object.strftime("%d")  # Zero-padded day

    return day+'-'+month

def getInitials(name):
    name=name.split()
    return name[0][:1].upper()+name[1][:1].upper()


def listUnratedAssignments(item):
    course_id = item["course_id"]
    assignment_id = item["assignment_id"]
    words_in_order = item["words_in_order"]
    file_type = item["file_type"]
    file_name_match = item["file_name"]

    list_of_dicts = []

    try:
        course = canvas.get_course(course_id)
        assignment = course.get_assignment(assignment_id)
    except:
        print(f"No access to course {course_id} and/or assignment {assignment_id}")
        return render_template(
            "results.html",
            data="No API access to course {course_id} and/or assignment {assignment_id}",
        )

    # Get all submissions
    submissions = assignment.get_submissions(include=["user", "submission_comments"])

    # removeTempFiles() # ToDo remove files when rating is done!?

    print(f"Checking course {course_id} assignment {assignment_id}")

    # Process each submission
    for i, submission in enumerate(submissions):
        # Check if the submission is already graded
        user=submission.user["name"]
        print(f"Checking {user} {submission.submitted_at} - {submission.workflow_state}")
        comments=""
        for comment in reversed(submission.submission_comments):
            this_date=getDayMonth(comment['created_at'])
            this_initials=getInitials(comment['author_name'])
            comments += f'<i>{this_date} {this_initials}</i>: {comment["comment"]}<br>'
            print(f"Comment {this_date} {this_initials} {comment['comment']}")

        if submission.submitted_at is None or submission.workflow_state == "graded":
            continue

        att_nr = 0
        for attachment in submission.attachments:
            att_file_type = Path(attachment.filename).suffix.lower()[1:]

            if (att_file_type not in ["png", "pdf", "jpg"] ):

                if ( att_file_type != file_type.lower() ):  # does the filename extentsion mach the required one?
                    print(f"Skipping {attachment.filename}")
                    continue

                if ( file_name_match != None and file_name_match not in attachment.filename ):  # when defined, check if the filename is correct.
                    continue

            response = requests.get(attachment.url, allow_redirects=True)
            if response.status_code != 200:
                print(f"Failed to download file: {attachment['url']}")
                continue

            if att_file_type in ["png", "pdf", "jpg"]:  # png, no word matching
                sort_order = 9
                att_nr += 1
                file_name = str(course_id) + "-" + str(attachment.id) + "." + att_file_type
                file_name = loadPicture( attachment.url, file_name )  # return file name with path

                file_content = (
                    "fn:" + file_name
                )  # file content refers to a filename fn: <filename> which is the file name to the picture downloaded
                feedback = getFeedback()
                words_correct = -99
                rating = (
                    assignment.points_possible
                )  # png is not rated automattically, propose higest score.

            else:  # anything but a png file, do the word matching
                sort_order = 1
                att_nr += 1
                file_content = response.content.decode()
                # words_correct, position = validateWords(words_in_order, file_content) #validate text(file_conten) with words (words must appear in text in order and !words may not exists in text)
                validation = TextValidation(file_content, words_in_order)
                words_correct = validation.wordsMatched
                match = validation.match

                # if (position > 1): # position of last found word and will be -1 when a word is not found.
                if match:
                    rating = assignment.points_possible
                    feedback = getFeedback()
                else:
                    rating = 0
                    feedback = "Niet helemaal goed"

            # When more than 3 attempts max score is 80% of points_possible (max score)

            if submission.attempt > 3:
                rating = int(int(rating) * 0.8)

            list_of_dicts.append(
                {
                    "sort_order": sort_order,
                    "assignment_id": assignment_id,
                    "assignment_name": assignment.name,
                    "course_id": course.id,
                    "course_name": course.name,
                    "submission_id": submission.id,
                    "attempt": submission.attempt,
                    "rating": rating,
                    "points_possible": assignment.points_possible,
                    "feedback": feedback,
                    "user": submission.user["name"],
                    "file_content": file_content,
                    "file_name": attachment.filename,
                    "file_type": att_file_type,
                    "words_in_order": words_in_order,
                    "words_correct": words_correct,
                    "number_of_words": len(words_in_order),
                    "hint": item.get("hint", ""),
                    "att_nr": att_nr,
                    "number_of_att": len(submission.attachments),
                    "comments": comments
                }
            )

    # pictures need to be placed after auto-graded text
    # in the view the picuteres will be 'inserted' using JS
    list_of_dicts = sorted(list_of_dicts, key=lambda x: (x["user"], x["sort_order"]))

    # Becasue of the sorting the att_nr can be in the wrong sequence and in the template we need to know if we are looking
    # at the first attachment or a asubsequent one. Becasue onoy the first is placed and all subsequent ones are inserted by JS
    prev_submission_id = -1
    for item in list_of_dicts:
        if item["submission_id"] != prev_submission_id:
            counter = 1
        else:
            counter += 1
        item["att_nr"] = counter
        prev_submission_id = item["submission_id"]

    saveFormData(list_of_dicts)  # save cache (mainly for developing)

    return list_of_dicts


def update_grade_and_feedback(posted_variables):
    output = ""
    rating_values = request.form.getlist("rating[]")
    feedback_values = request.form.getlist("feedback[]")
    checked_values = request.form.getlist("checked[]")
    submission_id_values = request.form.getlist("submission_id[]")
    assignment_id_values = request.form.getlist("assignment_id[]")
    course_id_values = request.form.getlist("course_id[]")
    check_values = request.form.getlist("checked[]")

    # We have 6 lists with all the saem length. All lists will have the same course_id and assignment_id

    try:
        course = canvas.get_course(course_id_values[0])
        assignment = course.get_assignment(assignment_id_values[0])
    except:
        return f"No access to course {course_id} and/or assignment {assignment_id}"

    # Get the submission
    submissions = assignment.get_submissions(include=["user"])

    count = 0

    for submission in submissions:
        for i, submission_id in enumerate(submission_id_values):
            # output+=(f"Evaluating {submission.id} and {submission_id}\n")
            if int(submission.id) == int(submission_id) and int(check_values[i]) == 1:
                count += 1
                output += f"\nRating {submission_id} for {submission.user['name']} with rate {rating_values[i]} and feedback {feedback_values[i]}\n"
                # next two lines do the actual rating and feedback submision
                submission.edit(submission={"posted_grade": str(rating_values[i])})
                submission.edit(comment={"text_comment": feedback_values[i]})

    output += f"\n\nRated {count} assignments succesfully."
    return output


@app.route("/")
def index():
    results = loadFormData()
    if results:
        return render_template("rate.html", data=results, alreadySubmitted=1)

    return render_template("results.html", data="No Data in form cache")


@app.route("/<file_name>")
def indexParameter(file_name):
    results = loadFormData(file_name)
    if results:
        return render_template("rate.html", data=results)

    return render_template("results.html", data="File empty or deleted")


@app.route("/correcta/<cohort>/<assignment_id>")
def correcta(cohort, assignment_id):
    # read API data
    url = "http://" + cohort + ".cmon.ovh/api/nakijken?aid=" + assignment_id
    print(f"url: {url}")
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
    else:
        print(f"Error: {response.status_code}")
        return f"Error: {response.status_code}"

    # print("Data-len: "+str(len(data)))
    # print (data)

    if not data:
        return render_template("results.html", data="No Data from Canvas API")

    for item in data:
        if int(assignment_id) == int(item["assignment_id"]):
            results = listUnratedAssignments(item)
            # print(results)
            return render_template(
                "rate.html", data=results, alreadySubmitted=0
            )  # stop after first hit

    return


@app.route("/submit-ratings", methods=["POST"])
def submit_ratings():
    results = update_grade_and_feedback(request.form)
    return render_template("results.html", data=results)


@app.route("/list")
def list():
    data = getFormdataFiles()
    print(f"Data: {data}")
    return render_template("list.html", data=data)


@app.route("/validationtest", methods=["GET", "POST"])
def validationtest():
    form = ValidationForm()
    if form.validate_on_submit():
        # set words in array
        form_words = form.words.data.split()
        form_text = form.text.data
        # print(form_text, '-', form_words)
        validation = TextValidation(form_text, form_words)
        # print(f"Matched: {validation.wordsMatched}")
        return render_template(
            "validation.html",
            form=form,
            match=validation.match,
            wordsMatched=validation.wordsMatched,
            words=form.words.data.split(),
        )

    return render_template(
        "validation.html", form=form, match="-", wordsMatched="-", words=""
    )


if __name__ == "__main__":
    app.run(debug=True)
