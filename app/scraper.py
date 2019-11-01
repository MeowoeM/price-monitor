from bs4 import BeautifulSoup
import urllib3
from datetime import datetime

from . import db
from .model import Task, Price

def scrape(task_id):
    task = Task.query.filter_by(id=task_id).first()

    http = urllib3.PoolManager()
    response = http.request('GET', task.url)
    soup = BeautifulSoup(response.data, "lxml")

    mode, operation = task.operation.split(':')
    # TODO: create default modes

    for option in operation.split(','):
        tag, attribute, value = option.split('/')
        result = soup.find(tag, {attribute: value})
        if result: break

    if result:
        task.prices.append(
            Price(
                time=datetime.now(), 
                price=float(result.contents[0].replace('￥', '').replace(',', ''))
            )
        )
        db.session.commit()