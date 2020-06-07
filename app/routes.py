from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.urls import url_parse

from app import application
from app import db_lib
from app.dbpanel import DBExecute
from app.exc import LibBaseError
from app.forms import CategoryForm, LoginForm, NewDataForm, RegForm, TypesForm
from app.generator import start_module
from app.models import Category, Types, User

# Дополнительные настройки
# dbw = DBExecute()
application.add_template_global(DBExecute.get_all_category(), 'category_links')


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    """
    Вывод главной страницы проекта.
    """
    dbw = DBExecute()

    form_login = LoginForm(request.form or None)
    data_render = dict(
        title='online',
        output='',
        tag_links=list(),
        exoutput='',
        types=dbw.get_list_types_reverse,
        form_login=form_login
    )

    chatstring = request.args.get(key="chatstring", default="")
    tagstring = request.args.get(key="tagstring", default="")
    question_to_base = f'{chatstring} {tagstring}'
    data_render['output'] = start_module(question_to_base, in_print=False)

    data_render['exoutput'] = request.args.get(key='chatstring', default='')

    tag_links = dbw.get_choices_types(category=data_render['exoutput'])
    data_render['tag_links'] = tag_links

    if request.method == 'POST':
        if form_login.validate_on_submit() and form_login.submit.data:
            user = User.query.filter_by(
                nickname=form_login.nickname.data).first()
            if user is None or not user.check_password(
                    form_login.password.data):
                flash('Неверные данные.', category='error')
                return render_template('index.html', **data_render)

            login_user(user, remember=True)

    if request.method == 'GET':
        pass

    return render_template('index.html', **data_render)


@application.route('/db', methods=['GET', 'POST'])
@application.route('/db/base', methods=['GET', 'POST'])
@login_required
def db_view():
    """
    Для авторизованных пользователей работа с записями в базе данных.

    :return: HttpResponse, форма.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    dbw = DBExecute()

    form = NewDataForm(request.form or None)

    if request.method == 'GET':
        form.lang.choices = [(str(ids), lng[0]) for ids, lng in
                             enumerate(dbw.get_list_language)]
        form.category.choices = [(str(key), cat) for key, cat in
                                 dbw.get_list_category_reverse.items()]

        form.types.choices = [(str(key), typ) for key, typ in
                              dbw.get_list_types_reverse.items()]

    if request.method == 'POST':
        if form.validate_on_submit():
            data_to_db = {
                'name': form.name.data,
                'url': form.url.data,
                'lang': form.lang.choices[
                    int(form.lang.data)][1],
                'types': dbw.get_list_types_reverse[
                    int(form.types.data)],
                'category': dbw.get_list_category_reverse[
                    int(form.category.data)]
            }

            try:
                dbw.add_to_db(create_types=False, create_category=False,
                              **data_to_db)
            except LibBaseError as err:
                flash(f'Возникла ошибка базы данных: {err}', category='danger')

            else:
                flash('Запись успешно сохранена!', category='success')
                return redirect(url_for('db_view'))

    db_output = dbw.get_content(full=True)

    return render_template('dbpanel/db_panel.html',
                           form=form, db=db_output)


@application.route('/db/cat', methods=['GET', 'POST'])
@login_required
def db_category():
    """
    Просмотр и добавление категорий и типов.
    :return: HttpResponse, форма.
    """

    dbw = DBExecute()

    if not current_user.isadmin:
        redirect(url_for('index'))

    category = Category.query.all()
    types = Types.query.all()

    form_cat = CategoryForm(request.form or None, prefix='category')
    form_type = TypesForm(request.form or None, prefix='types')

    if request.method == 'POST':

        if request.form.get('category-name', False) \
                and form_cat.validate_on_submit():
            name = form_cat.name.data
            fname = form_cat.fname.data
            if not fname:
                fname = None
            result = dbw.add_category(name=name, fname=fname)
            if result:
                flash('Категория успешно добавлена!', category='success')
                return redirect(url_for('db_category'))
            else:
                flash('Ошибка сохранения категории...', category='danger')

        if request.form.get('types-name', False) \
                and form_type.validate_on_submit():
            name = form_type.name.data
            fname = form_type.fname.data
            if not fname:
                fname = None
            result = dbw.add_types(name=name, fname=fname)
            if result:
                flash('Тип материалов успешно добавлен!',
                      category='success')
                return redirect(url_for('db_category'))
            else:
                flash('Ошибка сохранения нового типа...',
                      category='danger')

    return render_template('dbpanel/db_category.html',
                           category=category, types=types,
                           form_cat=form_cat, form_type=form_type)


@application.route('/db/cat/edit/<int:data_id>', methods=['GET', 'POST'])
@login_required
def db_edit_category(data_id: int):
    """
    Редактирование конкретной категории.
    :return: HttpResponse, форма.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    category = Category.query.all()
    edit = db_lib.session.query(Category).get(data_id)
    form = CategoryForm(request.form or None)

    if request.method == 'GET':
        form.name.data = edit.name
        form.fname.data = edit.fname

    if request.method == 'POST':
        if form.validate_on_submit():
            edit.name = form.name.data
            if form.fname.data:
                edit.fname = form.fname.data
            try:
                db_lib.session.commit()
            except SQLAlchemyError as err:
                flash(f'Что-то пошло не так... {err}', category='danger')
            else:
                flash('Изменения сохранены!', category='success')
                return redirect(url_for('db_category'))

    return render_template('dbpanel/db_category.html',
                           category=category, form=form)


@application.route('/db/cat/types/edit/<int:data_id>', methods=['GET', 'POST'])
@login_required
def db_edit_types(data_id: int):
    """
    Редактирование конкретного типа.
    :return: HttpResponse, форма.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    types = Types.query.all()
    edit = db_lib.session.query(Types).get(data_id)
    form = TypesForm(request.form or None)

    if request.method == 'GET':
        form.name.data = edit.name
        form.fname.data = edit.fname

    if request.method == 'POST':
        if form.validate_on_submit():
            edit.name = form.name.data
            if form.fname.data:
                edit.fname = form.fname.data
            try:
                db_lib.session.commit()
            except SQLAlchemyError as err:
                flash(f'Что-то пошло не так... {err}', category='danger')
            else:
                flash('Изменения сохранены!', category='success')
                return redirect(url_for('db_category'))

            return redirect(url_for('db_category'))

    return render_template('dbpanel/db_category.html',
                           types=types, form=form)


@application.route('/db/cat/active', methods=['GET', 'POST'])
@login_required
def db_category_active():

    if not current_user.isadmin:
        redirect(url_for('index'))

    dbw = DBExecute()

    if request.args.get(key='delete_category', default='') or \
            request.args.get(key='delete_types', default=''):

        method = 'category' if request.args.get(key='delete_category') \
            else 'types'
        data_id = request.args.get(key=f'delete_{method}')

        result = dbw.delete_category_or_types(method, data_id=data_id)
        if result:
            flash('Данные успешно удалены!', category='success')
        else:
            flash('Ошибка удаления данных...', category='danger')

    return redirect(url_for('db_category'))


@application.route('/db/user', methods=['GET', 'POST'])
@login_required
def db_user():
    """
    Просмотр и редактирование пользователей.

    :return: HttpResponse, форма.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    users = User.query.all()

    return render_template('dbpanel/db_user.html', users=users)


@application.route('/db/user/active', methods=['GET', 'POST'])
@login_required
def db_user_active():
    if not current_user.isadmin:
        redirect(url_for('index'))

    dbw = DBExecute()

    if request.args.get(key='delete', default=''):
        result = dbw.delete_user(user_id=request.args.get('delete'))
        if result:
            flash('Пользователь успешно удалён!', category='success')
        else:
            flash('Ошибка удаления пользователя...', category='danger')

    keys = ('isadmin', 'active',)
    for key in keys:
        argument = request.args.get(key=key, default=0)
        if argument:
            result = dbw.change_user_status(key, user_id=argument)
            if result:
                flash('Данные успешно изменены!', category='success')
            else:
                flash('Ошибка изменения данных...', category='danger')

    return redirect(url_for('db_user'))


@application.route('/delfrombase/<int:idn>', methods=['GET', 'POST'])
@login_required
def delete_from_bd(idn: int):
    if not current_user.isadmin:
        redirect(url_for('index'))

    dbw = DBExecute()

    dbw.del_from_db(id_n=idn)
    flash('Запись успешно удалена!', category='success')

    return redirect(url_for('db_view'))


@application.route('/signup', methods=['GET', 'POST'])
@application.template_global()
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegForm()

    if form.validate_on_submit():
        user = User(nickname=form.nickname.data)
        user.set_password(form.password1.data)
        db_lib.session.add(user)
        db_lib.session.commit()

        login_user(user, remember=True)

        return redirect(url_for('index'))

    return render_template('auth/registration.html', title='Регистрация',
                           form_reg=form)


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

    form = LoginForm(prefix='login')

    if form.validate_on_submit():
        user = User.query.filter_by(nickname=form.nickname.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверные данные.', category='error')
            return redirect(url_for('login'))

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
