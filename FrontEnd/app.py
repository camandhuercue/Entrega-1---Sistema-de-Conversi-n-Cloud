from flask import Flask, render_template, redirect,  url_for, request
from werkzeug.utils import secure_filename
import base64
from datetime import datetime

app = Flask(__name__)

app.secret_key = '$$%2342432423"##4rewr!'

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/api/auth/login", methods=['GET', 'POST'])
def login():
    print(request.method)
    params = {
        'user' : request.form.get('user'),
        'passwd' : request.form.get('passwd'),
    }
    print(params)
    return render_template('login.html')


@app.route("/api/auth/signup", methods=['GET', 'POST'])
def signUp():
    print(request.method)
    params = {
        'nombre' : request.form.get('nombre'),
        'correo' : request.form.get('correo'),
        'passwd1' : request.form.get('passwd1'),
        'passwd2' : request.form.get('passwd2')
    }
    print(params)
    return render_template('signup.html')

@app.route("/api/tasks", methods=['GET','POST'])
def tasks():
    print(request.method)
    if request.method == 'POST':
        file = request.files['archivo']
        form = [{
            'formato_origen' : 'ZIP',
            'formato_destino' : '7Z',
            'filename' : 'Entrega_0',
            'status' : 'Procesado',
            'id' : 0,
            'timestamp' : datetime.now()
            #'file_string' : base64.b64encode(file.read())
        }]
        params = {
            'formato_origen' : request.form.get('formato_origen'),
            'formato_destino' : request.form.get('formato_destino'),
            'filename' : secure_filename(file.filename),
            'status' : 'Procesado',
            'id' : 1,
            'timestamp' : datetime.now()
            #'file_string' : base64.b64encode(file.read())
        }
        form.append(params)
        print(form)
        return render_template('task.html', form = form)
    return render_template('task.html')

if __name__=='__main__':
    app.run(debug=True, port=4000)

