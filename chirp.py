from app import create_app, db
from app.models import User, Role

app = create_app('default')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


'''
flask shell
flask test
flask db init
    flask db migrate
    flask db upgrade
    flask db downgrade

'''
