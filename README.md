# habit-mgr
forces you to do stuff
--

Ever wanted to set daily goals, such as reading a book, exercising or studying? Did you find it hard to stick to these goals?
Well now, you can set reminders to go off when you're supposed to be doing one of such habits, directly from your terminal!

![image](https://github.com/user-attachments/assets/8d7eecc3-b9a5-4728-bd3e-a5c9c7d3650a)

You can retrieve information on all of the habits like this:
![image](https://github.com/user-attachments/assets/49ccada6-c867-4807-88e6-0b1e832f2805)

Or get an overview of your recent activity:
![image](https://github.com/user-attachments/assets/644fff7f-33e1-4c41-a597-e65aa88c8242)

When it's time to do a habit, you'll get a push notification send via https://ntfy.sh!

## installation
This program is intended to be self-hosted, either on localhost, on a home server, or wherever else you want to.It currently consists of two parts - a Flask API/backend and a CLI frontend. They can be used separately, but the Flask app needs to be running in order to send notifications.
If you don't want or need notifications, you can just use the CLI, which is a Python script. Otherwise, set the `app.py` file to auto-run on startup of your computer.

## contributing
I made the API and database as much open as possible, so you can easily add or remove features. If you end up creating something on top of this program, I'd appreciate it if you opened a pull request on this repo!
