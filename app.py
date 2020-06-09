from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp
import math
import random

app = Flask(__name__)
app.secret_key = "secret_key" 


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        # create a new board
        session["boardsize"] = int(request.form.get("boardsize"))
        setboard()
        return redirect(url_for("game"))


def setboard():
    session["board"] = [[None]*session["boardsize"] for _ in range(session["boardsize"])]
    session["turn"] = "X"
    session["xrow"] = [0]*session["boardsize"]
    session["xcol"] = [0]*session["boardsize"]
    session["orow"] = [0]*session["boardsize"]
    session["ocol"] = [0]*session["boardsize"]
    session["xdiagonal"] = 0
    session["xantidiagonal"] = 0
    session["odiagonal"] = 0
    session["oantidiagonal"] = 0
    session["movecount"] = 0
    session["winner"] = None
    session["movehistory"] = []
    return


@app.route("/game")
def game():
    return render_template("game.html", game=session["board"], turn=session["turn"], row=session["boardsize"], col=session["boardsize"])


@app.route("/play/<int:row>/<int:col>")
def play(row, col):
    
    session["board"][row][col] = session["turn"]

    if session["turn"] == "X":
        session["xrow"][row] += 1
        session["xcol"][col] += 1
        if row == col:
            session["xdiagonal"] += 1
        if row + col + 1 == session["boardsize"]:
            session["xantidiagonal"] += 1
        session["turn"] = "O"
    else:
        session["orow"][row] += 1
        session["ocol"][col] += 1
        if row == col:
            session["odiagonal"] += 1
        if row + col + 1 == session["boardsize"]:
            session["oantidiagonal"] += 1
        session["turn"] = "X"

    session["movecount"] += 1
    session["movehistory"].append([row, col])
    session["winner"] = checkWinner(session)

    if session["winner"]:
        if session["winner"] == "X":
            session.clear()
            return render_template("winner.html", winner="X wins")
        elif session["winner"] == "O":
            session.clear()
            return render_template("winner.html", winner="O wins")
        elif session["winner"] == "Draw":
            session.clear()
            return render_template("winner.html", winner="Draw")
    else:
        return redirect(url_for("game"))


def checkWinner(board):
    bs = board["boardsize"]
    if bs in board["xrow"] or bs in board["xcol"] or board["xdiagonal"] == bs or board["xantidiagonal"] == bs:
        return "X"
    elif bs in board["orow"] or bs in board["ocol"] or board["odiagonal"] == bs or board["oantidiagonal"] == bs:
        return "O"
    elif board["movecount"] == bs*bs:
        return "Draw"
    else:
        return None


@app.route("/resetgame")
def resetGame():
    # resets the board but not the session
    setboard()
    return redirect(url_for("game"))


@app.route("/undomove")
def undoMove():
    if session["movecount"] == 0:
        return redirect(url_for("game"))
    row, col = session["movehistory"].pop()
    session["board"][row][col] = None
    if session["turn"] == "X":
        session["orow"][row] -= 1
        session["ocol"][col] -= 1
        if row == col:
            session["odiagonal"] -= 1
        if row + col + 1 == session["boardsize"]:
            session["oantidiagonal"] -= 1
        session["movecount"] -= 1
        session["turn"] = "O"
    else:
        session["xrow"][row] -= 1
        session["xcol"][col] -= 1
        if row == col:
            session["xdiagonal"] -= 1
        if row + col + 1 == session["boardsize"]:
            session["xantidiagonal"] -= 1
        session["movecount"] -= 1
        session["turn"] = "X"
    return redirect(url_for("game"))


@app.route("/minmax")
def comPlay():
    cloneboard = session
    value, row, col = minimax(cloneboard, session["turn"])
    return redirect(url_for('play', row=row, col=col))


def minimax(board, turn):
    #base case
    winner = checkWinner(board)
    if winner == "X":
        return [1, None, None]
    elif winner == "O":
        return [-1, None, None]
    elif winner == "Draw":
        return [0, None, None]

    #recursive case
    moves = findempty(board)
    #case when there is nothing on the board
    if len(moves) == board["boardsize"]*board["boardsize"]:
        steprow = random.randint(0,board["boardsize"]-1)
        stepcol = random.randint(0,board["boardsize"]-1)
        return [None, steprow, stepcol]
    
    steprow = None
    stepcol = None
    if turn == "X":
        value = -math.inf
        for row, col in moves:
            board = move(board, row, col)
            value = max(value, minimax(board, "O")[0])
            board = unmove(board, row, col)
            steprow = row
            stepcol = col
    else:
        value = math.inf
        for row, col in moves:
           board = move(board, row, col)
           value = min(value, minimax(board, "X")[0])
           board = unmove(board, row, col)
           steprow = row
           stepcol = col
    return [value, steprow, stepcol]

def findempty(board):
    moves = []
    for i in range(len(board["board"])):
        for j in range(len(board["board"][i])):
            if board["board"][i][j] == None:
                moves.append([i, j])
    return moves


def move(board, row, col):
    board["board"][row][col] = board["turn"]

    if board["turn"] == "X":
        board["xrow"][row] += 1
        board["xcol"][col] += 1
        if row == col:
            board["xdiagonal"] += 1
        if row + col + 1 == board["boardsize"]:
            board["xantidiagonal"] += 1
        board["turn"] = "O"
    else:
        board["orow"][row] += 1
        board["ocol"][col] += 1
        if row == col:
            board["odiagonal"] += 1
        if row + col + 1 == session["boardsize"]:
            board["oantidiagonal"] += 1
        board["turn"] = "X"

    board["movecount"] += 1
    board["movehistory"].append([row, col])
    return board


def unmove(board, row, col):
    if board["movecount"] == 0:
        return board
    row, col = board["movehistory"].pop()
    board["board"][row][col] = None
    if board["turn"] == "X":
        board["orow"][row] -= 1
        board["ocol"][col] -= 1
        if row == col:
            board["odiagonal"] -= 1
        if row + col + 1 == board["boardsize"]:
            board["oantidiagonal"] -= 1
        board["movecount"] -= 1
        board["turn"] = "O"
    else:
        board["xrow"][row] -= 1
        board["xcol"][col] -= 1
        if row == col:
            board["xdiagonal"] -= 1
        if row + col + 1 == board["boardsize"]:
            board["xantidiagonal"] -= 1
        board["movecount"] -= 1
        board["turn"] = "X"
    return board