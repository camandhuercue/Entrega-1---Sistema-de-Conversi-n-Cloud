from queue_api.utils import get_tasks
from tasks import comprimir_zip, comprimir_7z, comprimir_bz2, comprimir_tar, update_task, send_email
from os import path, mkdir, remove, rename
import shutil
import time

while True:
    T = get_tasks()
    print("Se llama la tarea")
    for t in T:
        Path = '/workspace/files/'
        email = t['email']
        if not path.exists(Path + email + '/compress'):
            mkdir(Path + email + "/compress/")
        file_name = path.basename(t['path']).split('/')[-1]
        shutil.copyfile(t['path'], t['filename'])
        if t['format'] == "ZIP":
            comprimir_zip.delay(t['filename'], file_name + '.zip', Path + email + '/compress')
            send_email.delay(email, t['filename'], t['id'])
            update_task.delay(t['id'])
        if t['format'] == "7Z":
            comprimir_7z.delay(t['filename'], file_name + '.7z', Path + email + '/compress')
            send_email.delay(email, t['filename'], t['id'])
            update_task.delay(t['id'])
        if t['format'] == "BZ2":
            comprimir_bz2.delay(t['filename'], file_name + '.bz2', Path + email + '/compress')
            send_email.delay(email, t['filename'], t['id'])
            update_task.delay(t['id'])
        if t['format'] == "TGZ":
            comprimir_tar.delay(t['filename'], file_name + '.tgz', Path + email + '/compress', 'zip')
            send_email.delay(email, t['filename'], t['id'])
            update_task.delay(t['id'])
        if t['format'] == "TBZ2":
            comprimir_tar.delay(t['filename'], file_name + '.tbz2', Path + email + '/compress', 'bz2')
            send_email.delay(email, t['filename'], t['id'])
            update_task.delay(t['id'])
        #remove(t['filename'])
    time.sleep(30)
    print("Se inicia el Loop")