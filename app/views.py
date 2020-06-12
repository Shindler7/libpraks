from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import application
from app.forms import LoginForm, RegForm
from app.models import Category, Content, Types, User


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    """
    Вывод главной страницы проекта.
    """

    category = request.args.get(key="cy", default="")
    types = request.args.get(key="ts", default="")

    content = Content.manager.get_by(
        category=category,
        types=types
    )

    categories = Category.manager.get_all()
    types_content = Types.manager.get_by(category, dictionary=True)

    form_login = LoginForm(request.form or None)

    data = dict(
        title='online',
        categories=categories,
        excat=category,
        content=content,
        types=types_content,
        form_login=form_login,
    )

    if request.method == 'POST':
        if form_login.validate_on_submit() and form_login.submit.data:
            user = User.manager.get(
                nick=form_login.nickname.data,
                passd=form_login.password.data)
            if user:
                login_user(user, remember=True)

    return render_template('index.html', **data)


@application.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Регистрация пользователя.
    """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegForm()

    if form.validate_on_submit():
        user = User.manager.create(
            nick=form.nickname.data,
            passd=form.password1.data
        )
        login_user(user, remember=True)

        return redirect(url_for('index'))

    return render_template('auth/registration.html', title='Регистрация',
                           form_reg=form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    """
    Авторизация пользователя.
    """

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.manager.get(
            nick=form.nickname.data,
            passd=form.password.data)
        if user:
            login_user(user, remember=True)

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)

    return render_template('auth/login.html',
                           title='Авторизация',
                           form=form)


@application.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Разлогинивание пользователя.
    """

    if current_user.is_authenticated:
        logout_user()

    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')

    return redirect(next_page)


@application.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404


@application.errorhandler(500)
def server_error(error):
    return render_template('error/500.html'), 500
