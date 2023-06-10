# app.py
from flask import Flask, render_template, request
from canvasapi import Canvas
import requests
import sys

app = Flask(__name__)

# Canvas API URL
API_URL = "https://talnet.instructure.com"
# Canvas API key
API_KEY = "17601~V6FUc7Xvc07XkCMxJtDVJlpN7RiugCbaodIJ6pUzfnxTZ7S44eRs7yGW7jKc0hOO"

feedback = 'Top gedaan!'

data = [
    {"course_id": 6585, "assignment_id": 117166, "rating":10, "words_in_order": ["localhost", "games", "root","localhost", "artiesten", "roc-student", "welkom123", "$conn2" ], 'feedback':feedback},
    {"course_id": 6585, "assignment_id": 117167, "rating":10, "words_in_order": ["aappp","php", "localhost", "insert", "into", "producten", "values", "Playstation "], 'feedback':feedback},
]



# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

def rateSubmission(submission, rating, feedback, test=1):
    if (test):
        print(f"Testing (no execution), rating {rating} with feedback {feedback}")
    else:
        print("Here we go...")
        #submission.edit(submission={'posted_grade': rating})
        #submission.edit(comment= {'text_comment': feedback}))

def listAssignments():

    list_of_dicts=[]
    for item in data:
        course_id=item['course_id']
        assignment_id=item['assignment_id']

        try:
            course = canvas.get_course(course_id)
            assignment = course.get_assignment(assignment_id)
        except:
            print(f"No access to course {course_id} and/or assignment {assignment_id}")

        # Get all submissions
        submissions = assignment.get_submissions()

        list_of_dicts.append({'course_id':course_id, 'course_name':course.name,'assignment_id':assignment_id,'assignment_name':assignment.name})

    return(list_of_dicts)

def listUnratedAssignments(item):
    course_id=item['course_id']
    assignment_id=item['assignment_id']
    rating=item['rating']
    words_in_order=item['words_in_order']

    list_of_dicts=[]

    try:
        course = canvas.get_course(course_id)
        assignment = course.get_assignment(assignment_id)
    except:
        print(f"No access to course {course_id} and/or assignment {assignment_id}")

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
            words_correct = 0
            for word in words_in_order:
                pos = file_content.find(word, pos)
                if pos == -1:
                    # Word not found, stop searching
                    break
                else:
                    words_correct+=1

            if (pos > 1):
                rating=item['rating']
                feedback=item['feedback']
            else:
                rating=0
                feedback='Niet helemaal goed'

            list_of_dicts.append({'assignment_id':assignment_id,'assignment_name':assignment.name,
            'course_name':course.name,'submission':submission.id,
            'rating':rating, 'feedback':feedback,'user':submission.user['name'], 'file_content':file_content,
            'words_in_order':words_in_order,'words_correct':words_correct})

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

@app.route('/')
def index():
    results=listAssignments()
    return render_template('index.html', data=results)

@app.route('/correct/<assignment_id>')
def correct(assignment_id):
    for item in data:
        if ( int(assignment_id)==int(item['assignment_id']) ):
            results=listUnratedAssignments(item)
    #return(results)
    return render_template('rate.html', data=results)

@app.route('/submit-ratings', methods=['POST'])
def submit_ratings():
    # Get all the posted variables from the form
    posted_variables = request.form

    rating_values = request.form.getlist('rating[]')
    feedback_values = request.form.getlist('feedback[]')
    checked_values = request.form.getlist('checked[]')
    submission_id_values = request.form.getlist('submission_id[]')
    assignment_id_values = request.form.getlist('assignment_id[]')

    print(submission_id_values)

    # Print the posted variables
    for key, value in posted_variables.items():
        print(f'{key}: {value}')

    # Return a response to the client
    return 'Form submission successful'

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(debug=True)
