from flask import Blueprint, request
from settings import DB_DIRECTORY
import os, json, uuid

db = Blueprint('db', __name__)

def get_db_path(db_name):
    if not os.path.exists(DB_DIRECTORY):
        os.makedirs(DB_DIRECTORY)

    return os.path.join(DB_DIRECTORY, db_name + '.json')

def read(db_name, default={}):
    db_path = get_db_path(db_name)
    if not os.path.exists(db_path):
        with open(db_path, 'w') as f:
            json.dump(default, f)
        return default
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

class Model:
    def __init__(self, **kwargs):
        self.verify(**kwargs)

        # self.__dict__.update(kwargs)
        for key, value in self.Meta.fields.items():
            if key in kwargs:
                self.__dict__.update({key: kwargs[key]})
            elif value.verify_default():
                self.__dict__.update({key: value.default})
        
        # if id doesnt exist (or empty), generate a new one
        if 'id' not in self.__dict__:
            self.__dict__.update({'id': str(uuid.uuid4())})

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}> {json.dumps(self.serialize(), indent=4)}"

    def verify(self, **kwargs):
        for key, value in kwargs.items():
            field = self.Meta.fields.get(key)
            assert field, f'Invalid field: {key}'
            field.verify(value)

    def serialize(self):
        return {key: value for key, value in self.__dict__.items() if key in self.Meta.fields}

    class Meta:
        fields = {}

class Field:
    def __init__(self, default=None):
        if default is not None:
            self.verify_value(default)

        self.default = default
    
    def verify_value(self, value):
        return True

    def verify_default(self):
        return getattr(self, 'default', None) is not None
    
    def verify(self, value):
        if value is None and self.verify_default():
            return
        elif not self.verify_value(value):
            raise ValueError(f'Invalid value: {value}')
        else:
            return True
    
class StringField(Field):
    def verify_value(self, value):
        return isinstance(value, str)
    
class NumberField(Field):
    def verify_value(self, value):
        return isinstance(value, (int, float))
        
class BooleanField(Field):
    def verify_value(self, value):
        return isinstance(value, bool)
