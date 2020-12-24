from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

from cms import app, db
from cms.models import Users
import os

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server())


@manager.command
def create_db():
    db.create_all()

@manager.command
def drop_db():
    db.drop_all()

@manager.command
def create_admin():
    db.session.add(Users(
        "admin",
        "admin",
        admin=True, )
    )
    db.session.commit()


if __name__ == '__main__':
    manager.run()
