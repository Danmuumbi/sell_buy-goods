"""from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)"""

from app import create_app, db
from app.models import User, Good

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Good': Good}

if __name__ == '__main__':
    app.run(port=5001,debug=True)


