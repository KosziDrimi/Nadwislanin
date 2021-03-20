from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

app.config.from_object("project.config.DevelopmentConfig")


db = SQLAlchemy(app)
Migrate(app,db)



from project.views import app_routing

app.register_blueprint(app_routing)