from fasthtml.common import * 
import numpy as np
import io
import base64
import matplotlib.pyplot as plt

app, rt = fast_app()  
count = 0
plotdata = []

def generate_chart():
    plt.figure()
    plt.plot(range(len(plotdata)), plotdata)
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()
    return Img(src=f'data:image/jpg;base64, {my_base64_jpgData}')


@app.get("/")
def home():
    return Title("Matplotlib Demo"), Main(
        H1("Matplotlib Demo"),
        P("Nothing too fancy, but still kind of fancy."),
        Div(f"You have pressed the button {count} times.", id="chart"),
        Button("Increment", hx_get="/increment", hx_target="#chart", hx_swap="innerHTML"),
        Input(type="range", name="slider", hx_include="[name='email']", min=1, max=10, hx_trigger="input", hx_post="/increment_slider", hx_target="#chart", hx_swap="innerHTML", hx_vals="value"),
        style="margin: 30px"
    )


@app.get("/increment/")
def increment():
    global plotdata, count
    count += 1
    plotdata.append(np.random.exponential(1))
    print(plotdata)
    return Div(
        generate_chart(),
        P(f"You have pressed the button {count} times."),
    )


@app.post("/increment_slider/")
def increment_i(data: dict):
    global plotdata, count
    count += 1
    plotdata.append(float(data['slider']))
    return Div(
        generate_chart(),
        P(f"You have pressed the button {count} times."),
    )

serve()