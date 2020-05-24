#!/usr/bin/env python3

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user
from werkzeug.urls import url_parse

from app import application
from app.dbpanel import DBWork
from app.forms import LoginForm, RegForm
from app.generator import start_module
from app.models import User

from app import db_lib

# Дополнительные настройки
application.add_template_global(DBWork().get_list_category, 'list_category')

@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    """
    Вывод главной страницы проекта.
    """
    dbw = DBWork()
    form_login = LoginForm()
    data_render = dict(
        title='online',
        output='',
        category_links=dbw.get_list_category,  # chat_string
        tag_links=list(),  # tag_string
        exoutput='',
        form_login=form_login
    )

    chatstring = request.args.get(key="chatstring", default="")
    tagstring = request.args.get(key="tagstring", default="")
    question_to_base = f'{chatstring} {tagstring}'
    data_render['output'] = start_module(question_to_base)

    data_render['exoutput'] = request.args.get(key='chatstring', default='')

    tag_links = dbw.get_choices_types(category=data_render['exoutput'])
    data_render['tag_links'] = tag_links if len(tag_links) > 1 else list()

    if request.method == 'POST':
        if form_login.validate_on_submit() and form_login.submit.data:
            user = User.query.filter_by(nickname=form_login.nickname.data).first()
            if user is None or not user.check_password(form_login.password.data):
                flash('Неверные данные.', category='error')
                return render_template('index.html', **data_render)

            login_user(user, remember=True)

    if request.method == 'GET':
        pass

    return render_template('index.html', **data_render)


@application.route('/db')
@login_required
def db_view():
    """
    Для авторизованных пользователей работа с записями в базе данных.

    :return: HttpResponse, форма.
    """

    if not current_user.isadmin:
        return f'Техническая страница недоступна для вашей учётной записи. <a href={url_for("index")}>На главную</a>.'

    return 'В стадии разработки.'


@application.route('/login', methods=['GET', 'POST'])
@application.template_global()
def login():
    """
    Форма регистрации и авторизации пользователя.

    :return: HttpResponse, форма.
    """
    # https://habr.com/ru/post/346346/

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form_login = LoginForm(prefix='login')

    if form_login.validate_on_submit():
        user = User.query.filter_by(nickname=form_login.nickname.data).first()
        if user is None or not user.check_password(form_login.password.data):
            flash('Неверные данные.', category='error')
            return redirect(url_for('login'))
        login_user(user, remember=True)

        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('auth/login.html', title='Авторизация',
                           form=form_login)

@application.route('/singin', methods=['GET', 'POST'])
@application.template_global()
def singin():

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form_reg = RegForm()

    if form_reg.validate_on_submit():
        user = User(
            nickname=form_reg.nickname.data
        )
        user.set_password(form_reg.password1.data)
        db_lib.session.add(user)
        db_lib.session.commit()

        login_user(user, remember=True)

        return redirect(url_for('index'))

    return render_template('auth/registration.html', title='Регистрация',
                           form_reg=form_reg)
