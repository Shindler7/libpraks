#!/usr/bin/env python3

from flask import render_template, redirect, request
from app import application
from app.generator import start_module
from app.dbpanel import DBWork

active_output: str = ''


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    """
    Вывод главной страницы проекта.
    """
    global active_output
    dbw = DBWork()
    output: str = ''
    tag_links: list = list()

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

        tag_links = dbw.get_choices_types(category=active_output)
        if len(tag_links) < 2:
            tag_links = list()

    return render_template('index.html',
                           title='online',
                           output=output,
                           exoutput=active_output,
                           category_links=dbw.get_list_category,
                           tag_links=tag_links)


@application.route('/db')
def createbase():
    pass

