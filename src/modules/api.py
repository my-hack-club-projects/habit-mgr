from flask import Blueprint, request
from . import db
from .db import Model, StringField, NumberField
import time, threading

# DAY_DURATION = 60 * 60 * 24
DAY_DURATION = 5
REMINDER_UPDATE_INTERVAL = 1

class Habit(Model):
    class Meta:
        fields = {
            'id': StringField(default=None),
            'name': StringField(),
            'frequency': NumberField(default=1),
            'duration': NumberField(default=30),
            'time': NumberField(default=0), # Seconds since midnight
            'last_completed': NumberField(default=0),
            'last_reminded': NumberField(default=0),
            'streak': NumberField(default=0),
        }

    def last_completed_day_offset(self):
        return (time.time() - self.last_completed) // (DAY_DURATION * self.frequency)

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
    
@api.route('/habits/edit', methods=['POST'])
def habits_edit():
    try:
        habit_id = request.get_json().get('id')
        habits = db.read('habits', default=[])
        habit = next((h for h in habits if h.get('id') == habit_id), None)
        if habit:
            habit_obj = Habit(**habit)
            habit_obj.verify(**request.get_json().get('data'))
            for key, value in request.get_json().get('data').items():
                habit_obj.__dict__.update({key: value})
            habits = [h for h in habits if h.get('id') != habit_id]
            habits.append(habit_obj.serialize())
            db.save('habits', habits)
            return {'success': True, 'data': habit_obj.serialize()}
        else:
            return {'success': False, 'error': 'Habit not found'}, 404
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400
    
@api.route('/habits/delete', methods=['POST'])
def habits_delete():
    try:
        habit_id = request.get_json().get('id')
        habits = db.read('habits', default=[])
        habit = next((h for h in habits if h.get('id') == habit_id), None)
        if habit:
            habits = [h for h in habits if h.get('id') != habit_id]
            db.save('habits', habits)
            return {'success': True}
        else:
            return {'success': False, 'error': 'Habit not found'}, 404
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400

@api.route('/habits/complete', methods=['POST'])
def habits_complete():
    try:
        habit_id = request.get_json().get('id')
        habits = db.read('habits', default=[])
        habit = next((h for h in habits if h.get('id') == habit_id), None)
        if habit:
            habit_obj = Habit(**habit)

            day_offset = habit_obj.last_completed_day_offset()
            if day_offset == 0:
                return {'success': False, 'error': 'Habit already completed today'}, 400
            elif day_offset > 1:
                habit_obj.streak = 1
            else:
                habit_obj.streak += 1

            habit_obj.last_completed = time.time()

            habits = [h for h in habits if h.get('id') != habit_id]
            habits.append(habit_obj.serialize())
            db.save('habits', habits)

            return {'success': True, 'data': habit_obj.serialize()}
        else:
            return {'success': False, 'error': 'Habit not found'}, 404
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400

def reminder():
    from . import ntfy

    while True:
        habits = db.read('habits', default=[])
        for habit in habits:
            habit_obj = Habit(**habit)
            # is it time to remind?
            # habit_obj.frequency * DAY_DURATION must have passed since last reminder
            # and the current time must be within the time range
            if time.time() - habit_obj.last_reminded >= habit_obj.frequency * DAY_DURATION and habit_obj.time <= time.time() % (DAY_DURATION * habit_obj.frequency) < habit_obj.time + REMINDER_UPDATE_INTERVAL:
                habit_obj.last_reminded = time.time()
                habits = [h for h in habits if h.get('id') != habit_obj.id]
                habits.append(habit_obj.serialize())
                db.save('habits', habits)

                ntfy.send_notification(f"Hey! It's time to {habit_obj.name}!")

        time.sleep(REMINDER_UPDATE_INTERVAL)

def start_reminder():
    threading.Thread(target=reminder).start()

start_reminder()