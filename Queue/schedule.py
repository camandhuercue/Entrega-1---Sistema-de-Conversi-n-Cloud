from queue_api.utils import get_tasks
from tasks import comprimir
from os import path, mkdir

T = get_tasks()
for t in T:
    Path = '/workspace/files/'
    email = t['email']
    if not path.exists(Path + email + '/compress'):
        mkdir(Path + email + "/compress/")
    print(path.basename(t['path']).split('/')[-1])
    file_name = path.basename(t['path']).split('/')[-1]
    comprimir(t['path'], file_name + '.zip', Path + email + '/compress')