"""
Панель управления
"""

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

from app import application
from app.forms import CategoryForm, EditHeadingsForm, NewDataForm, TypesForm
from app.models import Category, Content, Types, User


@application.route('/db', methods=['GET', 'POST'])
@application.route('/db/base', methods=['GET', 'POST'])
@login_required
def db_view():
    """
    Для авторизованных пользователей работа с записями в базе данных.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    form = NewDataForm()

    form.lang.choices = [(lng.lang, lng.lang) for lng
                         in Content.manager.get_all_lang()]
    form.types.choices = [(types.id, types.name) for types
                          in Types.manager.get_all()]
    form.category.choices = [(cat.id, cat.name) for cat
                             in Category.manager.get_all()]

    if request.method == 'POST':
        if form.validate_on_submit():
            save_data = {
                'name': form.name.data,
                'url': form.url.data,
                'lang': form.lang.data,
                'types_id': form.types.data,
                'category_id': form.category.data
            }
            try:
                Content.manager.add(**save_data)
            except SQLAlchemyError as err:
                flash(f'Возникла ошибка базы данных: {err}', category='danger')
            else:
                flash('Тыц! Запись успешно добавлена.', category='success')
                return redirect(url_for('db_view'))

    content = Content.query.order_by(Content.id.desc()).all()

    return render_template('dbpanel/db_panel.html',
                           form=form, db=content)


@application.route('/db/delete/<int:idn>', methods=['GET', 'POST'])
@login_required
def delete_from_bd(idn: int):
    """
    Удаление записи из таблицы Content.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    try:
        Content.manager.remove(idn)
    except SQLAlchemyError as err:
        flash(f'Возникла ошибка базы данных: {err}', category='danger')
    else:
        flash('Запись успешно удалена!', category='info')

    return redirect(url_for('db_view'))


@application.route('/db/headings', methods=['GET', 'POST'])
@login_required
def db_headings():
    """
    Просмотр и добавление категорий и типов.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    category = Category.manager.get_all()
    types = Types.manager.get_all()

    form_c = CategoryForm(request.form or None, prefix='category')
    form_t = TypesForm(request.form or None, prefix='types')

    if request.method == 'POST':

        if request.form.get('category-name', False) \
                and form_c.validate_on_submit():

            try:
                Category.manager.add(name=form_c.name.data,
                                     f_name=form_c.fname.data)

            except SQLAlchemyError as err:
                flash(f'Ошибка сохранения категории: {err}', category='danger')
            else:
                flash('Категория успешно добавлена!', category='success')
                return redirect(url_for('db_headings'))

        if request.form.get('types-name', False) \
                and form_t.validate_on_submit():

            try:
                Types.manager.add(name=form_t.name.data,
                                  f_name=form_t.fname.data)
            except SQLAlchemyError as err:
                flash(f'Ошибка сохранения типа данных: {err}',
                      category='danger')
            else:
                flash('Новый тип успешно добавлен!', category='success')
                return redirect(url_for('db_headings'))

    return render_template('dbpanel/db_headings.html',
                           category=category, types=types,
                           form_c=form_c, form_t=form_t)


@application.route('/db/headings/category/edit/<int:data_id>',
                   methods=['GET', 'POST'])
@login_required
def db_edit_category(data_id: int):
    """
    Редактирование конкретной категории.
    :return: HttpResponse, форма.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    form = EditHeadingsForm(request.form or None)

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                Category.manager.edit(data_id,
                                      name=form.name.data,
                                      f_name=form.fname.data)
            except SQLAlchemyError as err:
                flash(f'Что-то пошло не так... {err}', category='danger')
            else:
                flash('Изменения сохранены!', category='success')
                return redirect(url_for('db_headings'))

    category = Category.manager.get_all()

    edit = Category.query.get(data_id)
    form.name.data = edit.name
    form.fname.data = edit.fname

    return render_template('dbpanel/db_headings.html',
                           category=category, form=form)


@application.route('/db/headings/types/edit/<int:data_id>',
                   methods=['GET', 'POST'])
@login_required
def db_edit_types(data_id: int):
    """
    Редактирование конкретного типа.
    :return: HttpResponse, форма.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    form = EditHeadingsForm(request.form or None)

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                Types.manager.edit(data_id,
                                   name=form.name.data,
                                   f_name=form.fname.data)
            except SQLAlchemyError as err:
                flash(f'Что-то пошло не так... {err}', category='danger')
            else:
                flash('Изменения сохранены!', category='success')
                return redirect(url_for('db_headings'))

    types = Types.manager.get_all()

    edit = Types.query.get(data_id)
    form.name.data = edit.name
    form.fname.data = edit.fname

    return render_template('dbpanel/db_headings.html',
                           types=types, form=form)


@application.route('/db/headings/active', methods=['GET', 'POST'])
@login_required
def db_headings_active():

    if not current_user.isadmin:
        redirect(url_for('index'))

    try:
        category_id = request.args.get(key='delete_category', default=0)
        if category_id:
            Category.manager.remove(category_id)

        types_id = request.args.get(key='delete_types', default=0)
        if types_id:
            Types.manager.remove(types_id)
    except SQLAlchemyError as err:
        flash(f'Ошибка удаления данных... {err}', category='danger')
    else:
        flash('Данные успешно удалены!', category='info')

    return redirect(url_for('db_headings'))


@application.route('/db/user', methods=['GET', 'POST'])
@login_required
def db_user():
    """
    Просмотр и редактирование пользователей.

    :return: HttpResponse, форма.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    users = User.query.order_by(User.nickname).all()

    return render_template('dbpanel/db_user.html', users=users)


@application.route('/db/user/active', methods=['GET', 'POST'])
@login_required
def db_user_active():
    """
    Набор методов для изменения параметров пользователей.
    """

    if not current_user.isadmin:
        redirect(url_for('index'))

    user_id = request.args.get(key='delete', default=0)
    if user_id:
        User.manager.remove(user_id)
        flash('Пользователь успешно удалён!', category='info')

        return redirect(url_for('db_user'))

    for key in ('isadmin', 'active',):
        user_id = request.args.get(key=key, default=0)
        if user_id:
            User.manager.invert_arg(user_id, key)

    return redirect(url_for('db_user'))
