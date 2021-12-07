import object
import fileType
import dynamoDB
import encryption
import s3
from cryptography.fernet import Fernet


class Document(object.Object):
    table_name = "document"
    attribute_key = ["name", "fileType"]
    fileType = fileType.FileType.text
    name = ''
    title = '' 
    password = ''
    description = ''
    notes = ''
    file = ''
    

    def __init__(self, name='', title="", password="", description="", notes="",file =""):
        self.name = name
        self.title = title,
        self.password = password,
        self.description = description,
        self.notes = notes
        self.file = file
        

def get_doc(doc):
    key_info={
        "name": doc.name,
        "fileType": doc.fileType
    }
    items = dynamoDB.get_item(doc.table_name, key_info)
    return items
    
    
def saveFile(name, title, notes, file="", password="", description=""):
    doc = Document(name)
    # get existing items to not be override when include new
    existingItems = get_doc(doc)
    print(existingItems['description'])
    items = []
    key = ""
    if existingItems['description'] :
        for i in existingItems['description']:
            key = i['key'].value
            if "_doc" in name:
                items.append({
                    'title': i['title'],
                    'notes': i['notes'],
                    'file': i['file'],
                    'key': i['key']
                })
            elif "_file" in name:
                items.append({
                    'title': i['title'],
                    'password': i['password'],
                    'description': i['description'],
                    'notes': i['notes'],
                    'key': i['key']
                })
    else:        
        key = encryption.getNewKey()
    
    if "_doc" in name:
        items.append({
            'title': encryption.encrypt(key, title),
            'notes': encryption.encrypt(key, notes),
            'file': file,
            'key': key
            }) 
    elif "_file" in name:
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
    
def getDocuments(doc, bucket=""):
    items = get_doc(doc)
    decodedItems = []
    if items:
        for i in items["description"]:
            key = i["key"] 
            if "_doc" in doc.name:
                fileURL = s3.getURL(bucket, i["file"])
                decodedItems.append({
                    "title": encryption.decrypt(key.value, i["title"]),
                    "fileName": i["file"],
                    "fileURL": fileURL,
                    "notes": encryption.decrypt(key.value, i["notes"])
                    })
            elif "_file" in doc.name:
                decodedItems.append({
                    "title": encryption.decrypt(key.value, i["title"]),
                    "description": encryption.decrypt(key.value, i["description"]),
                    "notes": encryption.decrypt(key.value, i["notes"])
                    })
    
    return decodedItems