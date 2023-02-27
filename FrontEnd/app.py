from flask import Flask, render_template, redirect,  url_for, request, session, Response
from werkzeug.utils import secure_filename
import base64
from datetime import datetime
import requests
import json

app = Flask(__name__)

app.secret_key = '$$%2342432423"##4rewr!'
ip_backend = '192.168.238.129:8080'

@app.route("/")
def index():
    if session.get("token"):
        return redirect('/api/tasks')
    return redirect('/api/auth/login')

@app.route("/api/auth/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get("token"):
            return redirect('/api/tasks')
        else:
            return render_template('login.html')
    elif request.method == 'POST':
        if session.get("token"):
            return redirect('/api/tasks')
        print(request.method)
        params = {
            'email' : request.form.get('user'),
            'password' : request.form.get('passwd'),
        }
        app.logger.info(params)
        url = "http://" + ip_backend + "/api/auth/login"
        x = requests.post(url, json = params)
        if x.status_code != 200:
            print(x.json())
            print("error de credenciales")
            return redirect('/api/auth/login')
        else:
            session['token'] = x.json()['access_token']
            return redirect('/api/tasks')


@app.route("/api/auth/signup", methods=['GET', 'POST'])
def signUp():
    if request.method == 'GET':
        if session.get("token"):
            return redirect('/api/tasks')
        else:
            return render_template('signup.html')
    if request.method == 'POST':     
        print(request.method)
        params = {
            'usuario' : request.form.get('nombre'),
            'email' : request.form.get('correo'),
            'password1' : request.form.get('passwd1'),
            'password2' : request.form.get('passwd2')
        }

        url = "http://" + ip_backend + "/api/auth/signup"
        x = requests.post(url, json = params)
        
        if x.status_code != 200:
            return redirect('/api/auth/signup')

        print(params)
        return redirect('/api/auth/login')

@app.route("/api/tasks", methods=['GET','POST'])
def tasks():
    print(request.method)
    if request.method == 'POST':
        if session.get("token"):
            pass
        else:
            return redirect('/api/auth/login')
        file = request.files['archivo']

        data = {
            'file_content': base64.b64encode(file.read()).decode("utf-8"),
            'filename': file.filename,
            'format': request.form.get('formato_destino')
        }
        url = "http://" + ip_backend + "/api/tasks"
        headers = {
            'Authorization': 'Bearer ' + session.get("token")
        }
        x = requests.post(url, json = data, headers = headers)
        if x.status_code != 200:
            return redirect('/api/auth/login')
        x = requests.get(url, headers = headers)
        if x.status_code != 200:
            session['token'] = None
            return redirect('/api/auth/login')
        form = x.json()
        print(form)
        return render_template('task.html', form = form)
    if request.method == 'GET':
        if session.get("token"):
            pass
        else:
            return redirect('/api/auth/login')
        url = "http://" + ip_backend + "/api/tasks"
        headers = {
            'Authorization': 'Bearer ' + session.get("token")
        }
        x = requests.get(url, headers = headers)
        if x.status_code != 200:
            print(x.json())
            session['token'] = None
            return redirect('/api/auth/login')
        if 'message' in x.json() and x.json()['message'] == "No hay registros disponibles":
            form = []
        else:
            form = x.json()
        print(form)
        return render_template('task.html', form = form)

@app.route("/api/auth/logout")
def logout():
    if request.method == 'GET':
        if session.get("token"):
            session['token'] = None
            return redirect('/api/auth/login')
        else:
            return redirect('/api/auth/login')

@app.route("/api/download/<int:id>")
def download(id):
    if session.get("token"):
        url = "http://" + ip_backend + "/api/tasks/{}".format(str(id))
        headers = {
            'Authorization': 'Bearer ' + session.get("token")
        }
        x = requests.get(url, headers = headers)
        if x.status_code != 200:
            print(x.json())
            session['token'] = None
            return redirect('/api/auth/login')
        name = x.json()['message']['internal_id'] + '.' + x.json()['message']['format'].lower()
        url = "http://" + ip_backend + "/api/files/{}".format(name)
        x = requests.get(url, headers = headers)
        if x.status_code != 200:
            print(x.json())
            session['token'] = None
            return redirect('/api/auth/login')
        file = x.json()['message']['data']
        file_name = x.json()['message']['name']
        binary_file = base64.decodebytes(file.encode("ascii"))
        formatos = {
            'zip': 'application/zip',
            'bz2': 'application/x-bzip2',
            'tbz2': 'application/x-bzip2',
            'tgz': 'application/gzip',
            '7z': 'application/x-7z-compressed'
        }
        return Response(binary_file, mimetype='application/octet-stream', headers={'Content-Disposition': 'attachment;filename={}'.format(file_name)})
    return redirect('/api/auth/login')

@app.route("/api/download_org/<int:id>")
def download_org(id):
    if session.get("token"):
        url = "http://" + ip_backend + "/api/tasks/{}".format(str(id))
        headers = {
            'Authorization': 'Bearer ' + session.get("token")
        }
        x = requests.get(url, headers = headers)
        if x.status_code != 200:
            print(x.json())
            session['token'] = None
            return redirect('/api/auth/login')
        name = x.json()['message']['internal_id']
        url = "http://" + ip_backend + "/api/files/{}".format(name)
        x = requests.get(url, headers = headers)
        if x.status_code != 200:
            print(x.json())
            session['token'] = None
            return redirect('/api/auth/login')
        file = x.json()['message']['data']
        file_name = x.json()['message']['name']
        binary_file = base64.decodebytes(file.encode("ascii"))
        return Response(binary_file, mimetype='application/octet-stream', headers={'Content-Disposition': 'attachment;filename={}'.format(file_name)})
    return redirect('/api/auth/login')

@app.route("/api/delete/<int:id>")
def delete(id):
    if session.get("token"):
        url = "http://" + ip_backend + "/api/tasks/{}".format(str(id))
        headers = {
            'Authorization': 'Bearer ' + session.get("token")
        }
        x = requests.delete(url, headers = headers)
        if x.status_code != 200:
            print(x.json())
            session['token'] = None
            return redirect('/api/auth/login')
        
        return redirect('/api/tasks')
        
    return redirect('/api/auth/login')

if __name__=='__main__':
    app.run(debug=True, port=4000)

