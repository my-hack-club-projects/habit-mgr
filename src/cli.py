# A CLI frontend for the program.
# Commands:
## new <name> <time?> <frequency?> <duration?>
## list
## edit <id> <name?> <time?> <frequency?> <duration?>
## delete <id>
## complete <id>

import argparse, colorama
from modules import api, db

def parse_time_str(time_str):
    # Convert 14:30 or 14:30:59 to seconds since midnight
    time_parts = time_str.split(':')
    if len(time_parts) > 3:
        raise argparse.ArgumentTypeError('Invalid time format')
    try:
        time_parts = [int(part) for part in time_parts]
    except ValueError:
        raise argparse.ArgumentTypeError('Invalid time format')
    
    current_multiplier = 60 * 60
    time = 0
    for part in time_parts:
        if part < 0 or part >= 60:
            raise argparse.ArgumentTypeError('Invalid time format')

        time += part * current_multiplier
        current_multiplier //= 60
    return time

def parse_time_seconds(time):
    # Convert seconds since midnight to 14:30
    hours = time // 3600
    minutes = (time % 3600) // 60
    seconds = time % 60

    if seconds == 0:
        return f'{hours}:{minutes:02}'
    else:
        return f'{hours}:{minutes:02}:{seconds:02}'

def human_readable_duration_days(remaining_days, singular_remove_count=True):
    if remaining_days == 0:
        return "none"

    units = {
        'day': 1,
        'week': 7,
        'month': 30,
        'year': 365
    }
    units_sorted = sorted(units.items(), key=lambda x: x[1], reverse=True)
    parts = []

    while remaining_days > 0:
        for unit, value in units_sorted:
            if remaining_days >= value:
                count = remaining_days // value
                parts.append(f'{count} {unit}{"s" if count > 1 else ""}')
                remaining_days %= value
                break
    
    if len(parts) > 1:
        return ', '.join(parts[:-1]) + ' and ' + parts[-1]
    else:
        if singular_remove_count:
            return parts[0].strip("1 ") # If it's the only unit and it's singular, remove the count
        else:
            return parts[0]

parser = argparse.ArgumentParser(description='Habit Tracker CLI')

subparsers = parser.add_subparsers(dest='command', required=True)

parser_new = subparsers.add_parser('new', help='Create a new habit')
parser_new.add_argument('name', type=str, help='Name of the habit')
parser_new.add_argument('time', type=str, default='00:00', help='Time to perform the habit')
parser_new.add_argument('frequency', type=int, default=1, help='Frequency in days')
parser_new.add_argument('duration', type=int, default=30, help='Duration in minutes')

parser_list = subparsers.add_parser('list', help='List all habits')
parser_overview = subparsers.add_parser('overview', help='Show an overview of all habits')

parser_edit = subparsers.add_parser('edit', help='Edit an existing habit')
parser_edit.add_argument('id', type=str, help='ID of the habit to edit')
parser_edit.add_argument('name', type=str, help='New name of the habit')
parser_edit.add_argument('time', type=str, help='New time to perform the habit')
parser_edit.add_argument('frequency', type=int, help='New frequency in days')
parser_edit.add_argument('duration', type=int, help='New duration in minutes')

parser_delete = subparsers.add_parser('delete', help='Delete a habit')
parser_delete.add_argument('id', type=str, help='ID of the habit to delete')

parser_complete = subparsers.add_parser('complete', help='Mark a habit as complete')
parser_complete.add_argument('id', type=str, help='ID of the habit to complete')

if __name__ == '__main__':
    args = parser.parse_args()

    if 'time' in args:
        processed_time = parse_time_str(args.time)
    if 'id' in args:
        # find the closest-matching habit ID
        matching_habits = [habit for habit in api.list_habits() if args.id in habit.get('id')]
        if len(matching_habits) == 0:
            print(colorama.Fore.RED + 'Error: Habit not found', colorama.Style.RESET_ALL)
            exit()
        closest_match = min(matching_habits, key=lambda habit: abs(len(habit.get('id')) - len(args.id)))
        if closest_match.get('id', None) is None:
            print(colorama.Fore.RED + 'Error: Habit not found', colorama.Style.RESET_ALL)
            exit()
        args.id = closest_match.get('id')

    if args.command == 'new':
        try:
            habit = api.new_habit(args.name, time=processed_time, frequency=args.frequency, duration=args.duration)
            print('Habit created! ID:', colorama.Fore.GREEN + str(habit.id) + colorama.Style.RESET_ALL)
        except Exception as e:
            print(colorama.Fore.RED + 'Error:', e, colorama.Style.RESET_ALL)
    elif args.command == 'list':
        habits = api.list_habits()
        for habit in habits:
            print(f'{colorama.Fore.GREEN}{habit.get("id")}{colorama.Style.RESET_ALL}: "{habit.get("name")}" at {parse_time_seconds(habit.get("time"))} every {human_readable_duration_days(habit.get("frequency"))} that lasts {habit.get("duration")} minutes')
    elif args.command == 'overview':
        log = db.read('log', default={})

        print(f'In total, you\'ve completed {colorama.Fore.GREEN}{log.get("habits_completed", 0)}{colorama.Style.RESET_ALL} habits and missed {colorama.Fore.RED}{log.get("habits_missed", 0)}{colorama.Style.RESET_ALL}.\n')
        print(f'Here are your streaks:\n')
        habits = api.list_habits()
        if len(habits) == 0:
            print(f'{colorama.Fore.LIGHTBLACK_EX}... nothing yet!{colorama.Style.RESET_ALL}')
        for habit in habits:
            print(f'{habit.get("name")}: {colorama.Fore.GREEN}{human_readable_duration_days(habit.get("streak"), singular_remove_count=False)}{colorama.Style.RESET_ALL}')
        print()
        print(f'Today, you\'ve completed {colorama.Fore.GREEN}{log.get("habits_completed_today", 0)}{colorama.Style.RESET_ALL} habits and missed {colorama.Fore.RED}{log.get("habits_missed_today", 0)}{colorama.Style.RESET_ALL}.')
    elif args.command == 'edit':
        try:
            habit = api.edit_habit(args.id, name=args.name, time=args.time, frequency=args.frequency, duration=args.duration)
            print('Habit edited!')
        except Exception as e:
            print(colorama.Fore.RED + 'Error:', e, colorama.Style.RESET_ALL)
    elif args.command == 'delete':
        try:
            api.delete_habit(args.id)
            print('Habit deleted!')
        except Exception as e:
            print(colorama.Fore.RED + 'Error:', e, colorama.Style.RESET_ALL)
    elif args.command == 'complete':
        try:
            habit = api.complete_habit(args.id)
            print(f'Habit completed! Streak: {colorama.Fore.GREEN}{habit.streak}{colorama.Style.RESET_ALL}')
        except Exception as e:
            print(colorama.Fore.RED + 'Error:', e, colorama.Style.RESET_ALL)
    else:
        print('Invalid command')
