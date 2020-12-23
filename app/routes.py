from flask import render_template, flash, redirect, url_for, jsonify
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import EditProfileForm
from flask_login import current_user, login_user
from app.models import User, Reactions, Post, Courses, Signups, Speed, Status
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
import random 
from datetime import datetime

@app.route('/')
@app.route('/index')
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
@app.route('/user/<username>/create_class') 
@login_required # Have to be logged in as a teacher for this to work
def create(username):
    t_courses_all = Courses.query.filter_by(teacher_id=current_user.id) # All of that teacher's courses   
    return render_template('create_class.html', t_courses_all=t_courses_all, title="Create a Class")

# Adds the new course to the database 
@app.route('/user/<username>/create_class/new', methods=["POST"]) # This is a POST method
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

# Last seen function
@app.before_request # This function will be executed right before the view function
def before_request():
    if current_user.is_authenticated: # Checks whether the current user is logged in
        current_user.last_seen = datetime.utcnow() # Sets the last seen to the date using the UTC time zone 
        db.session.commit() # Don't need to do db.session.add() because the user is already in the database (using a current_user)

# Edit Profile function
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit(): # If the form successfully submitted
        current_user.username = form.username.data # Set the user's username to what they entered in the form
        current_user.about_me = form.about_me.data # Set about me for current user to input from the form
        db.session.commit() # Commit changes to the database
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET': # If this is the first time that the form has been requested
        form.username.data = current_user.username # Then pre-populate the fields with the data in the database
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, title="Edit Profile")

@app.route('/user/<username>/classes') # User's classes
@login_required
def classes(username): # the word after def has to be the same as the text in the urlfor quotation marks 
    user = User.query.filter_by(username=username).first_or_404()
    user_signups_filtered = User.query.join(Signups, (Signups.user_id == User.id)).\
        join(Courses, (Courses.id == Signups.course)).\
            with_entities(Signups).\
                filter(Signups.user_id == user.id)
    teacher_courses = Courses.query.filter_by(teacher_id=user.id).all()
    return render_template('classes.html', user=user, user_signups_filtered=user_signups_filtered, teacher_courses=teacher_courses, title="Classes")

# Add a new class
@app.route('/user/<username>/classes/add', methods=["POST"]) # This is a POST method
@login_required
def add(username):
    user = User.query.filter_by(username=username).first_or_404()
    code = request.form.get("title") # This stores the user code that the student enters
    course = Courses.query.filter_by(code=code).first_or_404() # Filter through courses by this code
    new_signup = Signups(user_id = user.id, course=course.id) # Now that you have that course, take the course id and enter that into the course field
    signups_all = Signups.query.all() # Getting all of the sign-ups
    already = False
    for s in signups_all:
        if new_signup.user_id == s.user_id and new_signup.course == s.course:
            already = True
            flash('You have already enrolled in this course. Nice try.')
    if already == False:
        db.session.add(new_signup)
        db.session.commit()
    return redirect(url_for('classes', username=user.username))

@app.route('/classes/rooms/<room_id>') # The text inside the <> has to be the same as the parameter in the def room()
@login_required # Have to be logged in to see these rooms
def rooms(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    reactions_all = Reactions.query.filter_by(reactions_course_id=room_id).all()
    speeds_all = Speed.query.filter_by(speed_course_id=room_id).all()
    status_all = Status.query.all()
    status_filtered = Status.query.filter_by(status_course_id=room_id).all()
    present_list = [] # List of students present
    absent_list = [] # List of absent students (those naughty lil kids! Santa ain't bringing you presents this year!)
    students = Signups.query.filter_by(course=room_id) # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(reactions_course_id=room_id) # List of reactions that happened in this specific course
    speeds_specific = Speed.query.filter_by(speed_course_id=room_id) # List of reactions that happened in this specific course
    for s in students:
        present = False
        already = False
        for r in reactions_specific:
            if s.user_id == r.user_id: # If this is true, then that student has reacted in this class
                for p in present_list: # Checking to see whether they are already in the present_list
                    if s.student.username == p: # If they are already in the present list
                        already = True # Set already to true
                if already == False:
                    present_list.append(s.student.username) # Or you can append their ID by doing s.ID (s.student is the backref which will bring up the user in <User> form)
                    present = True
        if present == False: # If they didn't make a reaction
            for sp in speeds_specific: # Then check if they made a speed complaint
                if s.user_id == sp.user_id: # If this is true, then that student has complained about the speed in this class (naughty lil kids!)
                    present_list.append(s.student.username) 
                    present = True
            if present == False: # If they didn't react or enter a speed
                absent_list.append(s.student.username) # Add them to the absent list
    found = False # Found variable is for the teacher side regarding whether they have activated the class or not (and whether it is in the database yet)
    if status_all is not None: # If there are some courses already in the status table
        for s in status_all: # Checking whether this course is already in the database (aka if it hasn't been activated even once yet)
            if s.status_course_id == course.id:
                found = True
    if course.teacher_id != current_user.id: # If the current user is not that teacher (current user is a student)
        if found == False: # If this course has never been activated yet
            return render_template('unactivated.html') # Then render the HTMl for the unactivated page
        elif found == True:
            specific_status = Status.query.filter_by(status_course_id=room_id).first_or_404()
            if specific_status.status == 0: # If this course has been activated before (already in database) AND it's status is 0 (unactivated)
                return render_template('unactivated.html', course=course) 
    return render_template('rooms.html', course=course, reactions_all=reactions_all, speeds_all=speeds_all, status_all=status_all, status_filtered=status_filtered, found=found, present_list=present_list, absent_list=absent_list, title=course.course_name) 

# Attendance 
@app.route('/classes/rooms/<room_id>/attendance', methods=["POST"]) 
@login_required 
def attendance(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    present_list = [] # List of students present
    absent_list = [] # List of absent students (those naughty lil kids! Santa ain't bringing you presents this year!)
    students = Signups.query.filter_by(course=room_id) # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(reactions_course_id=room_id) # List of reactions that happened in this specific course
    speeds_specific = Speed.query.filter_by(speed_course_id=room_id) # List of reactions that happened in this specific course
    for s in students:
        present = False
        already = False
        for r in reactions_specific:
            if s.user_id == r.user_id: # If this is true, then that student has reacted in this class
                for p in present_list: # Checking to see whether they are already in the present_list
                    if s.student.username == p: # If they are already in the present list
                        already = True # Set already to true
                if already == False:
                    present_list.append(s.student.username) # Or you can append their ID by doing s.ID (s.student is the backref which will bring up the user in <User> form)
                    present = True 
        if present == False: # If they didn't make a reaction
            for sp in speeds_specific: # Then check if they made a speed complaint
                if s.user_id == sp.user_id: # If this is true, then that student has complained about the speed in this class (naughty lil kids!)
                    present_list.append(s.student.username) 
                    present = True
            if present == False: # If they didn't react or enter a speed
                absent_list.append(s.student.username) # Add them to the absent list
    return render_template('attendance.html', course=course, present_list=present_list, absent_list=absent_list, title=course.course_name)

# Status and Attendance JSON 
@app.route('/classes/rooms/<room_id>/attendance_json', methods=["GET", "POST"]) 
@login_required 
def attendance_json(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    present_set = set() # Set of students present
    absent_set = set() # Set of absent students (those naughty lil kids! Santa ain't bringing you presents this year!)
    present_list = list()
    absent_list = list()
    final_list = list()
    students = Signups.query.filter_by(course=room_id) # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(reactions_course_id=room_id) # List of reactions that happened in this specific course
    speeds_specific = Speed.query.filter_by(speed_course_id=room_id) # List of reactions that happened in this specific course
    for s in students:
        for r in reactions_specific: 
            if s.user_id == r.user_id: # If the student has reacted
                present_set.add(s.student.username) # Then add to the present list
        for sp in speeds_specific: 
            if s.user_id == sp.user_id: # If the student has made a speed complaint
                present_set.add(s.student.username) # Then add to the present list
    for student in students: # Going through the list of students
        found = False
        for p in present_set: # Going through list of present students
            if student.student.username == p: # If the student in the student list is in the present list
                found = True # Set found to true
        if found == False: # Otherwise, if they are not in the present list
            absent_set.add(student.student.username) # Add that student to the absent list
    # for s in students: 
    #     present = False
    #     already = False
    #     for r in reactions_specific:
    #         if s.user_id == r.user_id: # If this is true, then that student has reacted in this class
    #             for p in present_list: # Checking to see whether they are already in the present_list
    #                 if s.student.username == p: # If they are already in the present list
    #                     already = True # Set already to true
    #             if already == False:
    #                 present_list.append(s.student.username) # Or you can append their ID by doing s.ID (s.student is the backref which will bring up the user in <User> form)
    #                 present = True 
    #     if present == False: # If they didn't make a reaction
    #         for sp in speeds_specific: # Then check if they made a speed complaint
    #             if s.user_id == sp.user_id: # If this is true, then that student has complained about the speed in this class (naughty lil kids!)
    #                 present_list.append(s.student.username) 
    #                 present = True
    #         if present == False: # If they didn't react or enter a speed
    #             absent_list.append(s.student.username) # Add them to the absent list
    present_list = present_set
    absent_list = absent_set
    converted_dict_present = {
        "Present": list(present_list)  
    }
    final_list.append(converted_dict_present)
    
    converted_dict_absent = {
        "Absent": list(absent_list)
    }
    final_list.append(converted_dict_absent)
    #return str(final_list)
    return jsonify(list(final_list))

# Method to activate class
@app.route('/classes/rooms/<room_id>/activate', methods=["POST"]) # POST method, important declaration
@login_required
def activate(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    active = Status(status_course_id=course.id, status=1) # Status is 1, meaning class is activated
    status_all = Status.query.all()
    found = False
    for s in status_all:
        if active.status_course_id == s.status_course_id:
            exists = Status.query.filter_by(status_course_id=active.status_course_id).first_or_404() # Variable that represents the correct row of the database
            exists.status=1
            db.session.add(exists)
            db.session.commit()
            found = True
    if found == False:
        db.session.add(active)
        db.session.commit()
    return redirect(url_for('rooms', room_id=course.id))

# Method to end class
@app.route('/classes/rooms/<room_id>/end', methods=["POST"]) # POST method, important declaration
@login_required
def end(room_id):
    course = Courses.query.filter_by(id=room_id).first_or_404()
    end = Status(status_course_id=course.id, status=0) # Status is 0, meaning class is ended. What the students are thinking --> Yay! 
    status_all = Status.query.all()
    found = False
    for s in status_all: # Looping through all the Status objects, e.g. <Status 1 1 1>
        if end.status_course_id == s.status_course_id: # If this course is laready in the database
            exists = Status.query.filter_by(status_course_id=end.status_course_id).first_or_404() # Variable that represents the correct row of the database
            exists.status = 0  # Then update that course's status to 0 (inactive)
            db.session.add(exists) # Adding and committing to the database
            db.session.commit() 
            reactions = Reactions.query.filter_by(reactions_course_id=course.id) # Filtering the reactions to get only the reactions for this specific course
            for r in reactions: # Looping through all the reactions for this course only
                db.session.delete(r) # Deleting them because the class has ended, hurrah!
                db.session.commit() 
            speeds = Speed.query.filter_by(speed_course_id=course.id) # Deleting all the speed complaints for this course
            for s in speeds:
                db.session.delete(s)
                db.session.commit()
            found = True # This course was found in the database
    if found == False: # If this course was not found in the database
        db.session.add(end) # Just add the entire Status object
        db.session.commit()
    return redirect(url_for('rooms', room_id=course.id))

# Start of the defs for all the emotions and speeds
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

# Percentage of happiness in class
@app.route('/classes/rooms/<room_id>/percent', methods=["GET", "POST"])
@login_required
def percent(room_id):
    reactions = Reactions.query.filter_by(reactions_course_id=room_id) # Reactions represents all the reactions for this specific room
    percent_happy = "No reactions, no percentage"
    size = 0
    for reaction in reactions:
        size += 1
    if size > 0:
        total = 0
        happy = 0
        for r in reactions:
            total += 1
            if r.emotions == 0:
                happy += 1
        percent_happy = (happy/total) * 100
    return str(percent_happy)
    #return str(random.randint(100000, 999999)) # Generating a random code

# Fetch Reactions page
@app.route('/classes/rooms/<room_id>/reactions_only', methods=["GET", "POST"])
@login_required
def reactions_only(room_id):
    reactions = Reactions.query.filter_by(reactions_course_id=room_id).all() # Only show the reactions for this specific course
    result = []
    for r in reactions:
        converted_dict = {
            "reactions_id": r.id,
            "user_id": r.reactor.username,
            "reactions": r.emotions,
            "reactions_course_id": r.reactions_course_id
        }
        result.append(converted_dict)
    return jsonify(result)

# Fetch Speeds page
@app.route('/classes/rooms/<room_id>/speeds_only', methods=["GET", "POST"])
@login_required
def speeds_only(room_id):
    speeds = Speed.query.filter_by(speed_course_id=room_id).all() # Only show the speeds for this specific course
    result = []
    for s in speeds:
        converted_dict = {
            "speeds_id": s.id,
            "user_id": s.speeder.username,
            "speed": s.speed,
            "speed_course_id": s.speed_course_id
        }
        result.append(converted_dict)
    return jsonify(result)

# Fetch course status (active or inactive) json
@app.route('/classes/rooms/<room_id>/course_status', methods=["GET", "POST"])
@login_required
def course_status(room_id): 
    status = Status.query.filter_by(status_course_id=room_id).all() # Only show the status for this specific course
    result = list()
    for s in status:
        converted_dict = {
            "status_id": s.id,
            "course_id": s.status_course_id,
            "status": s.status
        }
        result.append(converted_dict)
    return jsonify(result)

# Just so I can see all the databases
@app.route('/database') 
def database():
    user_all = User.query.all() # All the users are stored in this variable, to be used in the HTML 
    reactions_all = Reactions.query.all()
    courses_all = Courses.query.all()
    signups_all = Signups.query.all()
    speed_all = Speed.query.all()
    status_all = Status.query.all()
    #user_signups = User.query.join(Signups, (Signups.user_id == User.id)) 
    user_signups = User.query.join(Signups, (Signups.user_id == User.id)).join(Courses, (Courses.id == Signups.course)) 
    return render_template('database.html', user_all=user_all, reactions_all=reactions_all, courses_all=courses_all, signups_all=signups_all, user_signups=user_signups, speed_all=speed_all, status_all=status_all, title='Database') # Have to pass in your variables above in here

# Testing javascript image reload
@app.route('/image-reload')
def reload():
    return render_template('image-reload.html', title="Image Reload") 