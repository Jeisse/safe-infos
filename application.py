import os
import boto3
import dynamoDB
import document
import json
import user
from dotenv import load_dotenv, find_dotenv
from flask import Flask, redirect, url_for, render_template, json, request
from flask_bootstrap import Bootstrap
from cryptography.fernet import Fernet

application = Flask(__name__)
Bootstrap(application)

load_dotenv(find_dotenv())
# read the .env-sample, to load the environment variable.
dotenv_path = os.path.join(os.path.dirname(__file__), ".env-sample")
load_dotenv(dotenv_path)


@application.route("/")
def home():
    # return the home page
    return render_template("index.html")

@application.route("/signup")
def signup():
    return render_template("signup.html")

@application.route("/signupForm", methods=['POST'])
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


@application.route("/confirmSignUp")
def confirm_signup():
    return render_template("confirmSignup.html")


@application.route("/confirmSignUpForm", methods=['POST'])
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


@application.route("/signin")
def signin():
    return render_template("signin.html")


@application.route("/signinForm", methods=['POST'])
def signin_form():

    # gets username and password from the form
    username = request.form['username']
    password = request.form['password']

    client = boto3.client("cognito-idp", region_name="us-east-1")

    # Initiating the Authentication
    # USER_PASSWORD_AUTH needs to be configured on Cognito (General Settings > App Client > Auth Flow Configuration)
    response = client.initiate_auth(
        ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
    )

    # Getting the user AccessToken details from the JSON response
    access_token = response["AuthenticationResult"]["AccessToken"]
    
    response = client.get_user(AccessToken=access_token)
    
    # userLogged = user.User(response["Username"], response["UserAttributes"][0]["Value"])
    # return redirect(url_for("logged", user=userLogged))
    return render_template("home.html")


@application.route("/logged", methods=['POST', 'GET'])
def logged():
    return render_template("home.html")
    
@application.route("/newFile")
def new_file():
    return render_template("newFile.html")    

@application.route("/fileForm", methods=['POST'])
def newFile():
    
    title = request.form["docTitle"]
    password = request.form["docPassword"]
    description = request.form["docDescription"]
    notes = request.form["docNotes"]
    
    #should be user logged
    name = "test-Jeisse-011220211013"
    doc = document.Document(name, title, password, description, notes)
    # for the first time so the DB is created
#   dynamoDB.initiate_db(doc)
    
    # get existing items to not be override when include new
    existingItems = get_doc(doc)
    
    items = []
    key = ""
    if existingItems != [] :
        for i in existingItems['description']:
            key = i['key'].value
            items.append({
                'title': i['title'],
                'password': i['password'],
                'description': i['description'],
                'notes': i['notes'],
                'key': i['key']
            })
    else:        
        key = Fernet.generate_key()
    
    items.append({
        'title': encryptation(key, title),
        'password': encryptation(key, password),
        'description': encryptation(key, description),
        'notes': encryptation(key, notes),
        'key': key
        })  

    
    item = {
        "name": name,
        "fileType": doc.fileType,
        "description": items
    }
    dynamoDB.add_item(doc.table_name, item)
    return redirect(url_for("docList"))


@application.route("/docList", methods=['GET', 'POST'])
def docList(): 
    doc = document.Document("test-Jeisse-011220211013") 
    items = get_doc(doc)
    decodedItems = []
    for i in items["description"]:
        key = i["key"]
        decodedItems.append({
            "title": decrypt(key.value, i["title"]),
            "description": decrypt(key.value, i["description"]),
            "notes": decrypt(key.value, i["notes"])
            })
    
    return render_template('doc.html', items=decodedItems) 

# redirect to the home page when reaching admin endpoint
# Both redirect and url_for must be import above before recognized by compiler
@application.route("/admin/")
def admin():
    return redirect(url_for("user", name="admin!"))


def get_doc(doc):
    key_info={
        "name": doc.name,
        "fileType": doc.fileType
    }
    items = dynamoDB.get_item(doc.table_name, key_info)
    return items

def encryptation(key, item):
    f = Fernet(key)
    encrypted = f.encrypt( item.encode())
    return encrypted
    
def decrypt(key, item):
    f = Fernet(key)
    print(item.value)
    # encrypted = b"...encrypted bytes..."
    decrypted = f.decrypt(item.value)
    # display the plaintext and the decode() method, converts it from byte to string
    return decrypted.decode()

@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# We need to state this below due to our C9 Env
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080, debug=True)
