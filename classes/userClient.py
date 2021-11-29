import os
import boto3

class User():
    
    username = ""
    password = ""
    
    def __init__(self, username, password):
        self.username = username,
        self.password = password
    
    
    def signupUser(self):
        client = boto3.client("cognito-idp", region_name="us-east-1")
    
        # sign-up on Cognito
        response = client.signup(
            ClientId=os.getenv("COGNITO_USER_CLIENT_ID"),
            Username=self.username,
            Password=self.password,
            UserAttributes=[{"Name": "email", "Value": self.username}],
        )
    
    