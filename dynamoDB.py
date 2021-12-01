import logging
import boto3
import util
import object
from botocore.exceptions import ClientError

class DynamoDB:
    # //DynamoDB setup
    
    def create_table(self, table_name, key_schema, attribute_definitions, provisioned_throughput, region):
        
        try:
            dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            self.table = dynamodb_resource.create_table(TableName=table_name, KeySchema=key_schema, AttributeDefinitions=attribute_definitions,
                ProvisionedThroughput=provisioned_throughput)

            # Wait until the table exists.
            self.table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            
        except ClientError as e:
            logging.error(e)
            return False
        return True

 
        

    def store_an_item(self, region, table_name, item):
        try:
            dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            table = dynamodb_resource.Table(table_name)
            table.put_item(Item=item)
        
        except ClientError as e:
            logging.error(e)
            return False
        return True
        
        
     
    def get_an_item(self,region, table_name, key):
        try:
            dynamodb_resource = boto3.resource("dynamodb", region_name=region)
            table = dynamodb_resource.Table(table_name)
            response = table.get_item(Key=key)
            item = response['Item']
            print(item)
        
        except ClientError as e:
            logging.error(e)
            return False
        return True



def initiate_db(objectDB : object):
    d = DynamoDB()
    
    table_name = objectDB.table_name
    
    attribute_definitions = [ ]
    for i in objectDB.attribute_key:
            attribute_definitions.append(
                {
                    "AttributeName": i,
                    "AttributeType": "S"
                },
            )
        
    print(attribute_definitions)
    
    key_schema = [
        {
            "AttributeName": objectDB.attribute_key[0],
             "KeyType": "HASH"
        },
        {
            "AttributeName": objectDB.attribute_key[1],
             "KeyType": "RANGE"
        }
    ]
    
    print(key_schema)
    
    provisioned_throughput={
        "ReadCapacityUnits": 100,
        "WriteCapacityUnits": 1
    }
    
    d.create_table(table_name, key_schema, attribute_definitions,provisioned_throughput, util.Utils.region)
    

    

def add_item(table_name, item):
    d = DynamoDB()
    d.store_an_item(util.Utils.region, table_name, item)
    
    
def get_item(table_name, key_info):
    d = DynamoDB()
    d.get_an_item(util.Utils.region, table_name, key_info)
    



