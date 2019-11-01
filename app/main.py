from flask import Blueprint, render_template, send_from_directory, request, url_for, redirect, flash
from flask_login import login_required, current_user
from . import db, scheduler, login
from .model import Task, User, Price, Subscribe
from .scraper import scrape

from datetime import datetime, timedelta
import plotly
import plotly.graph_objs as go

import pandas as pd
import numpy as np
import json

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
@login_required
def profile():
    # task info to be listed on the profile page
    task_info = []

    user = User.query.filter_by(id=current_user.id).first()
    for subscribe in user.subscribes:
        task_info.append(
            {
                'task_id': subscribe.task_id, 
                'name': subscribe.task.name, 
                'image_url': subscribe.task.image_url
            }
        )

    return render_template('profile.html', task_info=task_info)

@main.route('/task/<int:task_id>')
def display_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    
    data = db.session.query(Price.time, Price.price).filter(Price.tasks.any(id=task_id)).all()
    # print(data)
    if data:
        data = list(map(list, zip(*data)))
    else:
        data = [[0], [0]]
    df = pd.DataFrame({'time': data[0], 'price': data[1]})

    graph = dict(
        data=[
            dict(
                x=df['time'],
                y=df['price'],
                type='scatter'
            )
        ],
        layout=dict(
            xaxis_rangeslider_visible=True
        )
    )

    plot = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)
    
    return render_template(
        'display_task.html', 
        name=task.name, plot=plot, task_id=task_id,
        created_time=task.created_time,
        expiring_time=task.expiring_time,
        url=task.url, description=task.description,
        image_url=task.image_url
    )

@main.route('/tasks/<string:tasks_str>')
def display_tasks(tasks_str):
    tasks_id = list(map(int, tasks_str.split('|')))

    data = []
    task_info = []
    for task_id in tasks_id:
        task = Task.query.filter_by(id=task_id).first()

        task_info.append(
            {
                'task_id': task.id, 
                'name': task.name, 
                'image_url': task.image_url
            }
        )
    
        data = db.session.query(Price.time, Price.price).filter(Price.tasks.any(id=task_id)).all()
        if data:
            data = list(map(list, zip(*data)))
        else:
            data = [[0], [0]]
        df = pd.DataFrame({'time': data[0], 'price': data[1]})

        data.append(
            dict(
                x=df['time'],
                y=df['price'],
                type='scatter',
                name=task.name
            )
        )

    graph = dict(
        data=data,
        layout=dict(
            xaxis_rangeslider_visible=True
        )
    )

    plot = json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        'display_tasks.html', plot=plot, task_info=task_info
    )

@main.route('/add_task')
@login_required
def add_task():
    return render_template('add_task.html')

@main.route('/add_task', methods=['POST'])
@login_required
def add_task_post():
    url = request.form.get('url')
    operation = request.form.get('operation')
    name = request.form.get('name')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    interval = 60

    task = Task.query.filter_by(url=url, operation=operation).first()
    if not task:
        task = Task(
            name=name,
            url=url,
            operation=operation,
            description=description,
            image_url=image_url,
            interval=interval,
            created_time=datetime.now(),
            expiring_time=datetime.now() + timedelta(days=365)
        )

        db.session.add(task)
        db.session.commit()
        db.session.refresh(task)
        flash('Task added.')
    
    # task already exists and the user has already subscribed it
    elif Subscribe.query.filter_by(user_id=current_user.id, task_id=task.id).first():
        flash('Task already exists.')
        return redirect(url_for('main.profile'))
    # task already exists but the user hasn't subscribed it
    else:
        task.expiring_time = datetime.now() + timedelta(days=365)
        flash('Task added.')

    user = User.query.filter_by(id=current_user.id).first()
    user.subscribe(task)
    db.session.commit()

    # initiate task schedule
    scheduler.add_job(
        func=scrape, trigger='interval',
        minutes=interval, id=url, args=[task.id], 
        name=name, replace_existing=True,
        misfire_grace_time=2*60,
        start_date=datetime.now() + timedelta(seconds=2)
        )
    
    return redirect(url_for('main.profile'))

@main.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task_post(task_id):
    subscribe = Subscribe.query.filter_by(user_id=current_user.id, task_id=task_id).first()
    if subscribe:
        db.session.delete(subscribe)
        db.session.commit()
        flash('Task deleted.')
        return redirect(url_for('main.profile'))
    
    flash('No such task.')
    return redirect(url_for('main.profile'))