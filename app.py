from flask import Flask
from database import init_db, get_db_context
from models import User, Team, Board

app = Flask(__name__)

with app.app_context():
    init_db()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
