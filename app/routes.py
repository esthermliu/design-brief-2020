from flask import render_template, flash, redirect, url_for, jsonify
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import EditProfileForm
from flask_login import current_user, login_user
from app.models import User, Reactions, Post, Courses, Signups, Session
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
import random 
from datetime import datetime, timedelta


@app.route('/')
@app.route('/index')
def index():
    # posts = [
    #     {
    #         'author': {'username': 'John'},
    #         'body': "Beautiful day in Kirkland, Washington!"
    #     },

    #     {
    #         'author': {'username': 'Susan'},
    #         'body': "My name is Susan!"
    #     }
    # ]
    return render_template('index.html', title="Home")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # If the current user is already logged in 
        return redirect(url_for('classes', username=current_user.username)) # Then direct the user to their classes page
    form = LoginForm() # Takes in the login form
    if form.validate_on_submit(): # If the form is validated
        user = User.query.filter_by(username=form.username.data).first() # Get the correct user from the database
        if user is None or not user.check_password(form.password.data): # If the user does not exist or the user's password is not the same as the password in the form
            flash('Invalid username or password') # Flash an invalid username/password message
            return redirect(url_for('login')) # Redirect them to the login page
        login_user(user, remember=form.remember_me.data) # Otherwise, log the user in 
        next_page = request.args.get('next') 
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('classes', username=current_user.username) # Redirects to the classes page
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
    # TODO: Look up how to generate a random UNIQUE code
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
    # TODO: Remove this for loop later by querying with a filter and checking if none
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



# Route for each session
@app.route('/classes/course/session/<session_id>') # The text inside the <> has to be the same as the parameter in the def room()
@login_required # Have to be logged in to see these rooms
def sessions(session_id):
    session = Session.query.get(session_id)
    
    # If the session as ended, then redirect
    if (session.timestamp_end is not None):
        return redirect(url_for('course_waiting_room', course_id=session.course_id))


    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    signups = Signups.query.filter_by(course=course_id) # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(session_id=session_id) # List of reactions that happened in this specific course, specific session
    # speeds_specific = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5) # Speeds filtered out by the course ID and by the reaction number
    present_set = set()
    absent_set = set()
    for r in reactions_specific: 
        if (r.reactor.role == 1): # If the reactor is a student
            present_set.add(r.reactor.username) # Then add to the present list
    for signup in signups: # Going through the list of signups
        if (signup.student.username not in present_set and signup.student.role == 1):
            absent_set.add(signup.student.username)
    
    return render_template('rooms.html', course=course,
                                        reactions_specific=reactions_specific,
                                        session=session,
                                        session_id=session_id,
                                        present_list=list(present_set), 
                                        absent_list=list(absent_set), 
                                        title=course.course_name) 

# Course waiting room, if there is an active session, then redirect to session. Otherwise, redirect to unactivated html
@app.route('/classes/course/<course_id>')
@login_required
def course_waiting_room(course_id):
    course = Courses.query.get(course_id)
    # If session_filtered is None, then render unactivated html, otherwise, redirect to the session
    # TODO replace with constants
    # status 0 is unactive, status 1 is active
    if (course.status == 0): # If no sessions are currently active
        return render_template('unactivated.html', course=course) # Render the unactivated html page
    else:
        session_filtered = Session.query.filter_by(course_id=course_id).filter_by(timestamp_end=None).first() # Session that is currently active
        return redirect(url_for('sessions', session_id=session_filtered.id))     





# Attendance 
# @app.route('/classes/course/session/<session_id>/attendance', methods=["GET", "POST"]) 
@login_required 
def attendance(session_id):
    session = Session.query.get(session_id)
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    signups = Signups.query.filter_by(course=course_id) # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(session_id=session_id) # List of reactions that happened in this specific course, specific session
    # speeds_specific = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5) # Speeds filtered out by the course ID and by the reaction number
    present_set = set()
    absent_set = set()
    for r in reactions_specific: 
        if (r.reactor.role == 1):
            present_set.add(r.reactor.username) # Then add to the present list
    for signup in signups: # Going through the list of signups
        if (signup.student.username not in present_set and signup.student.role == 1):
            absent_set.add(signup.student.username)

    return render_template('attendance.html', course=course,
                                            session=session, 
                                            present_set=present_set, 
                                            absent_set=absent_set, 
                                            title=course.course_name)
    

# Method to activate class
@app.route('/classes/rooms/<course_id>/activate', methods=["GET", "POST"]) # POST method, important declaration
@login_required
def activate(course_id):
    course = Courses.query.filter_by(id=course_id).first_or_404()
    if (current_user.id == course.teacher_id and course.status != 1):
        session = Session(course_id=course_id)
        course.status = 1
        db.session.add(course)
        db.session.add(session)
        db.session.commit() 
    return redirect(url_for('course_waiting_room', course_id=course.id))

# Method to end class
@app.route('/classes/rooms/<course_id>/<session_id>/end', methods=["GET", "POST"]) # POST method, important declaration
@login_required
def end(course_id, session_id):
    course = Courses.query.get(course_id)
    session = Session.query.get(session_id) # Getting the correct session
    
    session.timestamp_end = datetime.utcnow() # Setting the end timestamp for the session
    course.status = 0 # Setting course status to 0 (unactivated)
    db.session.add(course)
    db.session.add(session)
    db.session.commit()

    return redirect(url_for('course_waiting_room', course_id=course.id))

# Function for all the emotions and speeds
@app.route('/classes/course/session/<session_id>/react/<reaction_num>', methods=["GET", "POST"]) # Adds an emotion, also don't forget to add this methods POST thing!
@login_required
def submit_reaction(session_id, reaction_num):
    session = Session.query.get(session_id)
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    reaction = Reactions(user_id=current_user.id, reactions=reaction_num, reactions_course_id=course_id, session_id=session_id) # This is the user's reaction based on the button pressed
    db.session.add(reaction)
    db.session.commit() 
    return redirect(url_for('sessions', session_id=session_id)) # Redirects to the room page



# Fetch Session json (includes reactions, speeds, attendance, percentage, speed num, and course status)
@app.route('/classes/course/session/<session_id>/session_json', methods=["GET", "POST"])
@login_required
def session_json(session_id):
    # Emotions, speeds, attendance, course status
    time_ago = datetime.utcnow()-timedelta(minutes=5) # Gets the time 5 minutes ago
    reactions = Reactions.query.filter_by(session_id=session_id).all() # Only show the reactions for this specific course's session
    reactions_time_filtered = Reactions.query.filter_by(session_id=session_id).filter(Reactions.timestamp > time_ago).all() # Filtered by time
    reaction_list = []
    speed_list = []
    attendance_list = []
    for r in reactions:
        if (r.reactions <= 5): # Then it is an emotion, add to emotion dictionary
            emotions_dict = {
                "reactions_id": r.id,
                "user_id": r.reactor.username,
                "emotions": r.reactions,
                "reactions_course_id": r.reactions_course_id, 
                "emotions_timetamp": r.timestamp
            }
            reaction_list.append(emotions_dict)
    for r in reactions_time_filtered:
        if (r.reactions > 5): # Then it is a speed, add to speed dictionary
            speed_dict = {
                "reactions_id": r.id, 
                "user_id": r.reactor.username,
                "speed": r.reactions,
                "reactions_course_id": r.reactions_course_id,
                "speed_timestamp": r.timestamp
            }
            speed_list.append(speed_dict)

    # To get the attendance information
    session = Session.query.get(session_id)
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    signups = Signups.query.filter_by(course=course_id) # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(session_id=session_id) # List of reactions that happened in this specific course, specific session
    # speeds_specific = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5) # Speeds filtered out by the course ID and by the reaction number
    present_set = set()
    absent_set = set()
    present_list = list()
    absent_list = list()
    for r in reactions_specific: 
        if (r.reactor.role == 1):
            present_set.add(r.reactor.username) # Then add to the present list
    for signup in signups: # Going through the list of signups
        if (signup.student.username not in present_set and signup.student.role == 1):
            absent_set.add(signup.student.username)
    
    present_list = present_set
    absent_list = absent_set
    converted_dict_present = {
        "Present": list(present_list)  
    }
    attendance_list.append(converted_dict_present)
    
    converted_dict_absent = {
        "Absent": list(absent_list)
    }
    attendance_list.append(converted_dict_absent)

    # Percentage of happiness FIX THIS RIP
    reactions = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions < 6) # All the emotions for this specific room, no speeds
    print("HELLO")
    
    percent_happy = "No reactions, no percentage"
    size = 0
    for reaction in reactions:
        size += 1
    if size > 0:
        happy = 0
        for r in reactions:
            if r.reactions == 0:
                happy += 1
        percent_happy = (happy/size) * 100
        
    # To determine the speed number
    
    #print(datetime.utcnow()-timedelta(minutes=5))
    
    speed_filtered = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5).filter(Reactions.timestamp > time_ago).all() # Speeds filtered out by the session ID and by the reaction number
    faster = 0
    slower = 0
    speed_number = 0
    calculated_number = 0
    for s in speed_filtered:
        if s.reactions == 6: # Faster request
            faster += 1
        else: # Slower request
            slower += 1
    total = slower + faster
    if total != 0:
        calculated_number = (faster/total) * 100 
    if calculated_number >= 91:
        speed_number = 10
    elif calculated_number >= 81:
        speed_number = 9
    elif calculated_number >= 71:
        speed_number = 8
    elif calculated_number >= 61:
        speed_number = 7
    elif calculated_number >= 51:
        speed_number = 6
    elif calculated_number >= 41:
        speed_number = 0 # Nothing will be shown at this point
    elif calculated_number >= 31:
        speed_number = 1
    elif calculated_number >= 21:
        speed_number = 2
    elif calculated_number >= 11:
        speed_number = 3
    elif calculated_number >= 1: # Smaller the number is, the slower the class should be 
        speed_number = 4
    else:
        speed_number = 5
        if total == 0: # No speeds have been selected yet
            speed_number = 0

    # To get course status information
    if (session.timestamp_end is None):
        course_status = 1 # The session is still active
    else:
        course_status = 0 # The session is over

    result = {
        "reactions": reaction_list, 
        "speeds": speed_list,
        "attendance": attendance_list, 
        "course_status": course_status,
        "percentage": percent_happy,    
        "speed_num": speed_number,
        "speed_percentage": calculated_number  
    }
    return jsonify(result)


# Fetch course status (active or inactive) json
@app.route('/classes/course/<course_id>/course_status_json', methods=["GET", "POST"])
@login_required
def course_status(course_id): 
    course = Courses.query.get(course_id)
    return jsonify({"status": course.status})

# Shows the list of previous sessions
@app.route('/classes/course/<course_id>/previous_session_list')
@login_required
def previous_session_list(course_id):
    sessions = Session.query.filter_by(course_id=course_id).filter(Session.timestamp_end!=None).all() # This is all the sessions for that course id that are inactive
    return render_template('previous_session_list.html', course_id=course_id, sessions=sessions)
    # Inside of the HTML page, there are links that will show the specific info for that session
    # Create a new route to the rendered page

# Directs to the previous session data pages
@app.route('/classes/course/<course_id>/previous_session_data/<session_id>')
@login_required
def previous_session_data(course_id, session_id):
    session = Session.query.get(session_id)
    
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    signups = Signups.query.filter_by(course=course_id) # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(session_id=session_id) # List of reactions that happened in this specific course, specific session
    speeds_specific = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5) # Speeds filtered out by the course ID and by the reaction number
    present_set = set()
    absent_set = set()
    for r in reactions_specific: 
        if (r.reactor.role == 1): # If the reactor is a student
            present_set.add(r.reactor.username) # Then add to the present list
    for signup in signups: # Going through the list of signups
        if (signup.student.username not in present_set and signup.student.role == 1):
            absent_set.add(signup.student.username)
    
    return render_template('previous_session_data.html', course=course,
                                        reactions_specific=reactions_specific,
                                        speeds_specific=speeds_specific,
                                        session=session,
                                        session_id=session_id,
                                        present_list=list(present_set), 
                                        absent_list=list(absent_set), 
                                        title=course.course_name + " Session " + session_id) 

# Just so I can see all the databases
@app.route('/database') 
def database():
    user_all = User.query.all() # All the users are stored in this variable, to be used in the HTML 
    reactions_all = Reactions.query.all()
    courses_all = Courses.query.all()
    signups_all = Signups.query.all()
    session_all = Session.query.all()
    #user_signups = User.query.join(Signups, (Signups.user_id == User.id)) 
    user_signups = User.query.join(Signups, (Signups.user_id == User.id)).join(Courses, (Courses.id == Signups.course)) 
    return render_template('database.html', user_all=user_all, reactions_all=reactions_all, courses_all=courses_all, session_all=session_all, signups_all=signups_all, user_signups=user_signups, title='Database') # Have to pass in your variables above in here

# Testing javascript image reload
@app.route('/image-reload')
def reload():
    return render_template('image-reload.html', title="Image Reload") 