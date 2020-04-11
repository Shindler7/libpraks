#!/usr/bin/env python3

from flask import render_template, flash, redirect, request
from app import application
from app.generator import start_module
from app import nav
from flask_nav.elements import *
#from app.forms import ChatForm
#from flask_mobility.decorators import mobile_template
#from flask_mobility.decorators import mobilized

from app._dblib import keytypedisp
from app.generator import CompileReq

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
            output = start_module('всё')
            active_output = ''

        if active_output == '':
            tag_links = []
        else:
            tags = CompileReq(key=active_output)
            tag_links = tags.get_tag()
            if len(tag_links) <= 1:
                tag_links = []

    return render_template('index.html', title='online', output=output, exoutput=active_output,
                           category_links=keytypedisp.values(), tag_links=tag_links)



