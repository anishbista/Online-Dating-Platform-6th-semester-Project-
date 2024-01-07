from itertools import cycle


def encrypt_message(message, shared_key):
    encrypted_message = ""
    for c in message:
        encrypted_message += chr(ord(c) + shared_key)
    return encrypted_message


def decrypt_message(encrypted_message, shared_key):
    decryptedMessage = "".join(
        chr(ord(c) ^ ord(k)) for c, k in zip(encrypted_message, cycle(shared_key))
    )
    return decryptedMessage
