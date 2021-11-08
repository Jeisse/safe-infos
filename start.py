import os
import boto3
from dotenv import load_dotenv, find_dotenv
from flask import Flask, redirect, url_for, render_template, json, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

load_dotenv(find_dotenv())
# read the .env-sample, to load the environment variable.
dotenv_path = os.path.join(os.path.dirname(__file__), ".env-sample")
load_dotenv(dotenv_path)


@app.route("/")
def home():
    # return the home page
    return render_template("index.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signupForm", methods=['POST'])
def signup_form():
    # gets username and password from the form
    username = request.form['username']
    password = request.form['password']

    client = boto3.client("cognito-idp", region_name="us-east-1")

    # sign-up on Cognito
    response = client.sign_up(
        ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
        Username=username,
        Password=password,
        UserAttributes=[{"Name": "email", "Value": username}],
    )
    return render_template("confirmSignup.html")


@app.route("/confirmSignUp")
def confirm_signup():
    return render_template("confirmSignup.html")


@app.route("/confirmSignUpForm", methods=['POST'])
def confirm_signup_form():
    username = request.form['username']
    confirm_code = request.form['confirm_code']

    client = boto3.client('cognito-idp', region_name="us-east-1")
    response = client.confirm_sign_up(
        ClientId=os.getenv('COGNITO_USER_CLIENT_ID'),
        Username=username,
        ConfirmationCode=confirm_code
    )
    return render_template("index.html")


@app.route("/signin")
def signin():
    return render_template("signin.html")


@app.route("/signinForm", methods=['POST'])
def signin_form():
    # gets username and password from the form
    username = request.form['username']
    password = request.form['password']

    client = boto3.client("cognito-idp", region_name="us-east-1")

    # sign-in on Cognito
    response = client.sign_in(
        ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
        Username=username,
        Password=password,
        UserAttributes=[{"Name": "email", "Value": username}],
    )
    return render_template("index.html")


@app.route("/logged")
def logged():
    return render_template("home.html")


# redirect to the home page when reaching admin endpoint
# Both redirect and url_for must be import above before recognized by compiler
@app.route("/admin/")
def admin():
    return redirect(url_for("user", name="admin!"))


# We need to state this below due to our C9 Env
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
