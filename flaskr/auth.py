from crypt import methods
import imp


import functools
from operator import index
import re
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, template_rendered, url_for, escape
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

def validateUsername(username):
    if not username:
        return "Please enter a Username!"
    if len(username)<4:
        return "Username should be longer than 4 characters"
    return None

def validatePassword(password):
    if not password:
        return "Please enter a Password!"
    if len(password)<4:
        return "Password should be longer than 4 characters"
    return None


@bp.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()

        error = validateUsername(username)
        if error is None:
            error = validatePassword(password)
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)", 
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"Username {escape(username)} is taken."
            else:
                flash("Successfully Registered. Login to continue!")
                return redirect(url_for('auth.login'))

        flash(error)
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute("SELECT * FROM user WHERE username=?", (username,)).fetchone()
        if user is None:
            error = "No such username is registered."
        elif not check_password_hash(user['password'], password):
            error = "Password is not matching"
        
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            flash("Successfully logged in!")
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id, )).fetchone()

@bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('index'))

       
    
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("You must be logged in to do that!")
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route("/delete_account")
@login_required
def delete_account():
    db = get_db()
    try:
        db.execute("DELETE FROM user WHERE id =?", (session.get('user_id'), ))
        db.commit()
    except:
        flash(f"Failed! ")
        return redirect(url_for('index'))
    else:
        flash("Deletion Successful!")
        return redirect(url_for('index'))  
 