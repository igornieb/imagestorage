FROM python:3
WORKDIR /code

COPY requirements.txt /code/
COPY entrypoint.sh /code/
RUN pip install -r requirements.txt
COPY . /code/