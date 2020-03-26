#!/usr/bin/env python3

from flask import render_template, flash, redirect, request
from app.forms import ChatForm
from app import application
from app.generator import startmodule

@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    form=ChatForm()
    output = ''
    helps = help()
    
    # Обработчик запроса пользователя
    #if form.validate_on_submit():
    #    txt_ans = 'Привет, мир!'
    if request.method == 'POST':
        
        output = startmodule(form.chatstring.data)

    return render_template('index.html', title='online', form=form, output=output, help=helps)


def help():
    from app._dblib import keytypedisp
    from app.generator import compilereq

    req = compilereq()
    tags = keytypedisp.values()
    

    txt = f'''<div id = "helpus">Библиотека ЯП: коллекция. Допустимые команды:<br>
            <ol>
            <li> Однострочный калькулятор Python (проверь: 2+2*2).</li>
            <li> Свободный <i>запрос</i>. </li>
            </ol>
            <ul>
            <li>доступные категории: {', '.join(tags).lower()};</li>
            <li>доступные ключи: {', '.join(req.getTag())}.</li>
            <br>
            </div>
            '''

    return txt
