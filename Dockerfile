FROM python:3.7-slim
RUN apt-get -y update
COPY . /app
WORKDIR /app 
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "app.py"]