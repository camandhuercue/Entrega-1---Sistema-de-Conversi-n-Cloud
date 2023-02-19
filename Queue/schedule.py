from queue_api.utils import get_tasks, update_task
from tasks import comprimir_zip, comprimir_7z, comprimir_bz2, comprimir_tar
from os import path, mkdir, remove, rename
import shutil

T = get_tasks()

for t in T:
    Path = '/workspace/files/'
    email = t['email']
    if not path.exists(Path + email + '/compress'):
        mkdir(Path + email + "/compress/")
    file_name = path.basename(t['path']).split('/')[-1]
    shutil.copyfile(t['path'], t['filename'])
    if t['format'] == "ZIP":
        comprimir_zip(t['filename'], file_name + '.zip', Path + email + '/compress')
        update_task(t['id'], t['email'], t['path'], t['format'])
    if t['format'] == "7Z":
        comprimir_7z(t['filename'], file_name + '.7z', Path + email + '/compress')
    if t['format'] == "BZ2":
        comprimir_bz2(t['filename'], file_name + '.bz2', Path + email + '/compress')
    if t['format'] == "TGZ":
        comprimir_tar(t['filename'], file_name + '.tgz', Path + email + '/compress', 'zip')
    if t['format'] == "TBZ2":
        comprimir_tar(t['filename'], file_name + '.tar.bz2', Path + email + '/compress', 'bz2')
    remove(t['filename'])