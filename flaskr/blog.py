from crypt import methods
from datetime import datetime
import functools
import imp
import re
from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, template_rendered, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)

@bp.route("/")
def index():
    posts = get_db().execute("SELECT post.id, title, body, created, author_id, username FROM post LEFT OUTER JOIN user ON post.author_id = user.id ORDER BY created DESC").fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method=="GET":
        return render_template('blog/create.html')
    else:
        title = request.form['title']
        body = request.form['body']
        if title is None:
            flash("Title can't be empty")
            return render_template('blog/create.html')
        elif body is None:
            flash("Body can't be empty")
            return render_template("blog/create.html")
        else:
            db = get_db()
            try:
                db.execute("INSERT INTO post (author_id, title, body) VALUES (?,?,?)", (g.user['id'], title, body))
                db.commit()
            except:
                flash("Problem Posting Content. Try Again or contact admin if problem persists")
                return render_template("blog/create.html")
            else:
                flash("Successfully Posted content.")
                return redirect(url_for('blog.index'))

def get_post_by_id(id, check_reqd=True):
    post = get_db().execute("SELECT post.id, title, body, created, author_id, username FROM post  LEFT OUTER JOIN user ON post.author_id = user.id WHERE post.id=?", (id,)).fetchone()
    if post is None:
        #No such post exists
        abort(404, "No Such Post Exists!")
    elif check_reqd and post['author_id'] != g.user['id']:
        #Trying to delete a post that doesn't belong to this user
        abort(403)
    else:
        return post

@bp.route("/<int:pid>")
def view(pid):
    post = get_post_by_id(pid, False)
    return render_template("blog/view.html", post=post)

@bp.route("/<int:pid>/update", methods=['GET', 'POST'])
@login_required
def update(pid):
    post = get_post_by_id(pid, True)
    if request.method == 'GET':
        return render_template("blog/update.html", post=post)
    else:
        db = get_db()
        nt = request.form['title']
        nb = request.form['body']
        now = datetime.now()
        if nt is None:
            flash("Title can't be empty!")
            return render_template("blog/update.html", post=post)
        elif nb is None:
            flash("Body can't be empty!")
            return render_template("blog/update.html", post=post)
        
        try:
            db.execute("UPDATE post SET title=?, body=?, created=? WHERE id=?", (nt, nb, now, pid))
            db.commit()
        except:
            flash("Unable to Update! Try again or Contact Admin")
            return render_template("blog/update.html", post=post)
        else:
            flash("Succesfully Updated!")
            return redirect(url_for('blog.view', pid=pid))
            

@bp.route("/<int:pid>/delete", methods=["GET", "POST"])
@login_required
def delete(pid):
    if request.method=="GET":
        post = get_post_by_id(pid, True)
        return render_template("blog/delete.html", post=post)
    else:
        db = get_db()
        try:
            db.execute("DELETE FROM post WHERE id=?", (pid, ))
            db.commit()
        except:
            flash("Unable to Delete! Try again or Contact Admin")
            return redirect(url_for('view', pid=pid))
        else:
            flash("Deletion Successful")
            return redirect(url_for('blog.index'))
    
