import os
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_session import Session
from sqlalchemy import MetaData
from dotenv import load_dotenv    # from python-dotenv library

load_dotenv()   # load env variables

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Accept"],
    origins=['https://furrylink-frontend.vercel.app']
    )

app.secret_key = os.getenv('SECRET_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')   # configure a database connection to the local file app.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # disable modification tracking to use less memory
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')  
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16 MB  
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_TYPE'] = 'filesystem'  # store session data server-side
app.config['SESSION_PERMANENT'] = False

Session(app)

app.json.compact = False

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)
db.init_app(app)     # initialize the Flask application to use the database

migrate = Migrate(app, db)

api = Api(app)

bcrypt = Bcrypt(app)
