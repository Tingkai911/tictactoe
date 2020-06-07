from flask import Flask, render_template, session, redirect, url_for, request
from flask_session import Session
from tempfile import mkdtemp

app = Flask(__name__)

app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        # create a new board
        session["boardsize"] = int(request.form.get("boardsize"))
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
        return redirect(url_for("game"))


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

    winner = checkWinner(row, col)

    if winner:
        session.clear()
        if winner == "X":
            return render_template("winner.html", winner="X wins")
        elif winner == "O":
            return render_template("winner.html", winner="O wins")
        elif winner == "Draw":
            return render_template("winner.html", winner="Draw")
    else:
        return redirect(url_for("game"))



def checkWinner(row, col):
    bs = session["boardsize"]
    if session["xrow"][row] == bs or session["xcol"][col] == bs or session["xdiagonal"] == bs or session["xantidiagonal"] == bs:
        return "X"
    if session["orow"][row] == bs or session["ocol"][col] == bs or session["odiagonal"] == bs or session["oantidiagonal"] == bs:
        return "O"
    elif session["movecount"] == bs*bs:
        return "Draw"
    else:
        return None