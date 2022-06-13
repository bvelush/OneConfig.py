import argparse
from venv import create
from cryptography.fernet import Fernet


def create_key(key_file_path: str) -> None:
    key = Fernet.generate_key()

    # string the key in a file
    with open(key_file_path, 'wb') as keyfile:
        keyfile.write(key)


def encrypt(key_file_path: str, input_file_path: str, out_file_path: str) -> None:
    # opening the key
    with open(key_file_path, 'rb') as keyfile:
        key = keyfile.read()
    
    # using the generated key
    fernet = Fernet(key)
    
    # opening the original file to encrypt
    with open(input_file_path, 'rb') as file:
        in_file = file.read()
        
    # encrypting the file
    encrypted = fernet.encrypt(in_file)
    
    # opening the file in write mode and 
    # writing the encrypted data
    with open(out_file_path, 'wb') as encrypted_file:
        encrypted_file.write(encrypted)


if __name__ == '__main__':

    parser = argparse.ArgumentParser('Utility to manage Encrypted File Stores')
    parser.add_argument('command', choices=['create_key', 'encrypt'])
    parser.add_argument('filename', nargs='+')

    arguments = parser.parse_args()
    if arguments.command.upper() == 'CREATE_KEY':
        create_key(arguments.filename[0])
    elif arguments.command.upper() == 'ENCRYPT':
        encrypt(arguments.filename[0], arguments.filename[1], arguments.filename[2])
  