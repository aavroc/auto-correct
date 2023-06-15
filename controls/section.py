from canvasapi import Canvas
from flask import Blueprint, render_template, redirect, url_for
import os
import json
from myflaskapp.mydata import data
from myflaskapp.config import config
import sys
import requests

# Canvas API URL
API_URL = config['API_URL']
# Canvas API key
API_KEY = config['API_KEY']
# not needed? default_feedback = config['default_feedback']

data_cache='data_cache.json'

# Create a blueprint named 'blog'
section = Blueprint('section', __name__, static_folder='static', template_folder='templates\section')

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

def readCanvas(module_id):
    url = 'http://c21.cmon.ovh/api/nakijken?mid='+module_id
    print(f"url: {url}")
    response = requests.get(url)  # Replace with your actual URL

    # Ensure we have a valid response
    if response.status_code == 200:
        json_data = response.json()
    else:
        print(f"Error: {response.status_code}")

    with open(data_cache, 'w') as f:
        f.write(str(json_data))

    return json_data

def listAssignments(module_id):
    # Create a list of available assignments that can be auto graded

    return readCanvas(module_id)

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
        # submissions = assignment.get_submissions()

        list_of_dicts.append({'course_id':course_id, 'course_name':course.name,'assignment_id':assignment_id,'assignment_name':assignment.name, 'points_possible':assignment.points_possible,})

    return(list_of_dicts)

# Define a route related to this blueprint
@section.route('/section/')
def section_list():
    filename = data_cache

    if os.path.isfile(filename):  # check if file/cache exists
        with open(filename, 'r') as f: 
            data = json.load(f) 
    else:
        data = listAssignments()  # generate data
        with open(filename, 'w') as f: 
            data = json.dump(data, f) 
    if (data):
        return render_template('section/section.html', data=data)
    else:
        return render_template('section/results.html', data='Done')

@section.route('/section/refresh/<module_id>')
def section_refresh(module_id):
    
    data = listAssignments(module_id)

    filename = data_cache
    print(f"fn: {filename} ")

    if os.path.isfile(filename): os.remove(filename)

    with open(filename, 'w') as f:  # open file in write mode
        json.dump(data, f)  # write data to file in JSON format

    # return('Done')
    return redirect(url_for('section.section_list'))