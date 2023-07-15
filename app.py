# app.py
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from canvasapi import Canvas
import os, json, glob, requests

from myflaskapp.myForms import ValidationForm
from myflaskapp.config import config
from myflaskapp.validation import TextValidation

from myflaskapp.getAssignments import getAssignmentInfo
import time

app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.loopcontrols")
app.config["SECRET_KEY"] = "083rhejwfdnslag9348uerfdijkcs398qCD"

# Canvas API URL
API_URL = config["API_URL"]
# Canvas API key
API_KEY = config["API_KEY"]

FILE_FORM_DATA = "static/temp/json/formdata.json"  # Global variable for the cached form data

TEST = config.get("TEST")
print(f"testing: {TEST}")


# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)


def saveFormData(data):
    if os.path.isfile(FILE_FORM_DATA):
        # Rename the existing file with a sequence number
        sequence_number = 1
        name, extension = os.path.splitext(FILE_FORM_DATA)
        while True:
            new_file_path = f"{name}-{sequence_number}{extension}"
            if not os.path.isfile(new_file_path):
                os.rename(FILE_FORM_DATA, new_file_path)
                break
            sequence_number += 1

    with open(FILE_FORM_DATA, "w") as file:
        json.dump(data, file)


def loadFormData(file_name=""):
    if file_name == "":
        file_name = FILE_FORM_DATA
    else:
        directory = os.path.dirname(FILE_FORM_DATA)
        file_name = os.path.join(directory, file_name)

    if not os.path.isfile(file_name):  # Check if file exists
        return False
    with open(file_name, "r") as file:
        print(f"file: {file}")
        data = json.load(file)
    return data


def getFormdataFiles():
    directory = os.path.dirname(
        FILE_FORM_DATA
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
    file_data.sort(key=lambda x: x["creation_date"], reverse=True)
    return file_data


@app.route("/") #  load latest JSON from cache and show rating screen.
def index():
    results = loadFormData()
    if results:
        return render_template("rate.html", data=results, defaults=config['defaults'], alreadySubmitted=1, test=TEST )

    return render_template("results.html", data="No Data in form cache")


@app.route("/<file_name>") #  load JSON from cache and show rating screen.
def indexParameter(file_name):
    results = loadFormData(file_name)
    if results:
        return render_template("rate.html",  data=results, defaults=config['defaults'], alreadySubmitted=1 )

    return render_template("results.html", data="File empty or deleted")


@app.route("/correcta/<cohort>/<assignment_id>") #  show all ratings
def correcta(cohort, assignment_id):
    start = time.time()
    result = getAssignmentInfo(canvas, cohort, assignment_id, TEST)
    
    if ( result.json_data == [] ):
        return "No auto-corect data in CMON for this assignemnt"

    saveFormData(result.rating_data)

    end = time.time()
    elapsed_time_ms = (end - start) * 1000  # Convert seconds to milliseconds
    print(f"Total time elapsed: {elapsed_time_ms} ms")

    return render_template("rate.html", data=result.rating_data, defaults=config['defaults'], alreadySubmitted=0, test=TEST, time_elapsed=elapsed_time_ms, warnings=result.warnings )


@app.route("/submit-ratings", methods=["POST"]) #  perform the actual rating
def submit_ratings():
    results = update_grade_and_feedback(request.form)
    return render_template("results.html", data=results)


@app.route("/json") #  show latest JSON (for debug)
def showJson():
    results = loadFormData()
    return results


@app.route("/list") #  show debug screen with history and with link to test auto-rating
def list():
    data = getFormdataFiles()
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
