import base64
from queue_api.utils import get_tasks
from tasks import comprimir_zip, comprimir_7z, comprimir_bz2, comprimir_tar, update_task, send_email
from os import path, mkdir, remove, rename
import shutil
import time
import json
from google.cloud import storage
from flask import Flask, request

app = Flask(__name__)

@app.route("/pub/sub/message/compress", methods=["POST"])
def hello_pubsub():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400
    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400
    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        data = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()

    print(data)
    data = json.loads(data)
    #client = storage.Client.from_service_account_json('./key.json')
    client = storage.Client()
    bucket_name = "unsuperbucketparaelproyecto"
    T = get_tasks(data['uuid'])
    bucket = client.get_bucket(bucket_name)
    print("Se llama la tarea de UUID: {}".format(data['uuid']))
    for t in T:
        Path = t['path']
        file_name = t['filename']
        ID = t['id']
        blob_name = Path
        blob = bucket.blob(blob_name)
        output_file_name = ID
        algo = blob.download_as_bytes()
        with open(output_file_name, "wb") as binary_file:
            binary_file.write(algo)
        if t['format'] == "ZIP":
            comprimir_zip(file_name, file_name + '.zip', Path, ID, bucket)
            #send_email.delay(email, t['filename'], t['id'])
            update_task(t['id'])
        if t['format'] == "7Z":
            comprimir_7z(file_name, file_name + '.7z', Path, ID, bucket)
            #send_email.delay(email, t['filename'], t['id'])
            update_task(t['id'])
        if t['format'] == "BZ2":
            comprimir_bz2(file_name, file_name + '.bz2', Path, ID, bucket)
            #send_email.delay(email, t['filename'], t['id'])
            update_task(t['id'])
        if t['format'] == "TGZ":
            comprimir_tar(file_name, file_name + '.tgz', Path, 'zip', ID, bucket)
            #send_email.delay(email, t['filename'], t['id'])
            update_task(t['id'])
        if t['format'] == "TBZ2":
            comprimir_tar(file_name, file_name + '.tbz2', Path, 'bz2', ID, bucket)
            #send_email.delay(email, t['filename'], t['id'])
            update_task(t['id'])

    return ("", 204)

    print("Fin de la funcion")
