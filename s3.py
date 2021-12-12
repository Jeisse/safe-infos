import boto3


def uploadFile(file_name, bucket, contentType):
    object_name = file_name
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name, ExtraArgs={'ACL': 'public-read', 'ContentType': contentType})

    return response


def downloadFile(file_name, bucket):
    print(file_name)
    s3 = boto3.resource('s3')
    output = f"{file_name}"
    s3.Bucket(bucket).download_file(file_name, output)

    return output


def listFiles(bucket):
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