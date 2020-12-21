from flask import render_template, flash, redirect, url_for
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from flask_login import current_user, login_user
from app.models import User, Reactions, Post, Courses, Signups, Speed
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
import random 

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

# Page to create a new class as a teacher
@app.route('/user/<username>/create-class') 
@login_required # Have to be logged in as a teacher for this to work
def create(username):
    t_courses_all = Courses.query.filter_by(teacher_id=current_user.id) # All of that teacher's courses   
    return render_template('create-class.html', t_courses_all=t_courses_all, title="Create a Class")

# Adds the new course to the database 
@app.route('/user/<username>/create-class/new', methods=["POST"]) # This is a POST method
@login_required 
def newclass(username):
    course_name = request.form.get("course_name")
    rand_code = random.randint(100000, 999999) # Generating a random code
    courses_all = Courses.query.all()
    # Making sure that the code hasn't already been generated for a previous class
    for c in courses_all: # Iterating through all the courses
        if c.code == rand_code: # If the code of an existing course already exists
            rand_code = random.randint(100000, 999999) # Generate a new random code
    new_course = Courses(course_name=course_name, code=rand_code, teacher_id=current_user.id)
    db.session.add(new_course)
    db.session.commit()
    return redirect(url_for('create', username=current_user.username)) # Redirects to the create page

@app.route('/user/<username>') # User profile page
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts, title=username)

@app.route('/user/<username>/classes') # User's classes
@login_required
def classes(username): # the word after def has to be the same as the text in the urlfor quotation marks 
    user = User.query.filter_by(username=username).first_or_404()
    user_signups = User.query.join(Signups, (Signups.user_id == User.id)).join(Courses, (Courses.id == Signups.course))
    teacher_courses = Courses.query.filter_by(teacher_id=user.id)
    return render_template('classes.html', user=user, user_signups=user_signups, teacher_courses=teacher_courses, title="Classes")

@app.route('/user/<username>/classes/add', methods=["POST"]) # This is a POST method
@login_required
def add(username):
    # Add a new class
    user = User.query.filter_by(username=username).first_or_404()
    code = request.form.get("title") # This stores the user code that the student enters
    course = Courses.query.filter_by(code=code).first_or_404() # Filter through courses by this code
    new_signup = Signups(user_id = user.id, course=course.id) # Now that you have that course, take the course id and enter that into the course field
    db.session.add(new_signup)
    db.session.commit()
    return redirect(url_for('classes', username=user.username))

@app.route('/classes/rooms/<room_id>') # The text inside the <> has to be the same as the parameter in the def room()
@login_required # Have to be logged in to see these rooms
def rooms(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    reactions_all = Reactions.query.all() # Tried filtering for reactions and speeds, but it wouldn't let me iterate through the object in HTML, so I had to check with if statements in the HTML :(
    speeds_all = Speed.query.all()
    return render_template('rooms.html', course=course, reactions_all=reactions_all, speeds_all=speeds_all, title=course.course_name) 

@app.route('/classes/rooms/<room_id>/good', methods=["POST"]) # Adds an emotion, also don't forget to add this methods POST thing!
@login_required
def happy(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404() # Finding the actual course by filtering through the room_id
    reaction = Reactions(user_id=current_user.id, emotions=0, reactions_course_id=room_id) # This is the user's reaction based on the button pressed
    db.session.add(reaction)
    db.session.commit()
    return redirect(url_for('rooms', room_id=course.id)) # Redirects to the room page

@app.route('/classes/rooms/<room_id>/okay', methods=["POST"]) # Adds an emotion, also don't forget to add this methods POST thing!
@login_required
def okay(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    reaction = Reactions(user_id=current_user.id, emotions=1, reactions_course_id=room_id)
    db.session.add(reaction)
    db.session.commit()
    return redirect(url_for('rooms', room_id=course.id)) # Redirects to the room page

@app.route('/classes/rooms/<room_id>/bad', methods=["POST"]) # Adds an emotion, also don't forget to add this methods POST thing!
@login_required
def bad(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    reaction = Reactions(user_id=current_user.id, emotions=2, reactions_course_id=room_id)
    db.session.add(reaction)
    db.session.commit()
    return redirect(url_for('rooms', room_id=course.id)) # Redirects to the room page

@app.route('/classes/rooms/<room_id>/fast', methods=["POST"]) # Too Fast!
@login_required
def fast(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    speed = Speed(user_id=current_user.id, speed=0, speed_course_id=room_id)
    db.session.add(speed)
    db.session.commit()
    return redirect(url_for('rooms', room_id=course.id)) # Redirects to the room page

@app.route('/classes/rooms/<room_id>/slow', methods=["POST"]) # Too Fast!
@login_required
def slow(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    speed = Speed(user_id=current_user.id, speed=1, speed_course_id=room_id)
    db.session.add(speed)
    db.session.commit()
    return redirect(url_for('rooms', room_id=course.id)) # Redirects to the room page


# Just so I can see all the databases
@app.route('/database') 
def database():
    user_all = User.query.all() # All the users are stored in this variable, to be used in the HTML 
    reactions_all = Reactions.query.all()
    courses_all = Courses.query.all()
    signups_all = Signups.query.all()
    speed_all = Speed.query.all()
    #user_signups = User.query.join(Signups, (Signups.user_id == User.id)) 
    user_signups = User.query.join(Signups, (Signups.user_id == User.id)).join(Courses, (Courses.id == Signups.course)) 
    return render_template('database.html', user_all=user_all, reactions_all=reactions_all, courses_all=courses_all, signups_all=signups_all, user_signups=user_signups, speed_all=speed_all, title='Database') # Have to pass in your variables above in here

# Testing javascript image reload
@app.route('/image-reload')
def reload():
    return render_template('image-reload.html', title="Image Reload") 