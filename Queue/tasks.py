from celery import Celery
import zipfile, py7zr, bz2, tarfile
from os import path, remove
from sqlalchemy import and_, update
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from queue_api.models import Tasks_TB, tasks_schema
from queue_api import session, engine


app = Celery( 'tasks' , broker = 'redis://192.168.238.129:6379/0' )

@app.task
def comprimir_zip(filename, zipname, new_path):
    print ('\n-> Se va a comprimir el archivo: {}'.format(filename))
    zfile = zipfile.ZipFile(new_path + '/' + zipname, 'w')
    zfile.write(filename, compress_type = zipfile.ZIP_DEFLATED)
    zfile.close()
    print ('\n-> El archivo comprimido se copió a : {}'.format(new_path))
    remove(filename)

@app.task
def comprimir_7z(filename, zipname, new_path):
    with py7zr.SevenZipFile(new_path + "/" + zipname, 'w') as archive:
        archive.writeall(filename)
    remove(filename)

@app.task
def comprimir_bz2(filename, zipname, new_path):
    with bz2.open(new_path + "/" + zipname, "wb") as f:
        with open(filename, "rb") as file:
            f.write(file.read())
    remove(filename)

@app.task
def comprimir_tar(filename, zipname, new_path, option):
    if option == 'zip':
        with tarfile.open(new_path + "/" + zipname, "w:gz") as tar:
            tar.add(filename, arcname="archive/" + filename)
        remove(filename)
    if option == 'bz2':
        with tarfile.open(new_path + "/" + zipname, "w:bz2") as tar:
            tar.add(filename, arcname="archive/" + filename)
        remove(filename)
@app.task
def update_task(id):
    up = (update(Tasks_TB).where(Tasks_TB.id == id).values(status="processed"))
    conn = engine.connect()
    print(up)
    conn.execute(up)
    conn.commit()
    
@app.task
def send_email(email, file_name, id):
    login = "soluciones.cloud.2023@hotmail.com"
    password = f"P4$$w0rD!2023*"
    sender_email = "soluciones.cloud.2023@hotmail.com"
    receiver_email = email
    message = MIMEMultipart("alternative")
    message["Subject"] = "Servicio de Notificación: Tarea Finalizada"
    message["From"] = sender_email
    message["To"] = receiver_email
    text = """\
    
Cordial saludo,

Por medio del presente se informa que la tarea para el archivo {} con id {} se ha finalizado con éxito y está disponible para su descarga.

Cordialmente,
Servicio de Compresión.""".format(file_name, id)

    part1 = MIMEText(text, "plain")
    message.attach(part1)
    
    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(login, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()