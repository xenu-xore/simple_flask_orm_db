from flask import Flask, render_template
import os
# from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
login_manager.init_app(app)
# bcrypt_flask = Bcrypt(app)
toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)

from cms.login.views import login_blueprint
from cms.articles.views import articles_blueprint
from cms.category.views import category_blueprint
from cms.home.home import home_blueprint

app.register_blueprint(login_blueprint)
app.register_blueprint(articles_blueprint)
app.register_blueprint(category_blueprint)
app.register_blueprint(home_blueprint)

from cms.models import Users

#  login.login - это login папка login это функция, вызов login.login
login_manager.login_view = "login.login"
login_manager.login_message_category = "danger"


@login_manager.user_loader
def user_loader(user_id):
    return Users.query.filter(Users.id == int(user_id)).first()


@app.errorhandler(500)
def server_error_page(error):
    return render_template("error/error_500.html"), 500


@app.errorhandler(404)
def server_error_page(error):
    return render_template("error/error_404.html"), 404
