import os
import boto3
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# read the .env-sample, to load the environment variable.
dotenv_path = os.path.join(os.path.dirname(__file__), ".env-sample")
load_dotenv(dotenv_path)

username = "abc.xyz@gmail.com"
password = "#Abc1234"

client = boto3.client("cognito-idp", region_name="<region-name>")

print(os.getenv("COGNITO_USER_CLIENT_ID"))

# The below code, will do the sign-up
response = client.sign_up(
    ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
    Username=username,
    Password=password,
    UserAttributes=[{"Name": "email", "Value": username}],
)