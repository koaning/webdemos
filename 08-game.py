import json
import matplotlib.pylab as plt
from fh_matplotlib import matplotlib2fasthtml
import pandas as pd
from fasthtml.common import Title, Img, Main, Div, P, H1, fast_app, serve, Input, Form, Script, RedirectResponse, Select, Option, NotStr, FileResponse, Td, Span, Button, Table, Thead, Tr, Th, Br, Response, Grid, Response
import numpy as np
from uuid import uuid4

app, rt = fast_app(hdrs=[Script(src='https://cdn.tailwindcss.com')])

inputs = [
    Div(
        Div(Img(src='static/castle.svg'), klass="flex justify-center items-center w-full px-6"),
        P(f"{i+1} pts", klass="text-center text-gray-600 font-bold"),
        Input(type="number", name=f"input-{i}", id=f"input-{i}", min=1, max=100, value=10, klass="w-1/2"),
    )
    for i in range(10)]

user_data = {}
logs = []

@app.get("/")
def home(request):
    global user_data
    contents = Title("Riddler Battles"), Main(
        Div(
            H1("Riddler Battleground", klass="text-3xl font-bold pb-4"),
            P("Game theory meets machine learning. Each castle is worth a certain number of points to attack and defend. Can you allocate your 100 armies and beat the machine?", klass="pb-4 text-gray-400"),
            Form(
                P('Allocate your armies.', klass="pb-4 text-gray-600 font-bold"),
                Div(*inputs, klass="grid grid-cols-10 gap-4"),
                Grid(
                    Button("Submit", 
                        hx_post="/army-update", hx_target="#response", hx_swap="innerHTML", hx_form="sklearn-form",
                        klass="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded w-full"),
                    Button("Submit 10x", 
                        hx_post="/army-update-10", hx_target="#response", hx_swap="innerHTML", hx_form="sklearn-form",
                        klass="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded w-full"),
                    Button("Reset", 
                        hx_post="/reset", hx_target="#response", hx_swap="innerHTML", hx_form="sklearn-form",
                        klass="bg-red-400 hover:bg-red-700 text-white font-bold py-2 px-4 rounded w-full"),
                ),
                id="sklearn-form"
            ),
        klass=''),
        Div(
            Div(id="response"),
            klass=''
        ),
        klass="m-8"
    )
    if request.cookies.get("user") is None:
        resp = RedirectResponse('/')
        uid = str(uuid4())
        user_data[uid] = []
        resp.set_cookie("user", uid)
        return resp
    return contents


def redo(s):
    return Span(f"Received {s} armies. Must allocate 100 in total!", klass="text-red-500 font-bold m-4")

def player_won(p1, p2):
    p1_score, p2_score = 0, 0
    for i in range(10):
        if p1[i] >= p2[i]:
            p1_score += 1 + i
        elif p1[i] < p2[i]:
            p2_score += 1 + i
    return p1_score >= p2_score

def result_table(p1, p2, rolling_chart):
    global logs
    p1, p2 = [int(i) for i in p1], [int(i) for i in p2]
    p1_score, p2_score = 0, 0
    rows = []
    for i in range(10):
        if p1[i] > p2[i]:
            p1_score += 1 + i
            rows.append(
                Tr(
                    Td(f"{i+1} pts"), 
                    Td(f"{p1[i]} pts"), 
                    Td(f"{p2[i]} pts"),
                    Td("Victory"),
                    Td(f"{p1_score}/{p2_score}"),
                )
            )
        elif p1[i] < p2[i]:
            p2_score += 1 + i
            rows.append(
                Tr(
                    Td(f"{i+1} pts"), 
                    Td(f"{p1[i]} pts"), 
                    Td(f"{p2[i]} pts"),
                    Td("Defeat"),
                    Td(f"{p1_score}/{p2_score}"),
                )
            )
        elif p1[i] == p2[i]:
            rows.append(
                Tr(
                    Td(f"{i+1} pts"), 
                    Td(f"{p1[i]} pts"), 
                    Td(f"{p2[i]} pts"),
                    Td("Draw"),
                    Td(f"{p1_score}/{p2_score}"),
                )
            )
    logs.append({"winner": p1, "loser": p2} if p1_score > p2_score else {"winner": p2, "loser": p1})
    print(logs[-1])
    return Div(
        Div(
            Grid(
                Div(
                    Div(
                        Img(src='static/fight.svg', klass='w-32'), 
                        klass="flex justify-center items-center w-full px-6 pt-8"
                    ),
                    P("The battle has ended!", klass="text-3xl font-bold pb-4 text-center"),
                    P("You won!" if p1_score > p2_score else "You did not win ...", klass="text-3xl font-bold pb-4 text-center"),
                ),
                Div(
                    rolling_chart
                )
            ),
        ),
        Table(
            Thead(
                Tr(
                    Th('Battle'),   
                    Th('Your army'),
                    Th('Opponent army'),
                    Th('Outcome'),
                    Th('Scores')
                )
            ),
            *rows
        )
    )

@matplotlib2fasthtml
def show_rolling_averages(user_data):
    print(pd.DataFrame({"outcomes": user_data}).rolling(10).mean())
    df = pd.DataFrame({"outcomes": user_data})
    plt.figure(figsize=(12, 5))
    plt.plot(df.rolling(10).mean()['outcomes'], label='Short term')
    plt.plot(df.expanding().mean()['outcomes'], label='Long term')
    plt.legend()

@app.post("/army-update")
def army_update(request, data: dict):
    values = [int(i) for i in data.values()]
    if sum(values) != 100:
        return redo(sum(values))
    r = np.random.random(10)
    r /= r.sum()
    r *= 100
    user = request.cookies.get("user")
    if user not in user_data:
        user_data[user] = []
    user_data[user].append(player_won(values, r.astype(int)))
    return Div(
        result_table(values, r.astype(int), rolling_chart=show_rolling_averages(user_data[user])),
    )

@app.post("/army-update-10")
def army_update_10(request, data: dict):
    for _ in range(9):
        army_update(request, data)
    return army_update(request, data)


@app.get("/logs")
def getlogs():
    return Response(json.dumps(logs))

@app.post("/reset")
def getlogs(request):
    global user_data
    user_data[request.cookies.get("user")] = []
    return Response('User data has been reset.')

if __name__ == "__main__":
    serve()
