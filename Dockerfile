FROM python:3.7-slim
RUN apt-get -y update
RUN apt-get install -y gcc
RUN apt-get -y install libpq-dev python-dev
ENV PYTHONUNBUFFERED 1

ADD ./requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . /app
WORKDIR /app
ENTRYPOINT ["python", "app.py"]