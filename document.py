import object
import fileType

class Document(object.Object):
    table_name = "document"
    attribute_key = ["name", "fileType"]
    fileType = fileType.FileType.text
    name = ''
    title = '' 
    password = ''
    description = ''
    notes = ''
    

    def __init__(self, name='', title="", password="", description="", notes=""):
        self.name = name
        self.title = title,
        self.password = password,
        self.description = description,
        self.notes = notes