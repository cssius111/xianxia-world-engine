from flask import Flask, render_template
from pathlib import Path

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def start_screen():
    return render_template("screens/start_screen.html")

@app.route("/choose")
def choose_start():
    return render_template("screens/choose_start.html")

@app.route("/roll")
def roll_screen():
    return render_template("screens/roll_screen.html")

if __name__ == "__main__":
    app.run(debug=True, port=5001)