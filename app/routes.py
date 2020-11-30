from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = { 'username': 'Bob'}
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

    bob = { "bob": "hello"}
    return render_template('index.html', title="Home", user=user, posts=posts, bob=bob)