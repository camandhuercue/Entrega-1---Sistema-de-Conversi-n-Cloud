FROM python:latest

WORKDIR /workspace

COPY ./queue_api/* ./queue_api/
COPY ./*.py .
COPY ./requirements.txt .

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

CMD ["flask", "--app", "main", "run", "--host=0.0.0.0"]
