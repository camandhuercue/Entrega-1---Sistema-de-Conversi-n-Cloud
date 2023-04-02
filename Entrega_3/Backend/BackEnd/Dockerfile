FROM python:latest

WORKDIR /workspace

COPY ./compress_api/* ./compress_api/
COPY ./setup.py .
#COPY ./wsgi.py .
COPY ./instance/* ./instance/

RUN mkdir -p /workspace/files

RUN pip install --upgrade pip
RUN pip install -e .
RUN pip install gunicorn

ENV FLASK_APP="compress_api"
ENV DB_HOST="172.16.2.3"
ENV DB_DB="compress_database"
ENV DB_USER="postgres"
ENV DB_PORT="5432"
ENV JWTSECRET="123"
#ENV DB_PW="$$53eer3&777R"
#ENV FLASK_DEBUG=1

EXPOSE 5000

#CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "compress_api:create_app()"]
