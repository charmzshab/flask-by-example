import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db


app.config.from_object(os.environ['APP_SETTINGS'])

# Flask-Migrate will introspect the application object for you and find out about available models on its own.
#  As long as you import app in manage.py and the models in app.py you are doing fine.

migrate = Migrate(app, db)
manager = Manager(app)

# added the db command to the manager so that we can run the migrations from the command line
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()