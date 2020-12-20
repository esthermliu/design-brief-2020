from flask import render_template, flash, redirect, url_for
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from flask_login import current_user, login_user
from app.models import User, Reactions, Post, Courses, Signups
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse

@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': "Beautiful day in Kirkland, Washington!"
        },

        {
            'author': {'username': 'Susan'},
            'body': "My name is Susan!"
        }
    ]

    return render_template('index.html', title="Home", posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    # print("Bob", form)
    # print("Form's password method", form.password())
    # print(form.password(size=54))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    print("role", form.role)
    print("label", form.role.label)
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>') # User profile page
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts, title=username)

@app.route('/user/<username>/classes') # User's classes/rooms
@login_required
def classes(username): # the word after def has to be the same as the text in the urlfor quotation marks 
    user = User.query.filter_by(username=username).first_or_404()
    user_signups = User.signups 
    return render_template('classes.html', user=user, user_signups=user_signups, title="Classes")

@app.route('/user/<username>/classes/add', methods=["POST"]) #This is a POST method
def add(username):
    # Add a new class
    user = User.query.filter_by(username=username).first_or_404()
    code = request.form.get("title") # This stores the user code that the student enters
    course = Courses.query.filter_by(code=code).first_or_404() # Filter through courses by this code
    new_signup = Signups(user_id = user.id, course=course.id) # Now that you have that course, take the course id and enter that into the course field
    db.session.add(new_signup)
    db.session.commit()
    return redirect(url_for('classes', username=user.username))

@app.route('/database') # Just so I can see all the databases
def database():
    user_all = User.query.all() # All the users are stored in this variable, to be used in the HTML 
    reactions_all = Reactions.query.all()
    courses_all = Courses.query.all()
    signups_all = Signups.query.all()
    return render_template('database.html', user_all=user_all, reactions_all=reactions_all, courses_all=courses_all, signups_all=signups_all, title='Database') # Have to pass in your variables above in here

@app.route('/image-reload')
def reload():
    return render_template('image-reload.html', title="Image Reload") 