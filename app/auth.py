from flask import Blueprint, flash, render_template, request, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('การเข้าสู่ระบบสำเร็จ', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง', category='error')
        else:
            flash('ไม่พบอีเมลที่ใช้งาน', category='error')
    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # code to validate and add user to database goes here
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        sector = request.form.get('sector')
        password = request.form.get('password')
        confirmed_password = request.form.get('confirmed_Password')

        # if this returns a user, then the email already exists in database
        user = User.query.filter_by(email=email).first()
        # if a user is found, we want to redirect back to signup page so user can try again
        if user:
            flash('อีเมลนี้ถูกลงทะเบียนแล้ว', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 1:
            flash('กรุณาระบุชื่อจริงของคุณ', category='error')
        elif len(last_name) < 1:
            flash('กรุณาระบุนามสกุลของคุณ')
        elif password != confirmed_password:
            flash('รหัสผ่านไม่ตรงกัน', category='error')
        elif len(password) < 7:
            flash('รหัสผ่านต้องอย่างน้อย 7 ตัวอักษรหรือตัวเลข', category='error')
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        else:
            new_user = User(email=email,
                            first_name=first_name,
                            last_name=last_name,
                            sector=sector,
                            password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash(
                f'บัญชีของคุณ {first_name} {last_name} จาก {sector} ถูกสร้างแล้ว! ',
                category='success'
            )
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)
