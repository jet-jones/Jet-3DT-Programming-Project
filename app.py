from flask import Flask, render_template, flash, redirect, url_for, request, session
import classes.forms
from functools import wraps
from classes.user import User
from classes.list import List
from classes.searcher import get

from configQuotes import Config

config = Config()

app = Flask(__name__)

app.secret_key = config.secret_key

def is_loggged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("Unauthorised access. Please log in.","danger")
            return redirect(url_for('login'))
    return wrap

def is_owner(f):
    @wraps(f)
    def wrap(*args, **kwargs):  
        return("")

@app.route("/", methods=["GET", "POST"])
def home():
    list = List()
    allLists = list.retrieveAllLists()
    extra = list.getExtraInfo(allLists)
    return render_template("home.html",allLists = allLists, extra = extra, showUsernames = True)

"""
@app.errorhandler(404)
def page_not_found():
    app.logger.info("404 encountered")
    return render_template("errors/404.html")"""

@app.route("/new", methods=["GET", "POST"])
@is_loggged_in
def new():
    form = classes.forms.ListForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        description = form.description.data
        sites = form.sites.data

        list = List()
        
        list.addList(name,description,sites,session['user_id'])
        return redirect(url_for("sessionuser"))

    return render_template("new.html", form = form)


@app.route("/sessionuser")
@is_loggged_in
def sessionuser():
    list = List()
    userLists = list.retrieveUserLists(session['username'])
    if userLists:
        extra = list.getExtraInfo(userLists)
        return render_template("user.html", name = session['username'], userLists = userLists, extra = extra)
    else:
        flash("you do not have any lists")
        return redirect(url_for("new"))

@app.route("/edit/<string:list_name>", methods = ["GET", "POST"])
def edit(list_name):
    list = List()
    list_id = list.retrieveListByName(list_name)
    sites = list.retrieveSites(list_id)

    form = classes.forms.EditForm(request.form)
    if request.method == "POST" and form.validate():
        site = form.site.data
        list.addSite(site,list_id)
        return redirect(url_for("edit", list_name = list_name))
    
    return render_template("edit.html", sites = sites, list_name = list_name, form = form)

@app.route("/delete/<string:list_name>")
def delete(list_name):
    list = List()
    success = list.deleteList(session['user_id'],list_name)

    if success:
        flash("Your quote was successfully deleted from the collection.","success")
    else:
        flash("Something went wrong. Either that quote doesn't exist or you don't have authorisation to delete it.","danger")
    
    return redirect(url_for("sessionuser"))

@app.route("/deletesite/<string:list_name>/<string:siteid>")
def deleteSite(list_name,siteid):
    list = List()
    listid = list.retrieveListByName(list_name)
    list.deleteSiteFromList(siteid,listid)
    return redirect(url_for("edit",list_name = list_name))


@app.route("/user/<string:user_name>")
def user(user_name):
    list = List()
    userLists = list.retrieveUserLists(user_name)
    extra = list.getExtraInfo(userLists)

    if userLists:
        return render_template("user.html", name=user_name, userLists = userLists, extra = extra)

    else:
        flash("none")
        return redirect(url_for("home"))


@app.route("/list/<string:list_name>", methods = ["GET", "POST"])
def list(list_name):
    list = List()

    currentList = list.retrieveListByName(list_name)
    
    if currentList:
        form = classes.forms.SearchForm(request.form)
        sites = list.retrieveSites(currentList)

        if request.method == "POST" and form.validate():
            search = form.search.data
            results = get(search, sites)
            
            if results:
                return render_template("results.html", results = results)

        return render_template("sitesearch.html", name = list_name, form=form, sites = sites)

    else:
        return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = classes.forms.RegisterForm(request.form)

    if request.method == "POST" and form.validate():

        username = form.username.data
        email = form.email.data
        password = form.password.data

        user = User()
        success = user.insertUser(username, password, email)

        if success:
            flash("You have now registered. ", "success")
            return redirect(url_for("login"))
        else:
            flash("This user already exists. Try again.", "danger")
            redirect(url_for("register"))

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    
    form = classes.forms.LoginForm(request.form)

    if request.method == "POST" and form.validate():
        username = form.username.data
        password = form.password.data

        user = User()
        auth = user.authenticateUser(username, password)

        if auth:
            
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = auth

            #flash("You are now logged in, " + username + ".", "success")
            return redirect(url_for("home"))
        else:
            error = "Incorrect username or password."
            return render_template("login.html", form=form, error=error)
    
    return render_template("login.html", form=form)

@app.route("/logout")
@is_loggged_in
def logout():
    session.clear()

    flash("You are now logged out.","success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)