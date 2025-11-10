import os
import time
from datetime import datetime, timedelta 
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_mail import Mail, Message
from dotenv import load_dotenv
load_dotenv()
import secrets
import random 
from pathlib import Path
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'd56f6dc9c2c6a958b676fa420ee7bec15086e310b4f39177ea1a552c051b4567'
app.config['UPLOAD_FOLDER'] = '/tmp/profile_pics'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'krishna1290verma@gmail.com' 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
db_uri = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
bcrypt = Bcrypt(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    fullname = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=True) 
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    profile_image = db.Column(db.String(20), nullable=False, default='default.jpg')
    # --- FIX 1: Add image_version column for cache busting ---
    image_version = db.Column(db.Integer, default=1) 
    tasks = db.relationship('Task', backref='author', lazy=True)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)

class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False) 
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def save_picture(picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_fn)
    picture.save(picture_path)
    return picture_fn

def delete_picture(filename):
    if filename != 'default.jpg':
        picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(picture_path):
            os.remove(picture_path)

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow}

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/tasks', methods=['GET', 'POST'])
@login_required 
def tasks():
    if request.method == 'POST':
        task_content = request.form.get('content')
        due_date_str = request.form.get('due_date')
        due_date_obj = None
        if due_date_str:
            try:
                due_date_obj = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('tasks'))
        if task_content:
            new_task = Task(content=task_content, author=current_user, due_date=due_date_obj)
            db.session.add(new_task)
            db.session.commit()
            flash('Task added!', 'success')
        return redirect(url_for('tasks'))
    tasks = Task.query.filter_by(author=current_user).order_by(Task.id.desc()).all()
    return render_template('index.html', tasks=tasks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        plain_text_password = request.form.get('password')
        username = request.form.get('username')
        existing_user_email = User.query.filter_by(email=email).first()
        existing_user_username = User.query.filter_by(username=username).first()
        if existing_user_email:
            flash('That email is already taken. Please sign in.', 'danger')
            return redirect(url_for('login')) 
        if existing_user_username:
            flash('That username is already taken. Please choose another.', 'danger')
            return redirect(url_for('register')) 
        hashed_password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
        new_user = User(
            username=username, 
            fullname=fullname, 
            phone=phone, 
            email=email, 
            password=hashed_password, 
            profile_image='default.jpg',
            image_version=int(time.time()), # Initialize version on registration
        ) 
        db.session.add(new_user)
        db.session.commit()
        try:
            msg_title = f"Welcome to Task Management App, {new_user.username}!"
            sender = app.config.get('MAIL_USERNAME')
            msg = Message(msg_title, sender=sender, recipients=[new_user.email])
            msg.body = f"""
            Hello {new_user.fullname},
            Welcome aboard the Task Management System! 🎉
            Your account is now fully set up. You can log in using your registered username/email and password to start creating and tracking your tasks right away.
            We're excited to help you stay organized and productive!
            Best regards,
            The Task Management App Team
            """
            mail.send(msg)
        except Exception as e:
            print(f"WELCOME EMAIL FAILED: {e}")
        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('tasks'))
    if request.method == 'POST':
        login_identifier = request.form.get('login_identifier')
        password = request.form.get('password')
        next_page = request.args.get('next') 
        user = User.query.filter(
            (User.email == login_identifier) | (User.username == login_identifier)
        ).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.fullname}! You are now signed in.', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('Invalid username/email or password.', 'danger')
            return redirect(url_for('login')) 
    if not current_user.is_authenticated and request.args.get('next'):
        flash('Please sign in to access that page.', 'info') 
    return render_template('login.html') 

@app.route('/profile', methods=['GET']) 
@login_required
def profile():
    return render_template('profile.html')

@app.route('/update_profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if request.method == 'POST':
        if 'remove_photo' in request.form:
            if current_user.profile_image != 'default.jpg':
                delete_picture(current_user.profile_image)
                current_user.profile_image = 'default.jpg'
                # --- Update version when photo is removed too! ---
                current_user.image_version = int(time.time())
                db.session.commit()
                flash('Profile photo has been removed.', 'info')
            return redirect(url_for('update_profile')) 
        elif 'save_changes' in request.form:
            new_username = request.form.get('username')
            new_fullname = request.form.get('fullname')
            new_phone = request.form.get('phone')
            
            # --- Check and update username ---
            if new_username != current_user.username:
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    flash('That username is already taken. Please choose another.', 'danger')
                    return redirect(url_for('update_profile')) 
                current_user.username = new_username
                
            # --- Check and update profile picture ---
            if 'picture' in request.files and request.files['picture'].filename != '':
                delete_picture(current_user.profile_image) 
                picture = request.files['picture']
                filename = save_picture(picture)
                current_user.profile_image = filename 
                
                # --- FIX 2: Update the cache-busting version on new photo upload ---
                current_user.image_version = int(time.time())
                
            # --- Update other fields ---
            current_user.fullname = new_fullname
            current_user.phone = new_phone
            
            db.session.commit()
            flash('Your profile information has been updated successfully!', 'success')
            return redirect(url_for('profile'))
            
    return render_template('update_profile.html')

@app.route('/logout')
@login_required 
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    Task.query.filter_by(author=current_user).delete()
    delete_picture(current_user.profile_image)
    user_to_delete = User.query.get(current_user.id)
    logout_user()
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('Your account and all associated tasks have been permanently deleted.', 'info')
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
@login_required 
def delete_task(task_id):
    task_to_delete = Task.query.get_or_404(task_id)
    if task_to_delete.author != current_user:
        flash("You don't have permission to delete that task.", "danger")
        return redirect(url_for('tasks'))
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash('Task deleted!', 'success')
    except:
        flash('There was an issue deleting your task.', 'danger')
    return redirect(url_for('tasks'))

@app.route('/complete/<int:task_id>')
@login_required 
def complete_task(task_id):
    task_to_complete = Task.query.get_or_404(task_id)
    if task_to_complete.author != current_user:
        flash("You don't have permission to modify that task.", "danger")
        return redirect(url_for('tasks'))
    task_to_complete.completed = True
    try:
        db.session.commit()
        flash('Task marked as complete!', 'success')
    except:
        flash('There was an issue updating your task.', 'danger')
    return redirect(url_for('tasks'))

@app.route('/contact', methods=['GET', 'POST'])
@login_required 
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message_content = request.form.get('message')
        new_message = ContactMessage(name=name, email=email, message=message_content)
        db.session.add(new_message)
        db.session.commit()
        try:
            msg_title = "We've Received Your Message!"
            sender = app.config.get('MAIL_USERNAME')
            msg = Message(msg_title, sender=sender, recipients=[email]) 
            msg.body = f"""
            Hello {name},
            Thank you for contacting us at Task Tracker! 
            We have received your message and will get back to you as soon as possible.
            Your message:
            "{message_content}"
            Best,
            The Task Tracker Team
            """
            mail.send(msg)
        except Exception as e:
            print(f"CONTACT EMAIL FAILED: {e}")
            flash(f'Thank you, {name}! Your message has been saved (but confirmation email failed).', 'success')
            return redirect(url_for('contact'))
        flash(f'Thank you, {name}! Your message has been saved and a confirmation email was sent.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(user.email, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            msg_title = "Password Reset Request for Task Tracker"
            sender = app.config.get('MAIL_USERNAME')
            msg = Message(msg_title, sender=sender, recipients=[user.email])
            msg.body = f"""
            Hello {user.fullname},
            To reset your password, please click the following link:
            {reset_url}
            If you did not make this request, please ignore this email.
            This link will expire in 1 hour.
            Best,
            The Task Tracker Team
            """
            try:
                mail.send(msg)
                flash('A password reset link has been sent to your email.', 'success')
            except Exception as e:
                print(f"PASSWORD RESET EMAIL FAILED: {e}")
                flash('There was an error sending the email. Please check your terminal for details.', 'danger')
            return redirect(url_for('forgot_password'))
        else:
            flash('Email not found.', 'danger')
    return render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        flash('The password reset link has expired.', 'danger')
        return redirect(url_for('login'))
    except (BadTimeSignature, Exception):
        flash('Invalid password reset link.', 'danger')
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user = User.query.filter_by(email=email).first()
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been reset successfully! You can now sign in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)