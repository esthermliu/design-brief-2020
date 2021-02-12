from datetime import datetime
from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

class User(UserMixin, db.Model):
    # columns of the database
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True) # adding columns to the database
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Integer, index=False, unique=False) # 0 is Teacher, 1 is Student
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic') # First part is calling it from the Post model, secret field is the backref (author)
    reactions = db.relationship('Reactions', backref='reactor', lazy='dynamic') # This will show all the reactions that this user has made
    teaches = db.relationship('Courses', backref='teacher', lazy='dynamic') # This will show all the courses that the user teaches
    signups = db.relationship('Signups', backref='student', lazy='dynamic') # This will show all of the signups of that user
    #speed = db.relationship('Speed', backref='speeder', lazy='dynamic') # This will show all the speed complaints of that user
    responses = db.relationship('Responses', backref='student_responder', lazy='dynamic') # This will show all the responses of that user
    prompts = db.relationship('Prompts', backref='teacher_prompter', lazy='dynamic') # This will show all forms of that teacher

    def __repr__(self):
        return '<User {} {}>'.format(self.username, self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size) 

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Taking the user ID from the user model, using backref of author will show you the actual user

    def __repr__(self):
        return '<Post {} {}>'.format(self.body, self.timestamp)
 
@login.user_loader
def load_user(id): 
        return User.query.get(int(id))

class Reactions(db.Model): # A base class for all models from Flask SQLAlchemy
    id = db.Column(db.Integer, primary_key=True) # every new database should have an ID so it knows how to organize the info passed in
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Taking the user ID from the user model, using the backref of reactor will show you the actual user
    reactions = db.Column(db.Integer, index=False, unique=False) # Creating a new column in the database for emotions. Not unique and not indexable 
    reactions_course_id = db.Column(db.Integer, db.ForeignKey('courses.id')) # Using backref of course_actual will show you the actual course
    session_id = db.Column(db.Integer, db.ForeignKey('session.id')) # Using backref actual_session of will show you the actual session, e.g. <Session>
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # Timestamp
    #speed = db.Column(db.Integer, index=False, unique=False) # Creating a new column in the database for speed, will put in separate table actually

    def __repr__(self):
        return '<Reaction {} {} {} {} {}>'.format(self.id, self.user_id, self.reactions, self.reactions_course_id, self.timestamp)

class Responses(db.Model):
    id = db.Column(db.Integer, primary_key=True) # every new database should have an ID so it knows how to organize the info passed in
    student_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Taking the user ID from the user model, using the backref of student_responder will show you the actual user
    form_prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id')) # Using the backref of responder will show the actual prompt
    form_responses = db.Column(db.Integer, index=False, unique=False) # Creating a new column in the database for responses. Not unique and not indexable 
    form_course_id = db.Column(db.Integer, db.ForeignKey('courses.id')) # Using backref of course_response will show you the actual course
    session_id = db.Column(db.Integer, db.ForeignKey('session.id')) # Using backref actual_session of will show you the actual session, e.g. <Session>
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # Timestamp

    def __repr__(self):
        return '<Response {} {} {} {} {} {} {}>'.format(self.id, self.student_id, self.form_prompt_id, self.form_responses, self.form_course_id, self.session_id, self.timestamp)

class Prompts(db.Model):
    id = db.Column(db.Integer, primary_key=True) # every new database should have an ID so it knows how to organize the info passed in
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Taking the user ID from the user model, using the backref of teacher_prompter will show you the actual user
    form_question = db.Column(db.String(140))
    responses = db.relationship('Responses', backref='responder', lazy='dynamic') # This will show all responses to this form
    form_course_id = db.Column(db.Integer, db.ForeignKey('courses.id')) # Using backref of course_form will show you the actual course
    session_id = db.Column(db.Integer, db.ForeignKey('session.id')) # Using backref actual_session of will show you the actual session, e.g. <Session>
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # Timestamp

    def __repr__(self):
        return '<Prompt {} {} {} {} {} {}>'.format(self.id, self.teacher_id, self.form_question, self.form_course_id, self.session_id, self.timestamp)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id')) # Using the backref of session_course_id will show you the actual course
    timestamp_start = db.Column(db.DateTime, index=True, default=datetime.utcnow) # Timestamp of the class starting
    timestamp_end = db.Column(db.DateTime, index=True) # Timestamp of the class ending
    reactions = db.relationship('Reactions', backref='actual_session', lazy='dynamic') # This will show all the reactions for that session
    forms = db.relationship('Prompts', backref='session_form', lazy='dynamic') # This will show you all of the forms of the session   
    responses = db.relationship('Responses', backref='session_response', lazy='dynamic') # This will show you all of the responses of the session
    
    def __repr__(self):
        return '<Session {} {} {} {}>'.format(self.id, self.course_id, self.timestamp_start, self.timestamp_end)

class Courses(db.Model): 
    id = db.Column(db.Integer, primary_key=True) # Always need ID
    course_name = db.Column(db.String(140), index=False, unique=False) # Not indexable or unique bc many people can have the same course
    code = db.Column(db.Integer, index=True, unique=True) # Indexable to link it back to the course name
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # Timestamp
    status = db.Column(db.Integer, index=False, unique=False, default=0) # 0 means the class is inactive, 1 is active
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Taking the user ID from the user model, using backref of teacher will show you the actual teacher
    icon = db.Column(db.String(220), index=False, unique=False, default="/static/images/Turtle.gif") # Icon option, turtle gif is set as the default 
    signups = db.relationship('Signups', backref='course_id', lazy='dynamic') # This will show all the student signups for this course
    reactions = db.relationship('Reactions', backref='course_actual', lazy='dynamic') # This will show all the reactions for this course
    #speed = db.relationship('Speed', backref='course_s', lazy='dynamic') # This will show all the speed complaints for this course 
    session = db.relationship('Session', backref='session_course_id', lazy='dynamic') # This will show you all the sessions of the course
    forms = db.relationship('Prompts', backref='course_form', lazy='dynamic') # This will show you all of the forms of the course
    responses = db.relationship('Responses', backref='course_response', lazy='dynamic') # This will show you all of the responses of the course

    def __repr__(self):
        return '<Courses {} {} {} {} {} {}>'.format(self.id, self.course_name, self.code, self.teacher_id, self.status, self.timestamp)


class Signups(db.Model):
    id = db.Column(db.Integer, primary_key=True) # Always need ID
    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) # Using the backref student will show you the actual student who signed up, inside of the foreign key should be lowercase
    course = db.Column(db.Integer, db.ForeignKey('courses.id')) # Using the backref course_id will show you the actual id of the course
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow) # Timestamp

    def __repr__(self):
        return '<Signups {} {} {} {}>'.format(self.id, self.user_id, self.course, self.timestamp)