# app.py
from flask import Flask, render_template, request
from canvasapi import Canvas
import requests
import sys
from pathlib import Path

app = Flask(__name__)

# Canvas API URL
API_URL = "https://talnet.instructure.com"
# Canvas API key
API_KEY = "17601~V6FUc7Xvc07XkCMxJtDVJlpN7RiugCbaodIJ6pUzfnxTZ7S44eRs7yGW7jKc0hOO"

feedback = 'Top gedaan!'

data = [
    {"course_id": 6585, "assignment_id": 117166, "rating":10, 'file_type':'php', "words_in_order": ["localhost", "games", "root","localhost", "artiesten", "roc-student", "welkom123", "$conn2" ], 'feedback':feedback},
    {"course_id": 6585, "assignment_id": 117167, "rating":10, 'file_type':'php', "words_in_order": ["php", "localhost", "insert", "into", "producten", "values", "Playstation "], 'feedback':feedback},
    {"course_id": 10780, "assignment_id": 136418, "rating":10, 'file_type':'js', "words_in_order": ["changeColor()","red", "getNumbers()", "this.state","addStar()", "render()", "onClick"], 'feedback':feedback},
    {"course_id": 7760, "assignment_id": 131584, "rating":10, 'file_type':'php', "words_in_order": ["php", "countries", "country","number_format", "country->SurfaceArea", "2"], 'feedback':feedback},
    {"course_id": 6585, "assignment_id": 117603, "rating":10, 'file_name':'verwijder' ,'file_type':'php', "words_in_order": ["php", "database", "delete","from", "klanten", "where","query"], 'feedback':feedback},
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
    # Create a list of available assignments that can be auto graded
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

    # Process each submission
    for submission in submissions:
        # Check if the submission is already graded
        if submission.submitted_at is None or submission.workflow_state == 'graded':
            continue
        
        for attachment in submission.attachments:
            if Path(attachment.filename).suffix != '.'+file_type: # does the filename extentsion mach the required one?
                continue
            print(f"FN: {file_name} == {attachment.filename}\n")
            if ( file_name != '' and file_name not in attachment.filename ): # when defined, check if the filename is correct.
                continue
            response = requests.get(attachment.url, allow_redirects=True)
            if response.status_code != 200:
                print(f"Failed to download file: {attachment['url']}")
                continue

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
                rating=item['rating']
                feedback=item['feedback']
            else:
                rating=0
                feedback='Niet helemaal goed'

            list_of_dicts.append({'assignment_id':assignment_id,'assignment_name':assignment.name,
            'course_id':course.id,'course_name':course.name,'submission_id':submission.id,
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


def update_grade_and_feedback(posted_variables):
    output='<pre>'
    rating_values = request.form.getlist('rating[]')
    feedback_values = request.form.getlist('feedback[]')
    checked_values = request.form.getlist('checked[]')
    submission_id_values = request.form.getlist('submission_id[]')
    assignment_id_values = request.form.getlist('assignment_id[]')
    course_id_values = request.form.getlist('course_id[]')
    check_values = request.form.getlist('checked[]')

    print(f"checked_values")

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
                    output+=(f"\nRating {submission_id} for {submission.user['name']} with rate {rating_values[i]} and feedback {feedback_values[i]}")
                    # next two lines do the actual rating and feedback submision
                    submission.edit(submission={'posted_grade': str(rating_values[i])})
                    submission.edit(comment={'text_comment': feedback_values[i]})

    output+=(f"\n\nRated {count} assignments succesfully.")
    output+="</pre>"
    return(output)


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
    result=update_grade_and_feedback(request.form)
    return(result)

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == "__main__":
    app.run(debug=True)
