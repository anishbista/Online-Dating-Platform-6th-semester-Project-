from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from os import urandom
import hashlib

AES_BLOCK_SIZE = 128  # AES block size is 128 bits


def pad_message(message: str) -> bytes:
    # Padding the message to ensure it is a multiple of the block size
    padder = padding.PKCS7(AES_BLOCK_SIZE).padder()
    padded_data = padder.update(message.encode()) + padder.finalize()
    return padded_data


def unpad_message(padded_message: bytes) -> str:
    # Unpadding the decrypted message
    unpadder = padding.PKCS7(AES_BLOCK_SIZE).unpadder()
    data = unpadder.update(padded_message) + unpadder.finalize()
    return data.decode()


def encrypt_message(message: str, shared_key: str) -> str:
    # Convert shared key to a valid hexadecimal string using SHA-256
    key = hashlib.sha256(shared_key.encode()).hexdigest()[:32]
    key = bytes.fromhex(key)  # AES-128 uses 16 bytes (32 hex characters)
    iv = urandom(16)  # AES requires a 16-byte initialization vector (IV)

    # Pad the message before encryption
    padded_message = pad_message(message)

    # Create AES cipher in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Encrypt the message
    encrypted_message = encryptor.update(padded_message) + encryptor.finalize()

    # Return the IV + encrypted message in hex format
    return (iv + encrypted_message).hex()


def decrypt_message(encrypted_message_hex: str, shared_key: str) -> str:
    # Convert the encrypted message and shared key to bytes
    encrypted_message = bytes.fromhex(encrypted_message_hex)
    key = hashlib.sha256(shared_key.encode()).hexdigest()[:32]
    key = bytes.fromhex(key)  # AES-128 uses 16 bytes (32 hex characters)
    iv = encrypted_message[:16]  # First 16 bytes are the IV
    encrypted_message = encrypted_message[
        16:
    ]  # Remaining bytes are the actual ciphertext

    # Create AES cipher in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decrypt the message
    decrypted_padded_message = (
        decryptor.update(encrypted_message) + decryptor.finalize()
    )

    # Unpad the decrypted message and return it
    return unpad_message(decrypted_padded_message)


message = "WE\."
shared_key = "65c0ac8d12081cd97d17b02193417965d8b1a54941ed76f7cd67b9802ab7272c"
encrypted_message = encrypt_message(message, shared_key)
print(f"Encrypted: {encrypted_message}")
decrypted_message = decrypt_message(encrypted_message, shared_key)
print(f"Decrypted: {decrypted_message}")
