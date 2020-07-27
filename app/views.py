import logging
import os
from random import choice

from flask import Response, redirect, render_template, request
from flask import flash, send_from_directory, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import application, csrf, db_lib
from app.auth_services import get_yandex_oauth_code, yandex_oauth
from app.forms import LoginForm, RegForm
from app.models import Category, Content, Types, User
from app.utils import get_screen_name


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


@application.route('/login')
def login():
    """
    Переадресация на страницу 'https://oauth.yandex.ru/' для прохождения
    авторизации. Ответ возвращается на адрес '/authorize'.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    redirect_uri = url_for('authorize', _external=True)
    return get_yandex_oauth_code(redirect_uri)


@application.route('/authorize')
def authorize():
    """
    Логин пользователя по ответу от Yandex.
    """
    code = request.args.get('code')
    nickname, social_id = yandex_oauth(code)

    user = User.manager.get_or_create(
        nickname=nickname,
        social_id=social_id
    )
    login_user(user, remember=True)
    return redirect('/')


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


@login_required
@application.route('/user/<username>', methods=['GET', 'POST'])
def profile(username):
    """
    Профиль пользователя. Возможность изменить логин, пароль.
    В перспективе сохранить свои любимые ссылки.
    """
    if username != current_user.nickname:
        return redirect(url_for('index'))

    types = Types.manager.get_by('', dictionary=True)

    return render_template('auth/profile.html', types=types)


@login_required
@application.route('/user/subscribes/<int:user_id>/<int:content_id>',
                   methods=['GET'])
def profile_action(user_id, content_id):
    """
    Оформление подписок для личной коллекции ссылок.
    """

    if current_user.id != user_id:
        return redirect(url_for('index'))

    try:
        user = User.query.get(user_id)
        content = Content.query.get(content_id)
        if content and content in user.content_id:
            user.content_id.remove(content)
        else:
            user.content_id.append(content)

        db_lib.session.add(user)
        db_lib.session.commit()
    except Exception as err:
        flash(f'Возникла ошибка подписки: {err}', category='danger')

    if request.args.get('profile'):
        reverse_page = url_for('profile', username=current_user.nickname)
    else:
        reverse_page = url_for('index')

    return redirect(reverse_page)


@application.route('/save/screenshot', methods=['GET', 'POST'])
@csrf.exempt
def save_screenshot():
    """
    Получение и сохранение скриншота.
    """

    logging.info(msg=f'Монитор вернулся: {request.data}')

    secret_key = request.form.get(key="token", default="")
    if secret_key != application.config['SCREEN_SERVER_SECRET_KEY']:
        return Response('Access denied! Wrong token!', status=403)

    if request.method == 'POST':
        id = request.form.get(key="id", default=None)
        screen = request.files.get(key="screen", default=None)

        if id is None or screen is None:
            return Response('Bad request!', status=400)

        screen_name = secure_filename(get_screen_name(id))

        upload_folder = os.path.join(
            'app',
            'static',
            application.config['SCREEN_URL_ROOT'],
            application.config['SCREEN_URL_FOLDER'],
            secure_filename(screen_name)
        )

        screen.save(upload_folder)

        item = Content.query.filter_by(id=id).first()
        item.img_url = screen_name
        db_lib.session.add(item)
        db_lib.session.commit()

        return Response('Image saved', status=200)


@application.route('/load-screen/<filename>')
def load_screen(filename=''):
    """
    Обеспечивает извлечение изображений, при отсутствии возвращает заглушку.
    """
    if filename != '0':
        url_to_img = os.path.join(
            'static',
            application.config['SCREEN_URL_ROOT'],
            application.config['SCREEN_URL_FOLDER']
        )

        check_img = os.path.join(
            os.getcwd(),
            'app',
            url_to_img,
            filename
        )

        if os.path.exists(check_img):
            return send_from_directory(url_to_img, filename=filename)

    filename = choice(('default_dog.jpg', 'default-cat-2.jpg',
                       'default-dog-2.jpg', 'default-dog-3.jpg'))

    url_to_img = os.path.join(
        'static',
        application.config['SCREEN_URL_ROOT'],
        application.config['IMAGE_OUTPUT']
    )

    return send_from_directory(url_to_img, filename=filename)


@application.errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404


@application.errorhandler(500)
def server_error(error):
    return render_template('error/500.html'), 500
