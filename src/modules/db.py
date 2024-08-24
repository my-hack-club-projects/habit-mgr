from flask import Blueprint, request
import os, json

DB_DIRECTORY = 'db'

db = Blueprint('db', __name__)

def get_db_path(db_name):
    return os.path.join(DB_DIRECTORY, db_name + '.json')

def read(db_name, default={}):
    db_path = get_db_path(db_name)
    if not os.path.exists(db_path):
        with open(db_path, 'w') as f:
            f.write(json.dumps(default))
    with open(db_path, 'r') as f:
        return json.load(f)
    
def save(db_name, data):
    db_path = get_db_path(db_name)
    with open(db_path, 'w') as f:
        json.dump(data, f)

@db.route('/db/<db_name>', methods=['GET', 'POST'])
def db_route(db_name):
    if request.method == 'GET':
        default = request.args.get('default')
        return read(db_name, default)
    elif request.method == 'POST':
        data = request.get_json()
        save(db_name, data)
        return data
