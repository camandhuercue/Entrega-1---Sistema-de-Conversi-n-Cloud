from flask import Flask, render_template, redirect,  url_for, request

app = Flask(__name__)

app.secret_key = '$$%2342432423"##4rewr!'

@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/api/auth/login", methods=['GET', 'POST'])
def login():
    print(request.method)
    print('Esto es request:', request.form)
    return render_template('login.html')


@app.route("/api/auth/signup", methods=['GET', 'POST'])
def signUp():
    print(request.method)
    print('Esto es request:', request.form)
    return render_template('signup.html')

@app.route("/api/task")
def tasks():
    return render_template('task.html')

if __name__=='__main__':
    app.run(debug=True)

