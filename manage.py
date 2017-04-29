from flask_migrate import  MigrateCommand
from flask_script import Shell, Manager
from app import create_app, db
from app.models import Admin, Post, Comment
from flask_migrate import Migrate

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, Admin=Admin, Post=Post,
                Comment=Comment)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
    app.run(debug=True)