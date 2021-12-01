import object
import fileType

class Document(object.Object):
    table_name = "document"
    attribute_key = ["name", "fileType"]
    fileType = fileType.FileType.text
    title = '' 
    password = ''
    description = ''
    notes = ''

    def __init__(self, title, password, description, notes):
        self.title = title,
        self.password = password,
        self.description = description,
        self.notes = notes