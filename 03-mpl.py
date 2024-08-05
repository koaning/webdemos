from fasthtml.common import * 
import numpy as np
import io
import base64
import matplotlib.pyplot as plt

app, rt = fast_app()  


count = 0
data = []


def generate_chart():
    plt.figure()
    plt.plot(range(len(data)), data)
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()
    return Img(src=f'data:image/jpg;base64, {my_base64_jpgData}')

@app.get("/")
def home():
    return Title("Matplotlib Demo"), Main(
        H1("Matplotlib Demo"),
        Div(f"You have pressed the button {count} times.", id="chart"),
        Button("Increment", hx_get="/increment", hx_target="#chart", hx_swap="innerHTML")
    )

@app.get("/increment")
def increment():
    print("updating chart")
    global data, count
    count += 1
    data.append(np.random.exponential(1))
    return Div(
        P(f"You have pressed the button {count} times."),
        generate_chart()
    )

if __name__ == "__main__":
    serve()
