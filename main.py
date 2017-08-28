from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import string

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:LAILA@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))


    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=['POST', 'GET'])
def index():

    blog_id = request.args.get('id')
    if blog_id == None:
        new_post = Blog.query.all()
        return render_template('blog.html', new_post=new_post)
    else:
        newblog = Blog.query.get(blog_id)
        return render_template('newblog.html', newblog=newblog)
    
        

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
            new_blog= Blog(request.form['title'], request.form['body'])
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id='+str(new_blog.id))
        else:
            return render_template('newpost.html', name_error=name_error, body_error=body_error)

@app.route('/newblog', methods=['POST'])
def newblog():
    blog_id = request.args.get('id')
    if request.method == 'POST':
        return redirect('./blog?id={{Blog.id}}')

if __name__ == '__main__':
    app.run()
