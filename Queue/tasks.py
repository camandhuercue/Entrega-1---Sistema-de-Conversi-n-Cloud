from celery import Celery
import zipfile, py7zr, bz2, tarfile
from os import path

app = Celery( 'tasks' , broker = 'redis://localhost:6379/0' )

@app.task
def comprimir_zip(filename, zipname, new_path):
    print ('\n-> Se va a comprimir el archivo: {}'.format(filename))
    zfile = zipfile.ZipFile(new_path + '/' + zipname, 'w')
    zfile.write(filename, compress_type = zipfile.ZIP_DEFLATED)
    zfile.close()
    print ('\n-> El archivo comprimido se copió a : {}'.format(new_path))

@app.task
def comprimir_7z(filename, zipname, new_path):
    with py7zr.SevenZipFile(new_path + "/" + zipname, 'w') as archive:
        archive.writeall(filename)

@app.task
def comprimir_bz2(filename, zipname, new_path):
    with bz2.open(new_path + "/" + zipname, "wb") as f:
        with open(filename, "rb") as file:
            f.write(file.read())

@app.task
def comprimir_tar(filename, zipname, new_path, option):
    if option == 'zip':
        with tarfile.open(new_path + "/" + zipname, "w:gz") as tar:
            tar.add(filename, arcname="archive/" + filename)
    if option == 'bz2':
        with tarfile.open(new_path + "/" + zipname, "w:bz2") as tar:
            tar.add(filename, arcname="archive/" + filename)