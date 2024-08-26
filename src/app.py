from flask import Flask, render_template
from modules import api
from modules.api import api as api_blueprint
import threading

app = Flask(__name__)
app.register_blueprint(api_blueprint, url_prefix='/api')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    threading.Thread(target=app.run).start()
    api.reminder()
