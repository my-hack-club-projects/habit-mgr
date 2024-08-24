from flask import Blueprint, request
from . import db
from .db import Model, StringField, NumberField

class Habit(Model):
    class Meta:
        fields = {
            'name': StringField(),
            'frequency': NumberField(default=1),
            'duration': NumberField(default=30)
        }

api = Blueprint('api', __name__)

@api.route('/habits/list', methods=['GET'])
def habits_list():
    try:
        habits = db.read('habits', default=[])
        return {'success': True, 'data': habits}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@api.route('/habits/new', methods=['POST'])
def habits_new():
    try:
        habit = Habit(**request.get_json())
        habits = db.read('habits', default=[])
        habits.append(habit.serialize())
        db.save('habits', habits)
        return {'success': True, 'data': habit.serialize()}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400
