import object
import fileType
import dynamoDB

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