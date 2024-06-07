from flask import render_template, url_for, flash, redirect, request
from app import app, db
from app.forms import RegistrationForm, LoginForm, PostGoodForm
from app.models import User, Good
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os

@app.route('/')
@app.route('/index')
def index():
    goods = Good.query.all()
    return render_template('index.html', goods=goods)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/post_good', methods=['GET', 'POST'])
@login_required
def post_good():
    form = PostGoodForm()
    if form.validate_on_submit():
        if 'image' in request.files:
            image_file = save_image(request.files['image'])
        else:
            image_file = 'default.jpg'
        good = Good(name=form.name.data, description=form.description.data, price=form.price.data, image_file=image_file, seller=current_user)
        db.session.add(good)
        db.session.commit()
        flash('Your good has been posted!', 'success')
        return redirect(url_for('index'))
    return render_template('post_good.html', title='Post Good', form=form)

def save_image(image):
    filename = secure_filename(image.filename)
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)
    return filename

@app.route('/good/<int:good_id>')
def good(good_id):
    good = Good.query.get_or_404(good_id)
    return render_template('good_detail.html', title=good.name, good=good)

@app.route('/good/<int:good_id>/delete', methods=['POST'])
@login_required
def delete_good(good_id):
    good = Good.query.get_or_404(good_id)
    if good.seller != current_user:
        abort(403)
    db.session.delete(good)
    db.session.commit()
    flash('Your good has been deleted!', 'success')
    return redirect(url_for('index'))
