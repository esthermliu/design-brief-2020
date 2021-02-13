from flask import render_template, flash, redirect, url_for, jsonify, send_file
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import EditProfileForm, TeacherRadioForm, StudentRadioForm, EditClassForm
from flask_login import current_user, login_user
from app.models import User, Reactions, Post, Courses, Signups, Session, Responses, Prompts
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
import random 
from datetime import datetime, timedelta
from dateutil import tz
from collections import defaultdict
#from flask_weasyprint import HTML, render_pdf

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

def unauthorized_access(error_message=""):
    flash('Unauthorized access.\n{}'.format(error_message), 'error')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: # If the current user is already logged in 
        return redirect(url_for('classes', username=current_user.username)) # Then direct the user to their classes page
    form = LoginForm() # Takes in the login form
    if form.validate_on_submit(): # If the form is validated
        user = User.query.filter_by(username=form.username.data).first() # Get the correct user from the database
        if user is None or not user.check_password(form.password.data): # If the user does not exist or the user's password is not the same as the password in the form
            flash('Invalid username or password', 'error') # Flash an invalid username/password message
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
        flash('Congratulations, you are now a registered user!', 'info')
        return redirect(url_for('login'))
    else:
        print("\n\nInvalid form!", form.errors)
    print("role", form.role)
    print("label", form.role.label)
    return render_template('register.html', title='Register', form=form)

# Page to create a new class as a teacher
@app.route('/user/<username>/create_class') 
@login_required # Have to be logged in as a teacher for this to work
def create(username):
    if User.query.filter_by(username=username).first().role == 1:
        flash('You must be a teacher to create classes', 'error')
        return redirect(url_for('index'))
    t_courses_all = Courses.query.filter_by(teacher_id=current_user.id) # All of that teacher's courses   
    # return render_template('create_class.html', t_courses_all=t_courses_all, title="Create a Class")
    return render_template('create_class.html', t_courses_all=t_courses_all, title="Create a Class")

# Adds the new course to the database 
@app.route('/user/<username>/create_class/new', methods=["POST"]) # This is a POST method
@login_required 
def newclass(username):
    course_name = request.form.get("course_name") # getting the course name from the form
    print("!!! " + username)
    print("CU id is %s but user id is %s" % (current_user.id, User.query.filter_by(username=username).first().id))
    if current_user.id != User.query.filter_by(username=username).first().id:
        return unauthorized_access()
    if len(course_name) == 0:
        flash('You must give your new course a name', 'error')
        return redirect(url_for('create', username=current_user.username)) # Redirects to the create page
    course_icon = request.form.get("icon") # getting the course icon from the form
    course_color = request.form.get("color") # getting the course color from the form
    rand_code = random.randint(100000, 999999) # Generating a random code
    exist_course = Courses.query.filter_by(code=rand_code).first() # Checks if rand_code is already linked to an existing course
    while exist_course is not None: # While an existing course has that code
        rand_code = random.randint(100000, 999999) # Generate a random code again
        exist_course = Courses.query.filter_by(code=rand_code).first() # Check the database again
    new_course = Courses(course_name=course_name, code=rand_code, teacher_id=current_user.id, icon=course_icon, color=course_color)
    db.session.add(new_course)
    db.session.commit()
    flash('Congratulations! You have successfully created a new course.', 'info')
    return redirect(url_for('classes', username=current_user.username)) # Redirects to the create page

@app.route('/user/<username>') # User profile page
@login_required
def user(username):
    if current_user.id == User.query.filter_by(username=username).first():
        return unauthorized_access()
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
        flash('Your changes have been saved', 'info')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET': # If this is the first time that the form has been requested
        form.username.data = current_user.username # Then pre-populate the fields with the data in the database
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, title="Edit Profile")


@app.route('/user/<username>/classes') # User's classes
@login_required
def classes(username): # the word after def has to be the same as the text in the urlfor quotation marks 
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.id != user.id:
        return unauthorized_access()
    user_signups_filtered = User.query.join(Signups, (Signups.user_id == User.id)).\
                                        join(Courses, (Courses.id == Signups.course)).\
                                        with_entities(Signups).\
                                        filter(Signups.user_id == user.id)
    print(x + "\n" for x in user_signups_filtered)
    teacher_courses = Courses.query.filter_by(teacher_id=user.id).all()
    return render_template('classes.html', user=user,
                                             user_signups_filtered=user_signups_filtered, 
                                             teacher_courses=teacher_courses, 
                                             title="Classes")

# Add a new class
@app.route('/user/<username>/classes/add', methods=["POST"]) # This is a POST method
@login_required
def add(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.id != user.id:
        return unauthorized_access()
    code = request.form.get("title") # This stores the user code that the student enters
    course = Courses.query.filter_by(code=code).first() # Filter through courses by this code
    if course is None:
        flash('The code you entered (%s) is invalid. Try again' % (code), 'error')
        return redirect(url_for('classes', username=user.username)) 
        
    new_signup = Signups(user_id = user.id, course=course.id) # Now that you have that course, take the course id and enter that into the course field
    # TODO: Remove this for loop later by querying with a filter and checking if none
    signups_all = Signups.query.all() # Getting all of the sign-ups
    already = False
    for s in signups_all:
        if new_signup.user_id == s.user_id and new_signup.course == s.course:
            already = True
            flash('You have already enrolled in this course. Nice try.', 'error')
    if already == False:
        db.session.add(new_signup)
        db.session.commit()
    return redirect(url_for('classes', username=user.username))





# Route for each session
@app.route('/classes/course/session/<session_id>') # The text inside the <> has to be the same as the parameter in the def room()
@login_required # Have to be logged in to see these rooms
def sessions(session_id):
    session = Session.query.get(session_id)
    
    # If the session has ended, then redirect
    if (session.timestamp_end is not None):
        return redirect(url_for('course_waiting_room', course_id=session.course_id))

    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    signups = Signups.query.filter_by(course=course_id).all() # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(session_id=session_id).all() # List of reactions that happened in this specific course, specific session
    # speeds_specific = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5) # Speeds filtered out by the course ID and by the reaction number
    present_set = set()
    absent_set = set()
    for r in reactions_specific: 
        if (r.reactor.role == 1): # If the reactor is a student
            present_set.add(r.reactor.username) # Then add to the present list
    for signup in signups: # Going through the list of signups
        if (signup.student.username not in present_set and signup.student.role == 1):
            absent_set.add(signup.student.username)

    forms_all = Prompts.query.filter_by(session_id=session_id).all() # getting all the forms in the session
    forms_exist = False # first setting forms as not existing
    forms_first = Prompts.query.filter_by(session_id=session_id).first() # getting first form in the session

    if (forms_first != None): # if there is a form in the session
        forms_exist = True # then a form does exist
       
    latest_form = Prompts.query.order_by(Prompts.id.desc()).filter_by(session_id=session_id).first() # Gets you the latest form in that session

    
    return render_template('rooms.html', course=course,
                                        reactions_specific=reactions_specific,
                                        session=session,
                                        session_id=session_id,
                                        present_list=list(present_set), 
                                        absent_list=list(absent_set), 
                                        title=course.course_name,
                                        form=latest_form,
                                        forms_all=forms_all,
                                        forms_exist=forms_exist) 

# Course waiting room, if there is an active session, then redirect to session. Otherwise, redirect to unactivated html
@app.route('/classes/course/<course_id>')
@login_required
def course_waiting_room(course_id):
    course = Courses.query.get(course_id)
    # If session_filtered is None, then render unactivated html, otherwise, redirect to the session
    # TODO replace with constants
    # status 0 is unactive, status 1 is active
    if (course.status == 0): # If no sessions are currently active
        return render_template('unactivated.html', course=course, title=course.course_name +  " Waiting Room") # Render the unactivated html page
    else:
        session_filtered = Session.query.filter_by(course_id=course_id).filter_by(timestamp_end=None).first() # Session that is currently active
        return redirect(url_for('sessions', session_id=session_filtered.id))     


@app.route('/classes/course/<course_id>/manage', methods=['GET', 'POST'])
@login_required
def manage_course_page(course_id):
    course = Courses.query.get(course_id) # getting the correct course with the course_id
    teacher_id = course.teacher_id # getting the appropriate teacher_id
    if current_user.id != teacher_id: # If the current user's id is not the same as the teacher id
        return unauthorized_access("You are not the teacher for this class.") # return an error message
    
    student_signups = Signups.query.filter_by(course=course.id).all()
    # students_user_info = [User.query.get(s.user_id) for s in student_signups]
    
    form = EditClassForm() # Setting form to the edit class form

    if form.validate_on_submit(): # If the form successfully submitted
        course.course_name = form.class_name.data # Set the course name to what they entered in the form
        course.icon = form.class_icon.data # Set icon for course from the form
        course.color = form.class_color.data # Set color for course from the form
        db.session.commit() # Commit changes to the database
        flash('Your changes have been saved', 'info')
        return redirect(url_for('manage_course_page', course_id=course_id))
    elif request.method == 'GET': # If this is the first time that the form has been requested
        form.class_name.data = course.course_name # Then pre-populate the fields with the data in the database
        form.class_icon.data = course.icon
        form.class_color.data = course.color
    else:
        flash('Please fill in every section', 'error')
    
    return render_template('manage_class.html', 
                            course_name=course.course_name,
                            course_id=course_id, 
                            title='Manage ' + course.course_name,
                            form=form)

@app.route('/classes/course/<course_id>/manage/remove/<user_id>', methods=["POST"]) # POST method
@login_required
def remove(course_id, user_id):
    course = Courses.query.get(course_id) # gets the right course
    student_removed = Signups.query.filter_by(course=course_id, user_id=user_id).first() # getting the student that is removed

    db.session.delete(student_removed) # removing the student from the database
    db.session.commit()
    flash("Student removed", 'info')

    return redirect(url_for('manage_course_page', course_id=course_id))

@app.route('/classes/course/<course_id>/manage/course_json', methods=["GET", "POST"])
@login_required
def course_json(course_id):
    student_list=[]
    student_info={}

    course = Courses.query.get(course_id) # Gets the appropriate course
    signups = course.signups # Gets a list of all of the signups in the course

    for s in signups: # each s represents a <Signups>
        student_info = {
            "student_id": s.student.id,
            "username": s.student.username,
            "email": s.student.email
        }
        student_list.append(student_info)

    result = {
            "students": list(student_list)
        }
    return jsonify(result)


# Attendance 
# @app.route('/classes/course/session/<session_id>/attendance', methods=["GET", "POST"]) 
@login_required 
def attendance(session_id):
    session = Session.query.get(session_id)
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    signups = Signups.query.filter_by(course=course_id).all() # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(session_id=session_id).all() # List of reactions that happened in this specific course, specific session
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
    if current_user.id != course.teacher_id:
        return unauthorized_access()
    if course.status != 1:
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
    course = Courses.query.filter_by(id=course_id).first_or_404()
    if current_user.id != course.teacher_id:
        return unauthorized_access()
    
    session = Session.query.get(session_id) # Getting the correct session
    session.timestamp_end = datetime.utcnow() # Setting the end timestamp for the session
    course.status = 0 # Setting course status to 0 (unactivated)
    db.session.add(course)
    db.session.add(session)
    db.session.commit()

    return redirect(url_for('course_waiting_room', course_id=course.id))

# To convert the utc times from the database to local times within python
def utc_to_local(utc_time):
    from_zone = tz.tzutc()
    to_zone = tz.gettz()

    out = utc_time.replace(tzinfo=from_zone)
    return out.astimezone(to_zone)

@app.route('/classes/course/session/<session_id>/report', methods=["GET", "POST"])
@login_required
def generate_report(session_id):

    # Get session info, course info, and teacher id for authorization verification
    session = Session.query.get(session_id)
    course_id = session.course_id
    course = Courses.query.get(course_id)
    teacher_id = course.teacher_id

    # Preventing unauthorized access to this report
    if teacher_id != current_user.id:
        return unauthorized_access("You are not the teacher for this class")
    
    course_name = course.course_name # Gets the string course name

    # get all the students signed up for this course
    students_all = Signups.query.filter_by(course=course_id).all()
    
    # create a dictionary mapping the students' user ids to their usernames for easy access later.
    ids_and_students = {student.user_id: User.query.get(student.user_id).username for student in students_all}

    # get all reactions for this session
    reactions_all = Reactions.query.filter_by(session_id=session_id).all()
    
    reaction_counts = {ids_and_students[s.user_id]:defaultdict(int) for s in students_all} # To store occurences of each reaction for each student

    attendance_present = set()
    attendance_absent = set()

    for r in reactions_all:
        s_id = r.user_id
        reaction_counts[ids_and_students[s_id]][r.reactions] += 1
        attendance_present.add(ids_and_students[s_id])

    for s in students_all:
        s_name = User.query.get(s.user_id).username
        if s_name not in attendance_present:
            attendance_absent.add(s_name)
    
    # converting the attendance sets to sorted lists
    attendance_absent = sorted(list(attendance_absent))
    attendance_present = sorted(list(attendance_present))

    full_start_info = utc_to_local(session.timestamp_start) # To avoid accessing twice for the start date and start time
    start_date = full_start_info.strftime("%A, %B %d, %Y")
    start_time = full_start_info.strftime("%I:%M %p")

    if session.timestamp_end is None:
        end_time = "In Progress"
    else:
        end_time = utc_to_local(session.timestamp_end).strftime("%I:%M %p")

    # renders the report template
    html = render_template('report.html',
                            title="{} Session Report: {}".format(course_name, session.timestamp_start.strftime("%A, %B %d, %Y")),
                            course_name=course_name, 
                            start_date=start_date,
                            start_time=start_time,
                            end_time=end_time,
                            session_id=session.id, 
                            present_list=attendance_present,
                            absent_list=attendance_absent,
                            reactions=sorted(reaction_counts.items())) # Sorts so that reactions are accessed in alphabetical order of students' usernames
    
    
    # renders the html as a pdf using weasyprint
    return render_pdf(HTML(string=html), stylesheets=[
                                                    'app/static/css/report.css',
                                                    "https://fonts.googleapis.com/css2?family=Montserrat&display=swap",
                                                    "https://fonts.googleapis.com/css2?family=Montserrat:wght@500&display=swap"])


# Function for all the emotions and speeds
@app.route('/classes/course/session/<session_id>/react/<reaction_num>', methods=["GET", "POST"]) # Adds an emotion, also don't forget to add this methods POST thing!
@login_required
def submit_reaction(session_id, reaction_num):
    session = Session.query.get(session_id)
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id
    student = Signups.query.filter_by(course=course_id, user_id=current_user.id).first()
    
    if student is None:
        return unauthorized_access("You are not in this class.")

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
    forms_list=[]

    for r in reactions:
        if (r.reactions <= 5): # Then it is an emotion, add to emotion dictionary
            emotions_dict = {
                "reactions_id": r.id,
                "user_id": r.reactor.username,
                "emotions": r.reactions,
                "reactions_course_id": r.reactions_course_id, 
                "emotions_timestamp": r.timestamp
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

    # To get the forms information
    forms_all = Prompts.query.filter_by(session_id=session_id).all() # Getting the entire list of forms for the session
    responses_all = Responses.query.filter_by(session_id=session_id).all()
    for f in forms_all:
        responses_list=[]
        responses_dict = {}
        responses_specific = Responses.query.filter_by(session_id=session_id, form_prompt_id=f.id).all() # These are the responses for each specific form
        for r in responses_specific:
            responses_dict = {
                "response_id": r.id,
                "student_id": r.student_responder.username,
                "form_prompt_id": r.form_prompt_id,
                "form_responses": r.form_responses,
                "form_course_id": r.form_course_id,
                "session_id": r.session_id,
                "timestamp": r.timestamp
            }
            responses_list.append(responses_dict)
        forms_dict = {
            "forms_id": f.id,
            "teacher_id": f.teacher_prompter.username,
            "form_question": f.form_question,
            "responses": responses_list,
            "form_course_id": f.form_course_id,
            "session_id": f.session_id,
            "timestamp": f.timestamp,
            "forms_url": url_for('form_response', session_id=f.session_id)
        }
        forms_list.append(forms_dict)


    # To get the attendance information
    session = Session.query.get(session_id)
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    signups = Signups.query.filter_by(course=course_id).all() # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(session_id=session_id).all() # List of reactions that happened in this specific course, specific session
    # speeds_specific = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5) # Speeds filtered out by the course ID and by the reaction number
    responses_specific = Responses.query.filter_by(session_id=session_id).all() # List of all the responses made for any forms in the session
    
    present_set = set()
    absent_set = set()
    present_list = list()
    absent_list = list()
    for r in reactions_specific: 
        if (r.reactor.role == 1):
            present_set.add(r.reactor.username) # Then add to the present list
    
    for response in responses_specific: # Goes through the list of responses made in the session and adds the student's username
        if (response.student_responder.role == 1): # Checking that the responder is indeed a student
            present_set.add(response.student_responder.username)

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
    reactions = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions < 6).all() # All the emotions for this specific room, no speeds
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
        "speed_percentage": calculated_number,
        "forms": forms_list  
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
    teacher_id = Courses.query.get(course_id).teacher_id
    if current_user.id != teacher_id:
        return unauthorized_access()
    sessions = Session.query.filter_by(course_id=course_id).filter(Session.timestamp_end!=None).all() # This is all the sessions for that course id that are inactive
    return render_template('previous_session_list.html', course_id=course_id, sessions=sessions, title="Previous Sessions")
    # Inside of the HTML page, there are links that will show the specific info for that session
    # Create a new route to the rendered page

# Directs to the previous session data pages
@app.route('/classes/course/<course_id>/previous_session_data/<session_id>')
@login_required
def previous_session_data(course_id, session_id):
    teacher_id = Courses.query.get(course_id).teacher_id
    if current_user.id != teacher_id:
        return unauthorized_access()
    
    session = Session.query.get(session_id)
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    signups = Signups.query.filter_by(course=course_id).all() # List of students that are in this specific course
    reactions_specific = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions<5).all() # List of reactions that happened in this specific course, specific session
    speeds_specific = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5).all() # Speeds filtered out by the course ID and by the reaction number
    present_set = set()
    absent_set = set()
    for r in reactions_specific: 
        if (r.reactor.role == 1): # If the reactor is a student
            present_set.add(r.reactor.username) # Then add to the present list
    for signup in signups: # Going through the list of signups
        if (signup.student.username not in present_set and signup.student.role == 1):
            absent_set.add(signup.student.username)

    # Getting the overall speed num
    speed_filtered = Reactions.query.filter_by(session_id=session_id).filter(Reactions.reactions>5).all() # Speeds filtered out by the session ID and by the reaction number
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

    
    return render_template('previous_session_data.html', course=course, 
                                        course_id=course_id,
                                        reactions_specific=reactions_specific,
                                        speeds_specific=speeds_specific,
                                        session=session,
                                        speed_number=speed_number,
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
    prompts_all = Prompts.query.all()
    responses_all = Responses.query.all()

    #user_signups = User.query.join(Signups, (Signups.user_id == User.id)) 
    user_signups = User.query.join(Signups, (Signups.user_id == User.id)).join(Courses, (Courses.id == Signups.course)) 
    return render_template('database.html', 
                            user_all=user_all, 
                            reactions_all=reactions_all, 
                            courses_all=courses_all, 
                            session_all=session_all, 
                            signups_all=signups_all, 
                            user_signups=user_signups, 
                            title='Database',
                            responses_all=responses_all,
                            prompts_all=prompts_all) # Have to pass in your variables above in here

# Testing javascript image reload
@app.route('/image-reload')
def reload():
    return render_template('image-reload.html', title="Image Reload") 

# creating forms
@app.route('/classes/course/session/<session_id>/create-form', methods=['GET', 'POST'])
@login_required
def create_form(session_id):
    form = TeacherRadioForm() # setting form to the TeaderRadioForm

    session = Session.query.get(session_id) # Get the correct session
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id
    teacher_id = Courses.query.get(course_id).teacher_id
    
    if current_user.id != teacher_id:
        return unauthorized_access()
    
    # If the session has ended, then redirect
    if (session.timestamp_end is not None):
        return redirect(url_for('course_waiting_room', course_id=session.course_id))


    if form.validate_on_submit():
        flash('Form has been successfully distributed', 'info')
        new_prompt = Prompts(teacher_id=current_user.id, form_question=form.prompt.data, form_course_id=course_id, session_id=session_id) # creating a new prompt from the information in the form
        db.session.add(new_prompt) # Adding and committing the new propmt to the database
        db.session.commit()
        return redirect(url_for('sessions', session_id=session_id))
    # else:
    #     flash('Error in form', 'error')
    return render_template('teacher_form.html', form=form, session_id=session_id, title='Create Form')

# student response to the form
@app.route('/classes/course/session/<session_id>/form-response', methods=['GET', 'POST'])
@login_required
def form_response(session_id):
    form = StudentRadioForm() # setting form to the TeaderRadioForm

    session = Session.query.get(session_id) # Get the correct session
    
    teacher_form = Prompts.query.order_by(Prompts.id.desc()).filter_by(session_id=session_id).first()
    prompt = teacher_form.form_question
    # If the session has ended, then redirect
    if (session.timestamp_end is not None):
        return redirect(url_for('course_waiting_room', course_id=session.course_id))

    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id

    if form.validate_on_submit():
        flash('Form has been successfully  submitted', 'info')
        new_response = Responses(student_id=current_user.id, form_prompt_id=teacher_form.id, form_responses=form.options.data, form_course_id=course_id, session_id=session_id) # creating a new prompt from the information in the form
        db.session.add(new_response) # Adding and committing the new propmt to the database
        db.session.commit()
        return redirect(url_for('sessions', session_id=session_id))

    return render_template('student_response.html', form=form, session_id=session_id, title='Form Response', prompt=prompt)

@app.route('/classes/course/session/<session_id>/form-data', methods=['GET', 'POST'])
@login_required
def form_data(session_id):
    session = Session.query.get(session_id) # Get the correct session
    course = session.session_course_id # This gives you the actual course
    course_id = session.course_id # This will give you the course id
    
    teacher_id = Courses.query.get(course_id).teacher_id
    if current_user.id != teacher_id:
        return unauthorized_access()

    return render_template('form_data.html', title="Form Data", session_id=session_id, course_id=course_id, course=course)