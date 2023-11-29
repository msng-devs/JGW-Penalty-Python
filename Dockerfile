FROM python:3.10.10

COPY . .
WORKDIR /jsp_django

WORKDIR ..
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN rm -rf ./logs
RUN mkdir ./logs

EXPOSE 50006

ENTRYPOINT gunicorn --bind=0.0.0.0:50006 jsp_django.wsgi:application