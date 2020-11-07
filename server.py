from flask import Flask, render_template, redirect, url_for, flash, request, g
from flask_mail import Mail, Message
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.types import TIMESTAMP
from flask_bcrypt import check_password_hash, generate_password_hash
from os import urandom, environ
from datetime import datetime
from smtplib import SMTP
from email.message import EmailMessage
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.secret_key = urandom(16)
mail = Mail()
mail.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///./database.sqlite'
db = SQLAlchemy(app)

class Category(db.Model):
    name = db.Column(db.String, primary_key=True)
    videos = relationship('Video', secondary='link')
    def __repr__(self):
        return '<Category %r>' % self.name
class Video(db.Model):
    link = db.Column(db.String, primary_key=True)
    categories = relationship(Category, secondary='link')
    def __repr__(self):
        return '<Video %r>' % self.link
class LinkVideoCategory(db.Model):
    __tablename__ = 'link'
    category_name = db.Column(db.Integer, db.ForeignKey('category.name'), primary_key = True)
    video_link = db.Column(db.Integer, db.ForeignKey('video.link'), primary_key = True)

class User(db.Model):
    """A user capable of viewing reports.

    :param str name: name address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'user'

    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, primary_key=True)
    authenticated = db.Column(db.Boolean, default=False)
    admin = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the name address to satisfy Flask-Login's requirements."""
        return self.name

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

    def __repr__(self):
        return '<User %r>' % self.name

#class RegisterRequests(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    email = db.Column(db.String, nullable=False)
#    request_time = db.Column('timestamp', TIMESTAMP(timezone=False),
#                             nullable=False, default=datetime.now())

db.create_all()
if User.query.filter_by(admin=True).first() == None:
    db.session.add(User(name='admin', password=generate_password_hash('secret', 10),
                        admin=True, email='brahim.pro@protonmail.com'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.before_request
def load_logged_in_user():
    g.current_user = current_user

def getVideoByCategory(category):
    return list(query.Video.link for query in db.session.query(Category, Video).filter(LinkVideoCategory.category_name == Category.name, LinkVideoCategory.video_link == Video.link, Category.name == category).all())

@app.route('/index.html')
def inedx():
    return redirect(url_for('default'))
@app.route('/')
def default():
    categories = Category.query.all()
    m = {}
    for category in categories:
        m[category.name] = getVideoByCategory(category.name)
    return render_template("index.html", categories=m)

@app.route("/logout.html", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template("/index.html")

@app.route('/login.html', methods=['POST'])
def login():
    if request.method == "POST":
        user = User.query.get(request.form.get('username'))
        if user and check_password_hash(user.password, form.password.data):
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            if user.admin: return redirect(url_for("admin"))
            return redirect(url_for("default"))
    return render_template('/login.html', form=form)

@app.route('/register.html/<id>')
def register(id):
    return "Registration page"

@app.route('/register.html', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        db.session.add(User(name=request.form.get('name'), password=generate_password_hash(request.form.get('password'), 10),
            admin=False, email='brahim.pro@protonmail.com'))
        db.session.commit()
        #register_request = RegisterRequests(email=request.form.get('email').data)
        #db.session.add(register_request)
        #db.session.commit()
        #link = request.url_root + 'register.html/' + str(register_request.id)
        #message = "Cliquer sur le lien pour vous enregistrer dans la plateforme de Amel Ben Brahim\r\n" + link
        #send_mail(form.email.data, "Email d'enregistrement au service en ligne d'Amel Ben Brahim",
        #          message)
    return render_template('register.html')

def send_mail(receiver, subject, body):
    app.logger.info("Instantiating SMTP server")
    with SMTP('smtp.gmail.com:587', timeout=5) as server:
        app.logger.info("EHLO")
        server.ehlo()
        app.logger.info("Start TLS")
        server.starttls()
        app.logger.info("EHLO")
        server.ehlo()
        app.logger.info("Logging to SMTP server")
        server.login('brahimalekhine@gmail.com', 'alekhinebrahim')
        email = EmailMessage()
        email.set_content(body)
        email['From'] = 'noreply@ortonabeul.tn'
        email['To'] = receiver
        email['Subject'] = subject
        message = f"Subject: {subject}\n\n{body}"
        app.logger.info("Sending email")
        server.send_message(email)

@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            message = 'Nom: %s\r\nEmail: %s\r\n %s' % (form.name.data, form.email.data, form.message.data)
            send_mail("brahim.pro@protonmail.com", request.form['subject'], message)
            flash("Message envoyé", "success")
        except Exception as e:
            app.logger.error(str(e))
            flash("Une erreur technique est survenue, veuillez contacter le cabinet par téléphone", "danger")
    return render_template('contact.html', form=form)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(host='0.0.0.0')
