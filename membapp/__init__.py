#initialize the app
#from python
from flask import Flask
#from third party
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
#from local
#want to make the object-based config avaliable
from membapp import config

app = Flask(__name__,instance_relative_config=True)
#initialize extension which will protect all my post route against csrf and you must pass the csrf_token when submitting to these routes
csrf = CSRFProtect(app)
#csrf.expempt

#load the config from instance folder file
app.config.from_pyfile('config.py', silent=False)
#how to load config from object_based config that is within your package
app.config.from_object(config.LiveConfig)

#
db=SQLAlchemy(app)

#load the route
from membapp import adminroutes,userroutes