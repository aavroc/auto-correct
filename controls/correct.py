from canvasapi import Canvas
from flask import Blueprint, render_template, redirect, url_for
import os
import json
from myflaskapp.mydata import data
from myflaskapp.config import config
import sys

# Canvas API URL
API_URL = config['API_URL']
# Canvas API key
API_KEY = config['API_KEY']
default_feedback = config['default_feedback']

# Create a blueprint named 'blog'
section = Blueprint('correct', __name__, static_folder='static', template_folder='templates\correct')