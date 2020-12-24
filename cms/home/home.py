from flask import render_template, Blueprint

from flask_login import login_required

home_blueprint = Blueprint('home', __name__)

@home_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def hello():
    return render_template('home.html')
