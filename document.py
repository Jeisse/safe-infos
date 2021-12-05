import object
import fileType
import dynamoDB
import encryption
import s3

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
    
    
def saveFile(name, title, notes, file):
    doc = Document(name)
    # get existing items to not be override when include new
    existingItems = get_doc(doc)
    print(existingItems['description'])
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
        key = encryption.getNewKey()
    
    items.append({
        'title': encryption.encrypt(key, title),
        'notes': encryption.encrypt(key, notes),
        'file': file,
        'key': key
        })  
    
    item = {
        "name": name,
        "fileType": doc.fileType,
        "description": items
    }
    dynamoDB.add_item(doc.table_name, item)
    
def getFiles(doc, bucket):
    items = get_doc(doc)
    decodedItems = []
    if items:
        for i in items["description"]:
            key = i["key"] 
            fileURL = s3.getURL(bucket, i["file"])
            decodedItems.append({
                "title": encryption.decrypt(key.value, i["title"]),
                "fileName": i["file"],
                "fileURL": fileURL,
                "notes": encryption.decrypt(key.value, i["notes"])
                })
    
    return decodedItems
    
  