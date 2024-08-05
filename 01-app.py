from flask import Flask, render_template_string

app = Flask(__name__)

counter = 0

# HTML template using Jinja2
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HTMX Counter Example</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
</head>
<body>
    <h1>HTMX Counter Example</h1>
    <p>Current count: <span id="counter">{{ counter }}</span></p>
    <button hx-post="/increment" hx-target="#counter" hx-swap="innerHTML">
        Increment
    </button>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(template, counter=counter)

@app.route('/increment', methods=['POST'])
def increment():
    global counter
    counter += 1
    return str(counter)

if __name__ == '__main__':
    app.run(debug=True)
