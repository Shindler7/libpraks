#!/usr/bin/env python3

from flask import render_template, redirect, request
from app import application
from app.generator import start_module
from app.dbpanel import DBWork

active_output: str = ''


# https://jinja.palletsprojects.com/en/2.11.x/


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    db_source = DBWork()
    output = ''
    tag_links = []
    global active_output

    # Обработчик запроса пользователя GET
    if request.method == 'GET':

        if request.args.get(key='chatstring'):
            output = start_module(request.args['chatstring'])
            active_output = request.args['chatstring']

        elif request.args.get(key='tagstring'):
            output = start_module(f"{active_output} {request.args['tagstring']}")
        else:
            output = start_module('all')
            active_output = ''

        if active_output == '':
            tag_links = []
        else:
            tag_links = db_source.get_types_name(category=db_source.category_list[active_output])

    return render_template('index.html',
                           title='online',
                           output=output,
                           exoutput=active_output,
                           category_links=db_source.category_list,
                           tag_links=tag_links)


@application.route('/createbase')
def createbase():
    from app.dbpanel import migrate_to_db, tech_all_tables

    # msg = 'Нет команд'

    if not tech_all_tables(command='create.all'):
        return 'Провал создания таблиц'

    if migrate_to_db():
        msg = 'Успешно'
    else:
        msg = 'Ошибка'

    return msg
