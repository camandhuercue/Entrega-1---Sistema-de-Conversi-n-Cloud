from queue_api.models import Tasks_TB, tasks_schema
from queue_api import session, engine
from os import path, mkdir
from sqlalchemy import and_, update
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_tasks():
    tasks = session.query(Tasks_TB).filter_by(status='uploaded')
    return tasks_schema.dump(tasks)

def update_task(id):
    up = (update(Tasks_TB).where(Tasks_TB.id == id).values(status="processed"))
    conn = engine.connect()
    print(up)
    conn.execute(up)
    conn.commit()

def send_email(email, file_name, id):
    login = "soluciones.cloud.2023@hotmail.com"
    password = f""
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
    #server.connect("smtp.gmail.com",465)
    #server = smtplib.SMTP_SSL("smtp.gmail.com")
    server.login(login, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()