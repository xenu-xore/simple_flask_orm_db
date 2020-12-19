from flask import redirect, render_template, Blueprint, \
    flash, url_for, request
from .forms import LoginForm
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, \
    login_required
from cms.models import Users
# from cms import bcrypt_flask

login_blueprint = Blueprint('login', __name__)


@login_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = Users.query.filter_by(login=form.login.data).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            flash('Welcome.', 'success')
            return redirect(url_for('login.hello'))
        else:
            flash('Неверный логин и/или пароль.', 'danger')
            return render_template('admin_templates/login.html', form=form)

    return render_template('admin_templates/login.html', form=form)


@login_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def hello():
    return render_template('home.html')


@login_blueprint.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'success')
    return redirect(url_for('login.login'))
