import zipfile, py7zr, bz2, tarfile
from os import path, remove
import shutil
import time



def comprimir_zip(filename, zipname, new_path, ID):
#    print ('\n-> Se va a comprimir el archivo: {}'.format(filename))
    zfile = zipfile.ZipFile(new_path + '/' + zipname, 'w')
    zfile.write(ID, compress_type = zipfile.ZIP_DEFLATED, arcname=filename)
    zfile.close()
#    print ('\n-> El archivo comprimido se copió a : {}'.format(new_path))
    remove(ID)

#@app.task
def comprimir_7z(filename, zipname, new_path, ID):
    with py7zr.SevenZipFile(new_path + "/" + zipname, 'w') as archive:
        archive.writeall(ID, arcname=filename)
    remove(ID)

#@app.task
def comprimir_bz2(filename, zipname, new_path, ID):
    with bz2.open(new_path + "/" + zipname, "wb") as f:
        with open(ID, "rb") as file:
            f.write(file.read())
    remove(ID)

#@app.task
def comprimir_tar(filename, zipname, new_path, option, ID):
    if option == 'zip':
        with tarfile.open(new_path + "/" + zipname, "w:gz") as tar:
            tar.add(ID, arcname="archive/" + filename)
        remove(ID)
    if option == 'bz2':
        with tarfile.open(new_path + "/" + zipname, "w:bz2") as tar:
            tar.add(ID, arcname="archive/" + filename)
        remove(ID)


filename="pruebas.csv"
Path="/workspace/files/"
ID="DUMMY"

print(len(list(range(1,100))))

start_time = time.time()

for n in list(range(1,100)):
    shutil.copyfile(Path + filename, ID)
    comprimir_zip(filename, filename + '.zip', Path, ID)

print("--- Tiempo utilizado para comprimir 100 archivos en zip: %s segundos ---" % (time.time() - start_time))

start_time = time.time()
for n in list(range(1,100)):
    shutil.copyfile(Path + filename, ID)
    comprimir_7z(filename, filename + '.7z', Path, ID)

print("--- Tiempo utilizado para comprimir 100 archivos en 7Z: %s segundos ---" % (time.time() - start_time))

start_time = time.time()
for n in list(range(1,100)):
    shutil.copyfile(Path + filename, ID)
    comprimir_bz2(filename, filename + '.bz2', Path, ID)

print("--- Tiempo utilizado para comprimir 100 archivos en BZ2: %s segundos ---" % (time.time() - start_time))

start_time = time.time()
for n in list(range(1,100)):
    shutil.copyfile(Path + filename, ID)
    comprimir_tar(filename, filename + '.tgz', Path, zip, ID)

print("--- Tiempo utilizado para comprimir 100 archivos en TGZ: %s segundos ---" % (time.time() - start_time))

start_time = time.time()
for n in list(range(1,100)):
    shutil.copyfile(Path + filename, ID)
    comprimir_tar(filename, filename + '.tbz2', Path, bz2, ID)

print("--- Tiempo utilizado para comprimir 100 archivos en TBZ2: %s segundos ---" % (time.time() - start_time))
