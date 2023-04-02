FROM python:latest

WORKDIR /workspace

COPY ./* /workspace
COPY ./static/img/* /workspace/static/img/
COPY ./templates/* /workspace/templates/
COPY ./templates/partials/* /workspace/templates/partials/

RUN pip install flask
RUN pip install requests

EXPOSE 5000

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0"]
