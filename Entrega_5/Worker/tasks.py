import zipfile, py7zr, bz2, tarfile
from os import path, remove
from sqlalchemy import and_, update
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from queue_api.models import Tasks_TB, tasks_schema
from queue_api import session, engine
from google.cloud import storage

def comprimir_zip(filename, zipname, new_path, ID, bucket):
    print ('\n-> Se va a comprimir el archivo a zip: {}'.format(filename))
    zfile = zipfile.ZipFile(zipname, 'w')
    zfile.write(ID, compress_type = zipfile.ZIP_DEFLATED, arcname=filename)
    zfile.close()
    blob_name = new_path + ".zip"
    source_file_name = zipname
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(source_file_name)
    print ('\n-> El archivo comprimido se copió a : {}'.format(new_path))

def comprimir_7z(filename, zipname, new_path, ID, bucket):
    with py7zr.SevenZipFile(zipname, 'w') as archive:
        archive.writeall(ID, arcname=filename)
    blob_name = new_path + ".7z"
    source_file_name = zipname
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(source_file_name)

def comprimir_bz2(filename, zipname, new_path, ID, bucket):
    with bz2.open(zipname, "wb") as f:
        with open(ID, "rb") as file:
            f.write(file.read())
    blob_name = new_path + ".bz2"
    source_file_name = zipname
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(source_file_name)

def comprimir_tar(filename, zipname, new_path, option, ID, bucket):
    if option == 'zip':
        with tarfile.open(zipname, "w:gz") as tar:
            tar.add(ID, arcname="archive/" + filename)
        blob_name = new_path + ".tgz"
        source_file_name = zipname
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(source_file_name)
    if option == 'bz2':
        with tarfile.open(zipname, "w:bz2") as tar:
            tar.add(ID, arcname="archive/" + filename)
        blob_name = new_path + ".tbz2"
        source_file_name = zipname
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(source_file_name)

def update_task(id):
    up = (update(Tasks_TB).where(Tasks_TB.id == id).values(status="processed"))
    conn = engine.connect()
    conn.execute(up)
    conn.commit()

def send_email(email, file_name, id):
    login = "soluciones.cloud.2023@hotmail.com"
    password = f"$$5fdsf&%*!"
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