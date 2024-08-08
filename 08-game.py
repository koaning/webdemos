import json
import matplotlib.pylab as plt
from fh_matplotlib import matplotlib2fasthtml
import pandas as pd
from fasthtml.common import Title, Img, Main, Div, P, H1, fast_app, serve, Input, Form, Script, RedirectResponse, A, Td, Span, Button, Table, Thead, Tr, Th, Br, Response, Grid, Response
import numpy as np
from scipy.stats import dirichlet
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
tournament_data = {}
logs = []

# Helper functions
def player_won(p1, p2):
    p1_score, p2_score = 0, 0
    for i in range(10):
        if p1[i] > p2[i]:
            p1_score += 1 + i
        elif p1[i] < p2[i]:
            p2_score += 1 + i
    return p1_score > p2_score


def generate_opponent(winner=[10, 10, 10, 10, 10, 10, 10, 10, 10, 10]):
    rvs = dirichlet.rvs((np.array(winner) + 1)) * 100
    rvs = np.floor(rvs)[0]
    s = rvs.sum()
    if s < 100:
        rvs[-1] += (100 - s)
    return rvs.astype(int).tolist()


def result_table(p1, p2):
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
                    Td(f"{p1[i]} pts", klass="font-bold"), 
                    Td(f"{p2[i]} pts"),
                    Td("Victory", klass="text-green-500"),
                    Td(f"{p1_score}/{p2_score}"),
                )
            )
        elif p1[i] < p2[i]:
            p2_score += 1 + i
            rows.append(
                Tr(
                    Td(f"{i+1} pts"), 
                    Td(f"{p1[i]} pts"), 
                    Td(f"{p2[i]} pts", klass="font-bold"),
                    Td("Defeat", klass="text-red-500"),
                    Td(f"{p1_score}/{p2_score}"),
                )
            )
        elif p1[i] == p2[i]:
            rows.append(
                Tr(
                    Td(f"{i+1} pts"), 
                    Td(f"{p1[i]} pts"), 
                    Td(f"{p2[i]} pts"),
                    Td("Draw", klass="text-gray-400"),
                    Td(f"{p1_score}/{p2_score}"),
                )
            )
    
    logs.append({"winner": p1, "loser": p2} if p1_score > p2_score else {"winner": p2, "loser": p1})
    if len(logs) > 100:
        logs.pop(0)
    
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
        ),
        A("Got what it takes to compete?", href="/compete", klass="text-blue-500 font-bold"),
    )

@matplotlib2fasthtml
def show_rolling_averages(user_data):
    df = pd.DataFrame({"outcomes": user_data})
    plt.figure(figsize=(12, 5))
    plt.plot(df.rolling(10).mean()['outcomes'], label='Short term')
    plt.plot(df.expanding().mean()['outcomes'], label='Long term')
    plt.legend()


# Routes related to the landing page
@app.get("/")
def home(request):
    global user_data
    contents = Title("Nerdsnipe Castles"), Main(
        Div(
            H1("Nerdsnipe Castles", klass="text-3xl font-bold pb-4"),
            P("Game theory meets machine learning. Each castle is worth a certain number of points to attack and defend. The player with the most armies on a castle wins the castle and all the points that belong to it. Can you allocate your 100 armies and beat the machine?", klass="pb-4 text-gray-400"),
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


@app.post("/reset")
def reset(request):
    global user_data
    user_data[request.cookies.get("user")] = []
    return Response('User data has been reset.')


@app.post("/army-update")
def army_update(request, data: dict):
    values = [int(i) for i in data.values()]
    if sum(values) != 100:
        return redo(sum(values))
    if (not logs) or len(logs) < 10:
        r = np.array([9, 10, 10, 10, 10, 10, 10, 10, 10, 11])
    else:
        inspiration = logs[-3]["winner"]
        for _ in range(2):
            # We look at the past to see if we can beat the opponent
            # A bit lazy, but we try to generate a new opponent until we win
            r = np.array(generate_opponent(inspiration))
            if player_won(r, values):
                break
    user = request.cookies.get("user")
    if user not in user_data:
        user_data[user] = []
    outcome = player_won(values, r.astype(int))
    user_data[user].append(outcome)
    print(f"{user} used {values} against {r} and {'won' if outcome else 'lost'}.")
    return Div(
        result_table(values, r.astype(int)),
    )

@app.post("/army-update-10")
def army_update_10(request, data: dict):
    for _ in range(9):
        army_update(request, data)
    return army_update(request, data)


@app.get("/logs")
def getlogs():
    return Response(json.dumps(logs))


@app.get("/compete")
def getlogs(request):
    global user_data
    contents = Title("Nerdsnipe Castles"), Main(
        Div(
            H1("Nerdsnipe Castle - The Tournament[tm]", klass="text-3xl font-bold pb-4"),
            P("Have you faced the computer and did you manage to win long term? Dare to compete on a grand scale against your fellow humans? Enter the tournament below to find out!", klass="pb-4 text-gray-400"),
            Form(
                P('Allocate your armies.', klass="pb-4 text-gray-600 font-bold"),
                Div(*inputs, klass="grid grid-cols-10 gap-4"),
                Grid(
                    Button("Submit", 
                        hx_post="/tournament-update", hx_target="#response", hx_swap="innerHTML", hx_form="sklearn-form",
                        klass="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded w-full"),
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
        resp = RedirectResponse('/compete')
        uid = str(uuid4())
        user_data[uid] = []
        resp.set_cookie("user", uid)
        return resp
    return contents


def tournament_table(highlight=None):
    rows = []
    for user in tournament_data:
        ratio = np.mean([player_won(tournament_data[user], tournament_data[name]) for name in tournament_data if name != user])
        rows.append(
            (user, ratio)
        )
    
    rows = [
        Tr(
            Td(user, klass="font-bold" if highlight == user else None), 
            Td(np.round(ratio * 100, 4), klass="font-bold" if highlight == user else None)
        ) for user, ratio in sorted(rows, key=lambda x: x[1], reverse=True)
    ]
    return Table(
        Thead(
            Tr(
                Th('Player'),   
                Th('Win ratio'),
            )
        ),
        *rows
    )

@app.post("/tournament-update")
def tournament_update(request, data: dict):
    global tournament_data
    user = request.cookies.get("user")
    values = [int(i) for i in data.values()]
    if sum(values) != 100:
        return redo(sum(values))
    for i in range(10):
        tournament_data[f'easy-bot-{i}'] = generate_opponent([10 for _ in range(10)])
    tournament_data[user] = values
    ratio = np.mean([player_won(values, tournament_data[name]) for name in tournament_data if name != user])
    return Div(
        f'We compared against {len(tournament_data)} other players and you were able to beat {np.round(ratio, 2) * 100}% of them.',
        tournament_table(highlight=user)
    )


if __name__ == "__main__":
    serve(port=8080)
