import os
import boto3
import dynamoDB
import document
import json
import user
import s3
import encryption
from dotenv import load_dotenv, find_dotenv
from flask import Flask, redirect, url_for, render_template, json, request, session, send_file
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet


application = Flask(__name__)
Bootstrap(application)
FontAwesome(application)

load_dotenv(find_dotenv())
# read the .env-sample, to load the environment variable.
dotenv_path = os.path.join(os.path.dirname(__file__), ".env-sample")
load_dotenv(dotenv_path)
application.secret_key = os.getenv('APP_KEY')
UPLOAD_FOLDER = "uploads"
BUCKET = "testbucketjeisse"


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
    print(response)
    # Assign current user to session
    session['username'] = response["Username"]
    
    return redirect(url_for('logged'))


@application.route("/logged", methods=['POST', 'GET'])
def logged():
    if session['username'] :
        return render_template("home.html")
        
    return  render_template("index.html")

    
@application.route("/form")
def form():
    return render_template("form.html")    

@application.route("/newForm", methods=['POST'])
def newForm():
    
    title = request.form["docTitle"]
    password = request.form["docPassword"]
    description = request.form["docDescription"]
    notes = request.form["docNotes"]
    
    #should be user logged
    name = session['username']+"_file"
    doc = document.Document(name, title, password, description, notes)
    # for the first time so the DB is created
#   dynamoDB.initiate_db(doc)
    
    # get existing items to not be override when include new
    existingItems = document.get_doc(doc)
    
    items = []
    key = ""
    if existingItems['description'] :
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
        'title': encryption.encrypt(key,title),
        'password': encryption.encrypt(key, password),
        'description': encryption.encrypt(key, description),
        'notes': encryption.encrypt(key, notes),
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
    doc = document.Document(session["username"]+"_file") 
    items = document.get_doc(doc)
    decodedItems = []
    for i in items["description"]:
        key = i["key"]
        decodedItems.append({
            "title": encryption.decrypt(key.value, i["title"]),
            "description": encryption.decrypt(key.value, i["description"]),
            "notes": encryption.decrypt(key.value, i["notes"])
            })
    
    return render_template('docList.html', items=decodedItems) 


@application.route("/newFile")
def new_file():
    return render_template("newFile.html")  
    
@application.route("/saveFile", methods=['SET','POST'])
def saveFile():
    
    # save file on S3
    file = request.files['file']
    file.save(file.filename)
    s3.upload_file(f"{file.filename}", BUCKET, 'image/jpeg')

    title = request.form['docTitle']
    notes = request.form['docNotes']
    
    #should be user logged
    name = session['username']+"_doc"
    doc = document.Document(name=name, title=title, notes=notes, file=file)

    # get existing items to not be override when include new
    existingItems = document.get_doc(doc)
    
    items = []
    key = ""
    if existingItems['description'] :
        for i in existingItems['description']:
            key = i['key'].value
            items.append({
                'title': i['title'],
                'notes': i['notes'],
                'file': i['file'],
                'key': i['key']
            })
    else:        
        key = Fernet.generate_key()
    
    items.append({
        'title': encryption.encrypt(key, title),
        'notes': encryption.encrypt(key, notes),
        'file': file.filename,
        'key': key
        })  
    
    item = {
        "name": name,
        "fileType": doc.fileType,
        "description": items
    }
    dynamoDB.add_item(doc.table_name, item)
  
    return redirect(url_for("fileList"))
    
@application.route('/fileList')
def fileList():
    doc = document.Document(session["username"]+"_doc") 
    items = document.get_doc(doc)
    decodedItems = []
    if items:
        for i in items["description"]:
            key = i["key"] 
            fileURL = s3.getURL(BUCKET, i["file"])
            decodedItems.append({
                "title": decrypt(key.value, i["title"]),
                "fileName": i["file"],
                "fileURL": fileURL,
                "notes": decrypt(key.value, i["notes"])
                })
    
    return render_template('fileList.html', items=decodedItems) 

@application.route('/logout')
def logout():
   # remove the username from the session
   session.pop('username', None)
   return render_template("index.html")


# redirect to the home page when reaching admin endpoint
@application.route("/admin/")
def admin():
    return redirect(url_for("user", name="admin!"))

@application.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# We need to state this below due to our C9 Env
if __name__ == "__main__":
    application.run(host='0.0.0.0', port=8080, debug=True)
