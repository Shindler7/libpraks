"""
Дополнительные возможности приложения.
"""

from app import application
from flask import render_template
from app.addons.mdpass import pass_generate


@application.route('/f/gpass', methods=['GET', 'POST'])
def mdpass():
    """
    Генератор паролей.
    """

    password = pass_generate()

    return render_template('addons/mdpass.html',
                           title='Генератор паролей',
                           password=password)
