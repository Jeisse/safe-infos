import os
import boto3
import document
import user
import s3
from media_identifier import identifier
from dotenv import load_dotenv, find_dotenv
from flask import Flask, redirect, url_for, render_template, json, request, session, send_file
from flask_bootstrap import Bootstrap
from flask_fontawesome import FontAwesome


application = Flask(__name__)
Bootstrap(application)
FontAwesome(application)
imt = identifier.MediaType()

load_dotenv(find_dotenv())
# read the .env-sample, to load the environment variable.
dotenv_path = os.path.join(os.path.dirname(__file__), ".env-sample")
load_dotenv(dotenv_path)
application.secret_key = os.getenv('APP_KEY')



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
    return render_template("signin.html")


@application.route("/signin")
def signin():
    return render_template("signin.html")


@application.route("/signinForm", methods=['POST'])
def signin_form():
    # gets username and password from the form and instanciate user object
    currentUser = user.User(request.form['username'], request.form['password'])
    response = user.signIn(currentUser, os)

    # Assign current user to session
    session['username'] = response["Username"]
    
    return redirect(url_for('logged'))


@application.route("/logged", methods=['POST', 'GET'])
def logged():
    if session['username'] :
        fileDoc = document.Document(session["username"]+"_file") 
        fileItems = document.getDocuments(fileDoc, os.getenv('BUCKET'))
        doc = document.Document(session["username"]+"_doc") 
        docItems = document.getDocuments(doc)
        return render_template("home.html", fileItems=fileItems, docItems=docItems)
        
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
    name = session['username']+"_doc"
    
    document.save_file(name, title, notes, "", password, description)
    return redirect(url_for("docList"))


@application.route("/docList", methods=['GET', 'POST'])
def docList(): 
    doc = document.Document(session["username"]+"_doc") 
    decodedItems = document.getDocuments(doc)
    
    return render_template('docList.html', items=decodedItems) 


@application.route("/newFile")
def new_file():
    return render_template("newFile.html")  
    
@application.route("/saveFile", methods=['SET','POST'])
def saveFile():
    # save file on S3
    file = request.files['file']
    file.save(file.filename)
    fileType = imt.get_type(file.filename)
    s3.uploadFile(f"{file.filename}", os.getenv('BUCKET'), fileType["mime"])

    #user logged
    name = session['username']+"_file"
    document.save_file(name, request.form['docTitle'], request.form['docNotes'], file.filename)
    
    return redirect(url_for("fileList"))
    
    
@application.route('/fileList')
def fileList():
    doc = document.Document(session["username"]+"_file") 
    decodedItems = document.getDocuments(doc, os.getenv('BUCKET'))
    
    return render_template('fileList.html', items=decodedItems) 

@application.route("/download/<filename>", methods=['GET'])
def download(filename):
    if request.method == 'GET':
        output = s3.downloadFile(filename, os.getenv('BUCKET'))
       
        return send_file(output, as_attachment=True)

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
