from celery import Celery
app = Celery('guoxiaonao', broker='redis://@127.0.0.1/1')

@app.task
def task_test():
    print("task is running....")