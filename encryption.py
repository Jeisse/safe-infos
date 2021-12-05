from cryptography.fernet import Fernet

def getNewKey():
    key = Fernet.generate_key()
    return key
    
def encrypt(key, item):
    f = Fernet(key)
    encrypted = f.encrypt( item.encode())
    return encrypted
    
def decrypt(key, item):
    f = Fernet(key)
    print(item.value)
    # encrypted = b"...encrypted bytes..."
    decrypted = f.decrypt(item.value)
    # display the plaintext and the decode() method, converts it from byte to string
    return decrypted.decode()
