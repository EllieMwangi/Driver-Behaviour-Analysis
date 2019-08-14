from flask import render_template, request, redirect, flash, url_for
from myapp.forms import LoginForm, SignupForm
from myapp import app, db
from myapp.models import User
import uuid, hashlib


def hash_password(password):
    # uuid is used to generate a random number
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt


def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()


@app.route('/', methods=['GET','POST'])
def index():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        print(email, password)

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        model = request.form['model']
        vid = request.form['vid']
        password = request.form['pass']

        hashed_password = hash_password(password)
        try:
            user = User(username=name,email=email,password_hash=hashed_password,vehicle_model=model, vehicle_id=vid)
            db.session.add(user)
            db.session.commit()
            flash('You are now registered!')
            return redirect(url_for('index'))
        except Exception as inst:
            print(type(inst))

    return render_template('signup.html', form=form)
