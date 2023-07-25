from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db' # relative path to db
db = SQLAlchemy(app) # database instance
migrate = Migrate(app, db)
bcrypt = Bcrypt(app) # bcrypt instance
login_manager = LoginManager(app) # login manager instance
login_manager.login_view = 'login' # function name of login route

from flaskproj import routes
from flaskproj.routes import users
app.register_blueprint(users)
