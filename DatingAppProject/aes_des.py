from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from os import urandom
import hashlib

AES_BLOCK_SIZE = 128


def pad_message(message: str) -> bytes:

    padder = padding.PKCS7(AES_BLOCK_SIZE).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    return padded_data


def unpad_message(padded_message: bytes) -> str:

    unpadder = padding.PKCS7(AES_BLOCK_SIZE).unpadder()
    data = unpadder.update(padded_message) + unpadder.finalize()
    return data.decode()


def encrypt_message(message: str, shared_key: str) -> str:

    key = hashlib.sha256(shared_key.encode()).hexdigest()[:32]
    key = bytes.fromhex(key)
    iv = urandom(16)

    padded_message = pad_message(message)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

    return (iv + encrypted_message).hex()


def decrypt_message(encrypted_message_hex: str, shared_key: str) -> str:

    encrypted_message = bytes.fromhex(encrypted_message_hex)
    key = hashlib.sha256(shared_key.encode()).hexdigest()[:32]
    key = bytes.fromhex(key)
    iv = encrypted_message[:16]
    encrypted_message = encrypted_message[16:]

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded_message = (
        decryptor.update(encrypted_message) + decryptor.finalize()
    )

    return unpad_message(decrypted_padded_message)
