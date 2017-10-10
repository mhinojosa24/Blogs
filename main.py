from flask import Flask, request, render_template, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:max1234@localhost:2222/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'hdhdhfa;h;uahehhffaf'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)  
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref="owner")

    def __init__(self, email, password):
        self.email = email
        self.password = password 

def check_valid( item ):
    message = ''
    if len(item)<3 or len(item)>20 or ' ' in item:
        message = "This must be between 3-20 characters and have no spaces."
    return message


def check_loggedin( sess ):

    if 'username' in sess:

        return True

    return False

# routes 

@app.before_request
def verify_logged_in():
    accessible = ['index', 'login', 'register']
    
    if request.endpoint not in accessible and not check_loggedin(session):
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users, loggedin=check_loggedin(session), page_headers="All users")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == passsword:
            session['email'] = email
            return redirect('/blog?user='+user.id)    
        else:
            return '<h1>This account does not exist!</h1>'

        # if user
    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        email_error = check_valid(email)
        password_error = check_valid(password)
        verify_password_error = check_valid(password)

        if password != verify_password: verify_password_error = "Password and verify password do not match"
        if not username_error and not password_error and not verify_password_error:

            existing_user = User.query.filter_by( email=email ).first()

        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()

            sessiom['email'] = new_user.email

            return redirect('/blog?user='+str(new_user.id))
        else:
            email_error = "This email already exists."
            return render_template('register.html', loggedin=check_loggedin(session), page_header="Register", email = email, email_error=email_error)
    
        return render_template('register.html',  loggedin=check_loggedin(session), page_header="Register", email = email, user_name_error = username_error, password_error = password_error, verify_password_error = verify_password_error)
    return render_template('register.html', loggedin=check_loggedin(session), page_header="Register")


        
@app.route('/blog')
def blog():
    get_blog_id = request.args.get('id')
    get_user_id = request.args.get('user')
    blogs = Blog.query.all()
    if get_blog_id: 
        blog_id = int(get_blog_id)
        this_blog = Blog.query.get( blog_id )
        if this_blog:
            return render_template('indiv_blog.html', loggedin=check_loggedin(session), page_header=this_blog.title, blog=this_blog)
        else:
            return render_template('no_blogs.html', loggedin=check_loggedin(session), page_header="Blog Not Found")
 
    if get_user_id:
        user = User.query.get( int(get_user_id) )
        blogs = user.blogs
    return render_template('/blogs.html', loggedin=check_loggedin(session), page_header="All Blogs", blogs=blogs)

@app.route('/blog_form', methods=['GET', 'POST'])
def blog_form():

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        title_error, body_error = "", ""

        if not title: title_error = "Please put a title"
        if not body: body_error = "Please put a body"

        if not title_error and not body_error:
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()

            return redirect('/blog?id='+str(new_blog.id))

        else:
            return render_template('/blog_form.html', 
                                    page_header="Create a new Blog", 
                                    title_error=title_error, 
                                    body_error=body_error,
                                    title=title,
                                    body=body)
    
    return render_template('blog_form.html', loggedin=check_loggedin(session))

#ending code ------->

if __name__ == "__main__":
    app.run()