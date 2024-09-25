import hashlib
import os
from threading import main_thread


def generate_salt_and_key(password):
    """
    Generates a salt and key for a password.

        Parameters:

            password (str): The password to generate a key for.

        Returns:

            salt (bytes): The salt to generate the key.
            key (bytes): The key generated.
    """
    salt = os.urandom(32)

    key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000)
    return salt, key


def verify_password(password, key, salt):
    """
    Checks the given password to an existing key and salt combination.

        Parameters:

            password (str): The password to check.
            key (bytes): The key to check against.
            salt (bytes): The salt to related to the key.

        Returns:

            (bool): Whether the checked password matches the given salt and key.
    """
    checked_key = hashlib.pbkdf2_hmac(
        'sha256', password.encode('utf-8'), salt, 100000)
    if checked_key == key:
        return True
    else:
        return False
