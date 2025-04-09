FROM python:3.12-slim

WORKDIR /scheduler
COPY ./requirements.txt /scheduler/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /scheduler/requirements.txt

COPY . /scheduler

CMD ["python","scheduler.py"]