import object
import fileType

class Document(object.Object):
    table_name = "document2"
    attribute_key = ["name", "fileType"]
    name = '' 
    fileType = fileType.FileType.text
    description = ''
    notes = ''

    def __init__(self, name, description, notes):
        self.name = name, 
        self.description = description,
        self.notes = notes