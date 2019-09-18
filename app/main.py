from flask import Blueprint, render_template, send_from_directory
from flask_login import login_required, current_user
from . import db, scheduler

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@main.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

@main.route('/profile')
#@login_required
def profile():
    return render_template('profile.html')