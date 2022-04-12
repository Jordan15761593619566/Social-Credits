from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Home page route
@app.route('/')
def root():
    return render_template('home.html', page_title = 'Home')


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)