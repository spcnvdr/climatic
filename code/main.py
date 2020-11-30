#!/usr/bin/env python3
###########################################################################
# Stupid basic, ugly website that allows logins to view a secret web page #
# Probably not secure                                                     #
###########################################################################
from flask import Flask, render_template, redirect, url_for, request, \
    session, flash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)

app.storage_path = os.path.join(os.path.realpath(__file__), '..', 'storage')
app.secret_key = "ls[F4U3yYkzI#%^wfupqXC3@fXSp"

from code.controllers import CSVController

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            if request.path not in ["/login", "/logout"]:
                flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route("/")
@login_required
def home():
    now = datetime.now()
    date_str = now.ctime()
    if session["logged_in"]:
        return render_template("home.html", date=date_str)
    else:
        return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form["username"] != "admin" or \
                request.form["password"] != "admin":
            error = "Invalid credentials"
        else:
            session["logged_in"] = True
            flash("You have successfuly logged in")
            return redirect(url_for("home"))
    return render_template("login.html", error=error)


@app.route("/logout")
@login_required
def logout():
    session.pop("logged_in", None)
    flash("You have logged out")
    return redirect(url_for('login'))


@app.route("/sandbox")
@login_required
def sandbox():
    now = datetime.now()
    date_str = now.ctime()
    return render_template("sandbox.html", date=date_str)

# Test page route
@app.route("/testpage")
@login_required
def testpage():
    # Return the rendered HTML template
    return render_template("testpage.html")


@app.route("/theme/toggle", methods=["POST"])
def theme_toggle():
    mode = request.form.get('mode', 'light')
    session['theme'] = mode
    return mode



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
