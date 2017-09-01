from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import string
from hashutils import make_pwd_hash, check_pwd_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:YES@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='lc202!*&'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pwd_hash(password)
        
@app.route('/index', methods=['POST', 'GET'])
def index():
    allusers = User.query.all()
    return render_template('index.html', allusers = allusers)
    

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('user')

    if blog_id:
        thisblog = Blog.query.get(blog_id)
        return render_template('newblog.html', blog=thisblog)

    if user_id:
        thisuser = User.query.get(user_id)
        return render_template('singleUser.html', user=thisuser)

    all_posts = Blog.query.all()
    return render_template('blog.html', blogs=all_posts)

    
        


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        pw_hash = user.pw_hash
       
        if user and pw_hash != check_pwd_hash(password, user.pw_hash):
            error = "Please enter a valid password"
            return render_template('login.html', error=error)

        if user and pw_hash == check_pwd_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')
        else:
            error = "Username does not exist. Please try again!"

    return render_template('login.html', error=error)

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        error = ''
        
        if username == '' or password == '' or verify == '':
            error = 'One or more fields are empty'

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error= 'Username already exists. Please try again!'

        if password != verify:
            error = 'Passwords do not match'

        if len(password)<3 or len(username)<3:
            error = 'Too short. More than 3 characters please!'    
            
        if not existing_user and not error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
        else:
            return render_template('signup.html', error=error)
      
    return render_template('signup.html', error=error)

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    if request.method == 'GET':
        return render_template('newpost.html')

    if request.method == 'POST':
        name_error = ''
        body_error = ''
        blog_name = request.form['title']
        blog_body = request.form['body']

        if len(blog_name) is 0:
            name_error= "Please enter a blog title"
            
        if len(blog_body) is 0:
            body_error= "Please enter a blog"
         
        if not name_error and not body_error:
            user = User.query.filter_by(username=session['username']).first()
            new_blog = Blog(request.form['title'],request.form['body'], user)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id='+str(new_blog.id))
        else:
            return render_template('newpost.html', name_error=name_error, body_error=body_error)

# @app.route('/newblog', methods=['GET', 'POST'])
# def newblog():
#     blog_id = request.args.get('id')
#     current_user = User.query.filter_by(username=session['username']).first()
#     current_blog = Blog.query.get(blog_id)
#     return redirect('./blog?id={{blog_id.id}}', blog=current_blog , user=current_user.username)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
    

if __name__ == '__main__':
    app.run()
