# A CLI frontend for the program.
# Commands:
## new <name> <time?> <frequency?> <duration?>
## list
## edit <id> <name?> <time?> <frequency?> <duration?>
## delete <id>
## complete <id>

import argparse

parser = argparse.ArgumentParser(description='Habit Tracker CLI')

subparsers = parser.add_subparsers(dest='command', required=True)

parser_new = subparsers.add_parser('new', help='Create a new habit')
parser_new.add_argument('name', type=str, help='Name of the habit')
parser_new.add_argument('--time', type=str, default='00:00', help='Time to perform the habit')
parser_new.add_argument('--frequency', type=int, default=1, help='Frequency in days')
parser_new.add_argument('--duration', type=int, default=30, help='Duration in minutes')

parser_list = subparsers.add_parser('list', help='List all habits')

parser_edit = subparsers.add_parser('edit', help='Edit an existing habit')
parser_edit.add_argument('id', type=int, help='ID of the habit to edit')
parser_edit.add_argument('name', type=str, help='New name of the habit')
parser_edit.add_argument('time', type=str, help='New time to perform the habit')
parser_edit.add_argument('frequency', type=int, help='New frequency in days')
parser_edit.add_argument('duration', type=int, help='New duration in minutes')

parser_delete = subparsers.add_parser('delete', help='Delete a habit')
parser_delete.add_argument('id', type=int, help='ID of the habit to delete')

parser_complete = subparsers.add_parser('complete', help='Mark a habit as complete')
parser_complete.add_argument('id', type=int, help='ID of the habit to complete')

if __name__ == '__main__':
    args = parser.parse_args()

    if args.command == 'new':
        print(f'Creating new habit: {args.name} at {args.time} every {args.frequency} days that lasts {args.duration} minutes...')
    elif args.command == 'list':
        print('Listing habits...')
    elif args.command == 'edit':
        print(f'Editing habit {args.id}: new name {args.name}, new time {args.time}, new frequency {args.frequency} days, new duration {args.duration} minutes...')
    elif args.command == 'delete':
        print(f'Deleting habit {args.id}...')
    elif args.command == 'complete':
        print(f'Completing habit {args.id}...')
    else:
        print('Invalid command')
