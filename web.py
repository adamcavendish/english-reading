from bottle import route, run, template, request

import rq
from redis import Redis
import logging

import english

redis_conn = Redis(host='localhost', port=6379)
rq_queue = rq.Queue(connection=redis_conn)
Going = {}


def checkGoing(student_id, Going):
    logger = logging.getLogger(student_id)
    logger.info(str(Going))
    job = Going.get(student_id)
    if job is None:
        return 'AVAIL'

    job_result = job.result
    if job_result is None:
        return 'GOING'
    elif job_result in ['SUCCESS', 'ERR_LOGIN_INFO', 'ERR_CAPTCHA_FAILED']:
        Going[student_id] = None
        return job_result
    else:
        return 'ERR_UNKNOWN'


@route('/')
def index():
    with open('index.html', 'r') as f:
        index = f.read()
    return template(index)


@route('/', method='POST')
def index_post():
    student_id = request.forms.get('student_id')
    password = request.forms.get('password')
    count = request.forms.get('count')

    try:
        count = int(count)
    except ValueError:
        return 'FAILURE'

    flag = Going.get(student_id)
    if flag is not None:
        return checkGoing(student_id, Going)

    job = rq_queue.enqueue(english.GoForEnglishReadingInQueue, student_id, password, count, Going)
    Going[student_id] = job

    return 'CREATE'


@route('/check/', method='POST')
def check():
    student_id = request.forms.get('student_id')
    return checkGoing(student_id, Going)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-10s %(levelname)-7s %(message)s',
                        datefmt='%m-%d-%H:%M', filename='web.log', filemode='w')
    run(host='0.0.0.0', port=12345)
