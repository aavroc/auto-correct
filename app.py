# app.py
from flask import Flask, render_template, request, redirect, url_for
from canvasapi import Canvas
import requests
import sys
from pathlib import Path
import os
import json
import glob

from myflaskapp.mydata import data
from myflaskapp.config import config

from controls.section import section
#from controls.correct import correct

app = Flask(__name__)

# Canvas API URL
API_URL = config['API_URL']
# Canvas API key
API_KEY = config['API_KEY']
default_feedback = config['default_feedback']

app.register_blueprint(section, url_prefix="")
#app.register_blueprint(correct, url_prefix="")

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

def removeTempFiles():
    path='static/temp/*'
    files = glob.glob(path)
    for f in files:
        os.remove(f)

def rateSubmission(submission, rating, feedback, test=1):
    if (test):
        print(f"Testing (no execution), rating {rating} with feedback {feedback}")
    else:
        print("Here we go...")
        #submission.edit(submission={'posted_grade': rating})
        #submission.edit(comment= {'text_comment': feedback}))

def listUnratedAssignments(item):
    course_id=item['course_id']
    assignment_id=item['assignment_id']
    rating=item.get('rating','0') # changed, getting from assignemtn (points_possible)
    words_in_order=item['words_in_order']
    file_type=item['file_type']
    file_name=item.get('file_name', "")

    list_of_dicts=[]

    try:
        course = canvas.get_course(course_id)
        assignment = course.get_assignment(assignment_id)
    except:
        print(f"No access to course {course_id} and/or assignment {assignment_id}")

    # Get all submissions
    submissions = assignment.get_submissions(include=['user'])

    # removeTempFiles() # ToDo remove files when rating is done!

    # Process each submission
    for i, submission in enumerate(submissions):
        # Check if the submission is already graded
        if submission.submitted_at is None or submission.workflow_state == 'graded':
            continue
        
        for attachment in submission.attachments:
            if Path(attachment.filename).suffix != '.'+file_type: # does the filename extentsion mach the required one?
                continue

            if ( file_name != '' and file_name not in attachment.filename ): # when defined, check if the filename is correct.
                continue
            response = requests.get(attachment.url, allow_redirects=True)
            if response.status_code != 200:
                print(f"Failed to download file: {attachment['url']}")
                continue
            
            if ( file_type == 'png' ):
                #save file
                path='static/temp'
                
                if not os.path.exists(path):
                    os.makedirs(path)
                # png_filename = attachment.filename
                png_filename = str(course_id)+'-'+str(assignment_id)+'-'+str(submission.id)+'-'+str(attachment.id)+'.png'
                png_filename = str(course_id)+'-'+str(attachment.id)+'.png'
                fn = os.path.join(path,png_filename)

                if not os.path.isfile(fn):
                    page = requests.get(attachment.url)
                    with open(fn, 'wb') as f:
                        f.write(page.content)

                file_content = 'fn:'+fn
                rating=item.get('rating','')
                feedback=item.get('feedback',default_feedback)
                words_correct=-99
            else:
                file_content = response.content.decode()

                pos = 0
                words_correct = 0
                for word in words_in_order:
                    pos = file_content.lower().find(word.lower(), pos)
                    if pos == -1:
                        # Word not found, stop searching
                        break
                    else:
                        words_correct+=1

                if (pos > 1):
                    rating=item.get('rating','0')
                    feedback=item.get('feedback',default_feedback)
                else:
                    rating=0
                    feedback='Niet helemaal goed'

            list_of_dicts.append({'assignment_id':assignment_id,'assignment_name':assignment.name,
            'course_id':course.id,'course_name':course.name,'submission_id':submission.id,
            'rating':assignment.points_possible, 'feedback':feedback,'user':submission.user['name'], 'file_content':file_content,
            'words_in_order':words_in_order,'words_correct':words_correct,'hint':item.get('hint',''),'number_of_att':len(submission.attachments)})

    return(list_of_dicts)

def autoGrade(course_id, assignment_id, rating, search_words):
    try:
        course = canvas.get_course(course_id)
        assignment = course.get_assignment(assignment_id)
    except:
        print(f"No access to course {course_id} and/or assignment {assignment_id}")

    global feedback

    print("")
    print(f"Autograde {course.name} {assignment.name}")

    # Get all submissions
    submissions = assignment.get_submissions(include=['user'])

    # Process each submission
    for submission in submissions:
        # Check if the submission is already graded
        if submission.submitted_at is None or submission.workflow_state == 'graded':
            continue

        for attachment in submission.attachments:
            response = requests.get(attachment.url, allow_redirects=True)
            if response.status_code != 200:
                print(f"Failed to download file: {attachment['url']}")
                continue

            file_content = response.content.decode()

            pos = 0
            for word in search_words:
                pos = file_content.find(word, pos)
                if pos == -1:
                    # Word not found, stop searching
                    break
                else:
                    print(f"{word} - ", end="")

            if (pos > 1):
                print(f"OK {pos}")
                print(f"Submission checked and correct, grading student: {submission.user['name']} (ID: {submission.user_id})")
                rateSubmission(submission, rating, feedback)
            else:
                print(f"Not OK {pos}")
                print(f"Submission incorrect, not grading student: {submission.user['name']} (ID: {submission.user_id})")

def update_grade_and_feedback(posted_variables):
    output=''
    rating_values = request.form.getlist('rating[]')
    feedback_values = request.form.getlist('feedback[]')
    checked_values = request.form.getlist('checked[]')
    submission_id_values = request.form.getlist('submission_id[]')
    assignment_id_values = request.form.getlist('assignment_id[]')
    course_id_values = request.form.getlist('course_id[]')
    check_values = request.form.getlist('checked[]')

    # We have 6 lists with all the saem length. All lists will have the same course_id and assignment_id

    try:
        course = canvas.get_course(course_id_values[0])
        assignment = course.get_assignment(assignment_id_values[0])
    except:
        return(f"No access to course {course_id} and/or assignment {assignment_id}")

    # Get the submission
    submissions = assignment.get_submissions(include=['user'])

    count=0

    for submission in submissions:
        for i, submission_id in enumerate(submission_id_values):
            # output+=(f"Evaluating {submission.id} and {submission_id}\n")
            if ( int(submission.id) == int(submission_id) and int(check_values[i])==1 ):
                    count+=1
                    output+=(f"\nRating {submission_id} for {submission.user['name']} with rate {rating_values[i]} and feedback {feedback_values[i]}\n")
                    # next two lines do the actual rating and feedback submision
                    submission.edit(submission={'posted_grade': str(rating_values[i])})
                    submission.edit(comment={'text_comment': feedback_values[i]})

    output+=(f"\n\nRated {count} assignments succesfully.")
    return(output)


@app.route('/')
def index():
    return redirect(url_for('section.section_list'))

@app.route('/correct/<assignment_id>')
def correct(assignment_id):
    for item in data:
        if ( int(assignment_id)==int(item['assignment_id']) ):
            results=listUnratedAssignments(item)
    #return(results)
    return render_template('rate.html', data=results)

@app.route('/submit-ratings', methods=['POST'])
def submit_ratings():
    results=update_grade_and_feedback(request.form)
    return render_template('results.html', data=results)

@app.route('/test')
def test():
    return render_template('results.html', data='Empty data set')

if __name__ == "__main__":
    app.run(debug=True)
