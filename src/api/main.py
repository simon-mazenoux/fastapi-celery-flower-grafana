from os import environ
from celery import Celery
from celery.result import AsyncResult
from fastapi import FastAPI, Response, status

from pydantic import BaseModel



class JobModel(BaseModel):
    name: str


app = FastAPI()

CELERY_BROKER_URL=environ['CELERY_BROKER_URL']
CELERY_RESULT_BACKEND=environ['CELERY_RESULT_BACKEND']

celery = Celery('tasks',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)

@app.get("/")
async def hello_word():
    return {"Hello": "World"}


@app.post("/add")
async def add(a: int, b: int):
    task = celery.send_task('tasks.add', args=[a, b])
    return task.id


@app.post("/divide")
async def divide(a: int, b: int):
    task = celery.send_task('tasks.divide', args=[a, b])
    return task.id


@app.get('/check/<string:id>')
async def check_task(id: str,  response: Response):
    res = AsyncResult(id, app=celery)

    if res.successful():
        response.status_code = status.HTTP_200_OK
        return str(res.result)
    
    if res.failed():
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

    response.status_code = status.HTTP_202_ACCEPTED
    return "PENDING"


@app.post('/job', status_code=status.HTTP_202_ACCEPTED)
async def submit_job(job: JobModel):
    task = celery.send_task('tasks.task_a', args=[job.json()])
    return task.id





async def submit_tsp():
    api_key = "AIzaSyD4Ozj95sho6lFH0FHFgD82LloqvBknLaA"