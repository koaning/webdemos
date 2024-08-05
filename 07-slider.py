from fasthtml.common import Title, Img, Main, Div, P, H1, fast_app, serve, Input, Form, Script, Select, Option
import numpy as np
import io
import base64
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split


app, rt = fast_app(hdrs=[Script(src='https://cdn.tailwindcss.com')])
count = 0
data = []
df = pd.read_csv('data.csv')
X_train, X_test, y_train, y_test = train_test_split(df[['x']].values, df['y'], test_size=0.2, random_state=0)


def show_charts(noise=1, n_estimators=1, model='boosted'):
    global data
    plt.figure(figsize=(12, 10))
    np.random.seed(0)
    y_train_ = y_train + np.random.exponential(noise, len(y_train))
    y_test_ = y_test + np.random.exponential(noise, len(y_test))
    if model == "boosted":
        mod = HistGradientBoostingRegressor(max_iter=n_estimators, random_state=0)
    else:
        mod = RandomForestRegressor(n_estimators=n_estimators, random_state=0)
    mod.fit(X_train, y_train_)
    xs = np.linspace(0, df['x'].max(), 100)
    
    plt.subplot(211)
    plt.scatter(X_train.reshape(-1), y_train_)
    plt.plot(xs, mod.predict(xs.reshape(-1, 1)), color='red')
    plt.title('Train performance')

    plt.subplot(212)
    plt.title('Test performance')
    plt.scatter(X_test.reshape(-1), y_test_)
    plt.plot(xs, mod.predict(xs.reshape(-1, 1)), color='red')

    # Perform a trick at the end to convert the plot to an image
    my_stringIObytes = io.BytesIO()
    plt.savefig(my_stringIObytes, format='jpg')
    my_stringIObytes.seek(0)
    my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()
    return Img(src=f'data:image/jpg;base64, {my_base64_jpgData}')


@app.get("/")
def home():
    return Title("Matplotlib Demo"), Main(
        Div(
            H1("Slider playground", klass="text-3xl font-bold pb-4"),
            P("This is a simple example of how to use sliders to update a chart.", klass="pb-4 text-gray-400"),
            Form(
                P('Increase the noise.'),
                Input(type="range", name="noise", min=1, max=100),
                P('Increase the number of estimators.'),
                Input(type="range", name="estimators", min=1, max=300),
                Select(
                    Option('Boosted Ensemble', value='boosted'),
                    Option('Random Forest', value='forest'),
                    name='model', form='sklearn-form',
                ),
                id="sklearn-form", hx_trigger="input", hx_post="/slider-update", hx_target="#chart", hx_swap="innerHTML"
            ),
        klass='col-span-1'),
        Div(
            Div(show_charts(), id="chart"),
            klass='col-span-3'
        ),
        klass="grid grid-cols-4 m-8"
    )


@app.post("/slider-update")
def slider_update(data: dict):
    print("updating chart")
    print(data)
    return show_charts(noise=float(data['noise']), n_estimators=int(data['estimators']), model=data['model'])


if __name__ == "__main__":
    serve()
