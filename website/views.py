from flask import Blueprint, flash, render_template, request, jsonify, url_for, redirect
import pyperclip
from random import choice, shuffle, randint
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from .models import User, Credentials
from . import db


views = Blueprint("views", __name__)


def generatePassword():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
               'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P',
               'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letters = [choice(letters) for _ in range(randint(8, 10))]
    password_symbols = [choice(symbols) for _ in range(randint(2, 4))]
    password_numbers = [choice(numbers) for _ in range(randint(2, 4))]

    password_list = password_letters + password_symbols + password_numbers

    shuffle(password_list)

    generated_password = "".join(password_list)
    pyperclip.copy(generated_password)
    return generated_password


@views.route('/')
@login_required
def home():
    all_credentials = Credentials.query.filter_by(user_id=current_user.id).order_by(Credentials.date).all()
    # for i in range(len(all_credentials)):
    #     all_credentials[i].date = len(all_credentials) - i
    db.session.commit()
    return render_template('home.html', user=current_user, credentials=all_credentials)


@views.route('/add', methods=["GET", "POST"])
@login_required
def add_credential():
    if request.method == "POST":
        website_app = request.form.get("website_app")
        email_username = request.form.get("email_username")
        return redirect(url_for("views.generate_password", website_app=website_app, email_username=email_username,
                                user=current_user, password=generatePassword))
    return render_template('add_credential.html', user=current_user)


@views.route("/generate_password", methods=["GET", "POST"])
def generate_password():
    if request.method == "POST":
        website_app = request.args.get("website_app")
        email_username = request.args.get("email_username")
        password = request.form.get("password")
        print(email_username)
        print(website_app)
        new_credential = Credentials(
            website_app=website_app,
            email_username=email_username,
            # password=generate_password_hash(password, method='sha256'),
            password=password,
            user_id=current_user.id
        )
        db.session.add(new_credential)
        db.session.commit()
        flash("Successfully Added.", category="success")
        return redirect(url_for("views.home", id=new_credential.id, user=current_user))
    return render_template("generate_password.html", password=generatePassword, user=current_user)


@views.route("/credential/edit", methods=["GET", "POST"])
def edit_credential():
    credential_id = request.args.get("id")
    credential = Credentials.query.get(credential_id)

    if request.method == "POST":
        rating = float(request.form.get("rating"))
        review = request.form.get("review")
        if 10 < rating < 0:
            flash("Rating Should Be Between 0 and 10.", category="error")
        elif 50 < len(review) < 4:
            flash("Review Should Be Between 5 and 50 Words.", category="error")
        else:
            credential.rating = rating
            credential.review = review
            db.session.commit()
            flash("Successfully Edited.", category="success")
            return redirect(url_for('views.home', user=current_user))
    return render_template("edit_credential.html", credential=credential, user=current_user)


@views.route("/credential/delete")
def delete_credential():
    credential_id = request.args.get("id")
    credential = Credentials.query.get(credential_id)
    db.session.delete(credential)
    db.session.commit()
    flash("Successfully Deleted.", category="error")
    return redirect(url_for('views.home'))


@views.route("/credential/copy")
def copy_credential():
    credential_id = request.args.get("id")
    credential = Credentials.query.get(credential_id)
    pyperclip.copy(credential.password)
    flash("Successfully Copied.", category="sucess")
    return redirect(url_for('views.home'))

