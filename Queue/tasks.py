from celery import Celery
import zipfile

app = Celery( 'tasks' , broker = 'redis://localhost:6379/0' )

@app.task
def comprimir(filename, zipname, new_path):
    print ('\n-> Se va a comprimir el archivo: {}'.format(filename))
    zfile = zipfile.ZipFile(new_path + '/' + zipname, 'w')
    zfile.write(filename, compress_type = zipfile.ZIP_DEFLATED)
    zfile.close()
    print ('\n-> El archivo comprimido se copió a : {}'.format(new_path))