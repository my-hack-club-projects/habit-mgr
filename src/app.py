from flask import Flask, render_template
from modules.api import api

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    api.start_reminder()
    app.run(debug=True)
