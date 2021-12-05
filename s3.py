import boto3


def upload_file(file_name, bucket, contentType):
    """
    Function to upload a file to an S3 bucket
    """
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL': 'public-read', 'ContentType': contentType})

    return response


def download_file(file_name, bucket):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource('s3')
    output = f"downloads/{file_name}"
    s3.Bucket(bucket).download_file(file_name, output)

    return output


def list_files(bucket):
    """
    Function to list files in a given S3 bucket
    """
    s3 = boto3.client('s3')
    contents = []
    try:
        for item in s3.list_objects(Bucket=bucket)['Contents']:
            print(item)
            contents.append(item)
    except Exception as e:
        pass

    return contents

def getURL(bucket, key):
    # Get the service client.
    s3t = boto3.client('s3')
    # Generate the URL to get 'key-name' from 'bucket-name'
    url = s3t.generate_presigned_url(
        ClientMethod='get_object',
        Params={
        'Bucket': bucket,
        'Key': key
        }
    )
    return url