from fasthtml.common import *
from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")


def fasthtml2flask(func):
    def wrapper(*args, **kwargs):
        return show(func(*args, **kwargs)).data
    return wrapper


@app.route("/")
@fasthtml2flask
def index():
    return Div(
        P('Hello, World!'), 
        Ul(
            Li('This is a list item'),
            Li('This is another list item')
        ),
    )

if __name__ == "__main__":
    app.run(debug=True)
