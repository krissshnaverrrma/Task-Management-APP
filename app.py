import os
import time
from datetime import datetime, timedelta 
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt
import secrets
import random 
from pathlib import Path
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = os.environ.get("UPLOAD_FOLDER", "static/profile_pics")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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
    image_version = db.Column(db.Integer, default=1) 
    security_question = db.Column(db.String(150), nullable=True)
    security_answer_hash = db.Column(db.String(150), nullable=True)
    tasks = db.relationship('Task', backref='author', lazy=True)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(300), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    due_date = db.Column(db.DateTime, nullable=True)
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
    return render_template('index.html')
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
    return render_template('mytasks.html', tasks=tasks)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        plain_text_password = request.form.get('password')
        username = request.form.get('username')
        security_question = request.form.get('security_question')
        security_answer = request.form.get('security_answer')
        if security_answer and security_question:
            hashed_answer = bcrypt.generate_password_hash(security_answer).decode('utf-8')
        else:
            flash('Please select a security question and provide an answer.', 'danger')
            return redirect(url_for('register'))
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
            image_version=int(time.time()),
            security_question=security_question,         
            security_answer_hash=hashed_answer,        
        ) 
        db.session.add(new_user)
        db.session.commit()
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
                current_user.image_version = int(time.time())
                db.session.commit()
                flash('Profile photo has been removed.', 'info')
            return redirect(url_for('update_profile')) 
        elif 'save_changes' in request.form:
            new_username = request.form.get('username')
            new_fullname = request.form.get('fullname')
            new_phone = request.form.get('phone') 
            if new_username != current_user.username:
                existing_user = User.query.filter_by(username=new_username).first()
                if existing_user:
                    flash('That username is already taken. Please choose another.', 'danger')
                    return redirect(url_for('update_profile')) 
                current_user.username = new_username  
            if 'picture' in request.files and request.files['picture'].filename != '':
                delete_picture(current_user.profile_image) 
                picture = request.files['picture']
                filename = save_picture(picture)
                current_user.profile_image = filename 
                current_user.image_version = int(time.time())    
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
        flash(f'Thank you, {name}! Your message has been noted.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        identifier = request.form.get('identifier') 
        user = User.query.filter(
            (User.email == identifier) | (User.username == identifier)
        ).first()
        if user:
            return redirect(url_for('reset_security', user_id=user.id))
        else:
            flash('User not found. Please check your email or username.', 'danger')
            return redirect(url_for('forgot_password'))
    return render_template('forgot_password.html')
@app.route('/reset_security/<int:user_id>', methods=['GET', 'POST'])
def reset_security(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        submitted_answer = request.form.get('answer')
        if bcrypt.check_password_hash(user.security_answer_hash, submitted_answer):
            return redirect(url_for('reset_password_new', user_id=user.id))
        else:
            flash('Incorrect security answer.', 'danger')
            return redirect(url_for('reset_security', user_id=user.id))
    return render_template('reset_security.html', 
                           user_id=user.id, 
                           question=user.security_question)
@app.route('/reset_password_new/<int:user_id>', methods=['GET', 'POST'])
def reset_password_new(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_password = request.form.get('password')
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        flash('Your password has been reset successfully! Please sign in.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password_new.html', user_id=user.id)