from flask import Blueprint, request
from . import db
from .db import Model, StringField, NumberField, BooleanField
import time

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
            'missed': BooleanField(default=False),
            'streak': NumberField(default=0),
        }

    def last_completed_day_offset(self):
        return (time.time() - self.last_completed) // (DAY_DURATION * self.frequency)

api = Blueprint('api', __name__)

def list_habits():
    return db.read('habits', default=[])
    
def new_habit(name, time='00:00', frequency=1, duration=30):
    habits = list_habits()
    habit = Habit(name=name, time=time, frequency=frequency, duration=duration)
    habits.append(habit.serialize())
    db.save('habits', habits)
    return habit

def edit_habit(id, **kwargs):
    habits = list_habits()
    habit = next((h for h in habits if h.get('id') == id), None)
    if habit:
        habit_obj = Habit(**habit)
        habit_obj.verify(**kwargs)
        for key, value in kwargs.items():
            habit_obj.__dict__.update({key: value})
        habits = [h for h in habits if h.get('id') != id]
        habits.append(habit_obj.serialize())
        db.save('habits', habits)
        return habit_obj
    else:
        raise Exception('Habit not found')

def delete_habit(id):
    habits = list_habits()
    habit = next((h for h in habits if h.get('id') == id), None)
    if habit:
        habits = [h for h in habits if h.get('id') != id]
        db.save('habits', habits)
    else:
        raise Exception('Habit not found')

def complete_habit(id):
    habits = list_habits()
    habit = next((h for h in habits if h.get('id') == id), None)
    if habit:
        habit_obj = Habit(**habit)

        day_offset = habit_obj.last_completed_day_offset()
        if day_offset == 0:
            raise Exception('Habit already completed today')
        elif day_offset > 1:
            habit_obj.streak = 1
        else:
            habit_obj.streak += 1

        habit_obj.last_completed = time.time()

        habits = [h for h in habits if h.get('id') != id]
        habits.append(habit_obj.serialize())
        db.save('habits', habits)

        # logging
        log = db.read('log', default={})
        log["habits_completed"] = log.get("habits_completed", 0) + 1
        log["habits_completed_today"] = log.get("habits_completed_today", 0) + 1
        db.save('log', log)

        return habit_obj
    else:
        raise Exception('Habit not found')

@api.route('/habits/list', methods=['GET'])
def view_habits_list():
    try:
        return {'success': True, 'data': list_habits()}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 500

@api.route('/habits/new', methods=['POST'])
def view_habits_new():
    try:
        habit = new_habit(**request.get_json())
        return {'success': True, 'data': habit.serialize()}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400
    
@api.route('/habits/edit', methods=['POST'])
def habits_edit():
    try:
        habit_id = request.get_json().get('id')
        habit = edit_habit(habit_id, **request.get_json())
        return {'success': True, 'data': habit.serialize()}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400
    
@api.route('/habits/delete', methods=['POST'])
def habits_delete():
    try:
        habit_id = request.get_json().get('id')
        delete_habit(habit_id)
        return {'success': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400

@api.route('/habits/complete', methods=['POST'])
def habits_complete():
    try:
        habit_id = request.get_json().get('id')
        habit = complete_habit(habit_id)
        return {'success': True, 'data': habit.serialize()}
    except Exception as e:
        return {'success': False, 'error': str(e)}, 400

def reminder():
    from . import ntfy

    while True:
        # is it the start of a new day?
        if time.time() % DAY_DURATION < REMINDER_UPDATE_INTERVAL:
            log = db.read('log', default={})
            log["habits_completed_today"] = 0
            log["habits_missed_today"] = 0
            db.save('log', log)

        habits = db.read('habits', default=[])
        for habit in habits:
            habit_obj = Habit(**habit)
            # is it time to remind?
            # habit_obj.frequency * DAY_DURATION must have passed since last reminder
            # and the current time must be within the time range
            if time.time() - habit_obj.last_reminded >= habit_obj.frequency * DAY_DURATION and habit_obj.time <= time.time() % (DAY_DURATION * habit_obj.frequency) < habit_obj.time + REMINDER_UPDATE_INTERVAL:
                habit_obj.last_reminded = time.time()
                habit_obj.missed = False
                ntfy.send_notification(f"Hey! It's time to {habit_obj.name}!")
            # otherwise, did the habit pass the time range and was not completed? (habit.duration)
            elif (time.time() - habit_obj.last_reminded >= habit_obj.duration * 60) and (habit_obj.last_completed < habit_obj.last_reminded) and (not habit_obj.missed):
                habit_obj.missed = True
                log = db.read('log', default={})
                log["habits_missed"] = log.get("habits_missed", 0) + 1
                log["habits_missed_today"] = log.get("habits_missed_today", 0) + 1
                db.save('log', log)
            habits = [h for h in habits if h.get('id') != habit_obj.id]
            habits.append(habit_obj.serialize())
            db.save('habits', habits)

        time.sleep(REMINDER_UPDATE_INTERVAL)