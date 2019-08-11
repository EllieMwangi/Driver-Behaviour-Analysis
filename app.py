from flask import Flask, render_template, request
from forms import LoginForm

app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY'] = 'envirocar2019'


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

    return render_template('signup.html')

if __name__ == '__main__':
    app.run(debug=True)


