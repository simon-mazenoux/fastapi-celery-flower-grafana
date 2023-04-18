import logging
from os import environ
from random import random
from time import sleep

from celery import Celery
from celery.exceptions import Retry, Reject

CELERY_BROKER_URL=environ['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND=environ['CELERY_RESULT_BACKEND']

celery = Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


@celery.task(bind=True, name='tasks.add')
def add(self, x: int, y: int):
    try:
        sleep(10)
        if random() <= 0.1:
            raise Exception("Unlucky")
        return x + y
    except Exception as e:
        self.retry(exc=e, countdown=1)
    

@celery.task(bind=True, name='tasks.divide', acts_late=True)
def divide(self, a: int, b: int):
    try:
        sleep(10)
        return a/b
    except ZeroDivisionError as e:
        raise Reject(e)
        # Doesn't work, check https://github.com/celery/celery/issues/4222
    except Exception as e:
        self.retry(exc=e)



@celery.task(name='tasks.task_a', bind=True, acts_late=True)
def task_a(self, s: str):
    sleep(3)
    logging.info("Job received in task A")
    if random() <= 0.1:
        self.retry()
        logging.info("Need retry")
    # next = Operations().getValue("taskA/nextTask", "tasks.task_b")
    celery.send_task("tasks.task_b", [s])
    


@celery.task(name='tasks.task_b', bind=True, acts_late=True)
def task_b(self, s: str):
    sleep(3)
    logging.info("Job received in task B")
    if random() <= 0.1:
        self.retry()
        logging.info("Need retry")
    celery.send_task("tasks.task_c", [s])


@celery.task(name='tasks.task_c', bind=True, acts_late=True)
def task_c(self, s: str):
    sleep(3)
    logging.info("Job received in task C")
    if random() <= 0.1:
        celery.send_task("tasks.task_a", [s])
    else:
        print("END")
    
