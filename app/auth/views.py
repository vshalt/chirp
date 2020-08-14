from app.auth import auth_blueprint
from app.auth.forms import LoginForm, RegisterForm, UpdatePasswordForm, UpdateEmailForm, PasswordResetRequestForm, PasswordResetForm, UpdateUsernameForm
from flask import render_template, redirect, flash, url_for, request, session
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.emails import send_email

from flask import current_app


@auth_blueprint.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.blueprint != 'auth' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower(), password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Account confirmation', 'auth/mail/confirm', user=user, token=token)
        flash('Account created,Login to continue')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next = request.args.get('next')
            return redirect(next) if next else redirect(url_for('main.home'))
        else:
            flash('Invalid email or password')
    return render_template('auth/login.html', form=form)


@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have successfully logged out')
    return redirect(url_for('main.home'))


@auth_blueprint.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account! Thanks')
    else:
        flash('The time has expired or is invalid, try again')
    return redirect(url_for('main.home'))


@auth_blueprint.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.home'))
    else:
        return render_template('auth/unconfirmed.html', current_app=current_app)


@auth_blueprint.route('/confirm')
@login_required
def resend_confirmation():
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    else:
        token = current_user.generate_confirmation_token()
        send_email(current_user.email, 'Confirm your Account', 'auth/mail/confirm', user=current_user, token=token)
        flash('A new mail has been sent')
    return redirect(url_for('main.home'))


@auth_blueprint.route('/update-password', methods=['GET', 'POST'])
@login_required
def update_password():
    form = UpdatePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Password Updated!')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid Password')
    return render_template('auth/update_password.html', form=form)


@auth_blueprint.route('/reset', methods=['GET', 'POST'])
def reset_password_request():
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(form.email.data, 'Password Reset', 'auth/mail/reset_password', token=token, user=current_user)
            flash('Password reset link sent with instructions')
        else:
            flash('Invalid email')
    return render_template('auth/forgot_password_request.html', form=form)


@auth_blueprint.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.home'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password_1.data):
            db.session.commit()
            flash('Your password has been updated. Login to continue')
            return redirect(url_for('auth.login'))
        else:
            flash('Try again later')
            return redirect(url_for('main.home'))
    return render_template('auth/reset_password.html', form=form)


@auth_blueprint.route('/update-email', methods=['GET', 'POST'])
@login_required
def update_email():
    form = UpdateEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            session['new_email'] = new_email
            token = current_user.generate_email_update_token(new_email=new_email)
            send_email(new_email, 'Account Updated', 'auth/mail/update_email', token=token)
            flash('mail sent with instructions')
            return redirect(url_for('main.home'))
        else:
            flash('Check your password')
    return render_template('auth/update_email.html', form=form)


@auth_blueprint.route('/update-email/<token>')
@login_required
def update_email_token(token):
    if User.update_email(token, session.get('new_email')):
        db.session.commit()
        flash('Your account credentials has been updated. Login with new email')
        return redirect(url_for('auth.login'))
    else:
        flash('invalid email or token timed out')
    return redirect(url_for('main.home'))


@auth_blueprint.route('/update-username', methods=['GET', 'POST'])
@login_required
def update_username():
    form = UpdateUsernameForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            current_user.username = form.username.data
            db.session.add(current_user)
            db.session.commit()
            flash('Username Updated')
        else:
            flash('check password')
    return render_template('auth/update_username.html', form=form)
