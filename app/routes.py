#!/usr/bin/env python3

from flask import render_template, flash, redirect, request
from app import application
from app.generator import start_module, CompileReq
from app._dblib import keytypedisp, urlbase

active_output: str = ''


# https://jinja.palletsprojects.com/en/2.11.x/


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
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
            tags = CompileReq(key=active_output)
            tag_links = tags.get_tag()
            if len(tag_links) <= 1:
                tag_links = []

    return render_template('index.html',
                           title='online',
                           output=output,
                           exoutput=active_output,
                           category_links=keytypedisp.values(),
                           tag_links=tag_links)


@application.route('/createbase')
def createbase():
    from app.dbpanel import tech_all_tables, add_to_db

    # tech_all_tables(command='create.all')
    # query = {'name': 'Empire of Code',
    #          'url': 'https://empireofcode.com/',
    #          'lang': 'en',
    #          'type': 'game',
    #          'category': 'python'}

    dict_from = urlbase[0]
    querys = {'name': dict_from[0], 'url': dict_from[1], 'lang': dict_from[2], 'types': dict_from[3],
              'category': dict_from[4][0]}

    if add_to_db(**querys):
        msg = 'Успешно'
    else:
        msg = 'Ошибка'

    return msg
