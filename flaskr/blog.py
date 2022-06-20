from cmath import log
from crypt import methods
import functools
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, template_rendered, url_for, escape
)
from .auth import login_required
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

from flaskr import auth

bp = Blueprint('blog', __name__, url_prefix='/blog')




@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM user WHERE id = ?", (user_id, )).fetchone()


@bp.route("/create_post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method=="GET":
        return render_template('blog/create.html')
    else:
        db = get_db()
        authid = session.get('user_id')
        title = request.form['title']
        cont = request.form['cont']
        error = None
        if title is None:
            error = "Title can't be empty"
        elif cont is None:
            error = "Body can't be empty"
        
        if error is None:
            try:
                db.execute("INSERT INTO post (author_id, title, body) VALUES (?, ?, ?)", (authid, title, cont))
                db.commit()
            except:
                error = "Insertion Failed"
            else:
                flash("Posted Successfully!")
                return redirect(url_for('index'))
        return redirect(url_for('create_post'))
    

@bp.route("/view_posts", methods=["GET", "POST"])
@login_required
def view_posts():
    if request.method=="GET":
        db = get_db()
        res = db.execute("SELECT * FROM post").fetchall()
        auths=[]
        for result in res:
            auths.append( db.execute("SELECT username FROM user, post WHERE user.id=post.author_id AND post.id = ?", (result['id'],)).fetchone()[0] )        
        return render_template('blog/view.html', res=res, auths=auths)               
            