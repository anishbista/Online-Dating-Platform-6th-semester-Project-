from binascii import hexlify
from hashlib import sha256
from os import urandom


primes = {
    # 2048-bit
    14: {
        "prime": int(
            "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
            + "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
            + "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
            + "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
            + "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D"
            + "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F"
            + "83655D23DCA3AD961C62F356208552BB9ED529077096966D"
            + "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B"
            + "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9"
            + "DE2BCBF6955817183995497CEA956AE515D2261898FA0510"
            + "15728E5A8AACAA68FFFFFFFFFFFFFFFF",
            base=16,
        ),
        "generator": 2,
    },
}


class DiffieHellman:
    # Current minimum recommendation is 2048 bit (group 14)
    def __init__(self, group: int = 14) -> None:
        if group not in primes:
            raise ValueError("Unsupported Group")
        self.prime = primes[group]["prime"]
        self.generator = primes[group]["generator"]

        self.__private_key = int(hexlify(urandom(32)), base=16)

    def get_private_key(self) -> str:
        return hex(self.__private_key)[2:]

    def generate_public_key(self) -> str:
        public_key = pow(self.generator, self.__private_key, self.prime)
        return hex(public_key)[2:]

    @staticmethod
    def is_valid_public_key_static(
        local_private_key_str: str, remote_public_key_str: str, prime: int
    ) -> bool:
        # check if the other public key is valid based on NIST SP800-56
        if 2 <= remote_public_key_str and remote_public_key_str <= prime - 2:
            if pow(remote_public_key_str, (prime - 1) // 2, prime) == 1:
                return True
        return False

    @staticmethod
    def generate_shared_key_static(
        local_private_key_str: str, remote_public_key_str: str, group: int = 14
    ) -> str:
        local_private_key = int(local_private_key_str, base=16)
        remote_public_key = int(remote_public_key_str, base=16)
        prime = primes[group]["prime"]
        if not DiffieHellman.is_valid_public_key_static(
            local_private_key, remote_public_key, prime
        ):
            raise ValueError("Invalid public key")
        shared_key = pow(remote_public_key, local_private_key, prime)
        return sha256(str(shared_key).encode()).hexdigest()
