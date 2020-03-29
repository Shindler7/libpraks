#!/usr/bin/env python3

from flask import render_template, flash, redirect, request
from app.forms import ChatForm
from app import application
from app.generator import startmodule
from flask_mobility.decorators import mobile_template
from flask_mobility.decorators import mobilized

@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    form=ChatForm()
    output = ''
    helps = help()
    
    # Обработка в режиме POST
    #if request.method == 'POST':
        #output = startmodule(form.chatstring.data)
    
    # Обработчик запроса пользователя GET
    if request.method == 'GET':
        if request.args.get(form.chatstring.name, None):
            output = startmodule(request.args[form.chatstring.name])

    return render_template('index.html', title='online', form=form, output=output, help=helps)

@mobilized(index)
def index_v():
    return 'Здесь'

def help():
    from app._dblib import keytypedisp
    from app.generator import compilereq

    req = compilereq()
    tags = keytypedisp.values()
    

    txt = f'''<div id = "helpus">Библиотека ЯП: коллекция. Допустимые команды:<br>
            <ol>
            <li> Однострочный калькулятор Python (проверь: 2+2*2).</li>
            <li> Свободный <i>запрос</i> ('всё' или команда в вольном стиле по категориям и ключам). </li>
            </ol>
            <ul>
            <li>доступные категории: {', '.join(tags).lower()};</li>
            <li>доступные ключи: {', '.join(req.getTag())}.</li>
            <br>
            </div>
            '''

    return txt
