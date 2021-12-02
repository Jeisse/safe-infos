import os
import boto3
import dynamoDB
import document
import json
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
    
    return render_template("home.html")


@app.route("/logged")
def logged():
    return render_template("home.html")
    
@app.route("/newFile")
def new_file():
    return render_template("newFile.html")    

@app.route("/fileForm", methods=['POST'])
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
    
    test = []
    if existingItems != [] :
        for i in existingItems['description']:
            test.append({
                'title': i['title'],
                'password': i['password'],
                'description': i['description'],
                'notes': i['notes']
            })
    
    test.append({
        'title': title,
        'password': password,
        'description': description,
        'notes': notes
        })  
    print(test)    

    item = {
        "name": "test-Jeisse-011220211013",
        "fileType": doc.fileType,
        "description": test
    }
    dynamoDB.add_item(doc.table_name, item)
    return redirect(url_for("docList"))


@app.route("/docList", methods=['GET', 'POST'])
def docList(): 
    doc = document.Document("test-Jeisse-011220211013") 
    items = get_doc(doc)
    my_json = json.dumps(items)
   
    
    
    return render_template('doc.html', items=items["description"]) 

# redirect to the home page when reaching admin endpoint
# Both redirect and url_for must be import above before recognized by compiler
@app.route("/admin/")
def admin():
    return redirect(url_for("user", name="admin!"))


def get_doc(doc):
    key_info={
        "name": doc.name,
        "fileType": doc.fileType
    }
    items = dynamoDB.get_item(doc.table_name, key_info)
    return items



# We need to state this below due to our C9 Env
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
