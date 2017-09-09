from Crypto.Cipher import AES
import base64


class Encryptor():
    BLOCK_SIZE = 32
    PADDING = '{'

    def __init__(self):
        pass

    def encrptcode(self, toencode, secret):
        pad = lambda s: s + (self.BLOCK_SIZE - len(s) % self.BLOCK_SIZE) * self.PADDING

        EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))

        cipher = AES.new(secret)

        encoded = EncodeAES(cipher, toencode)

        return encoded

    def decrptcode(self, encoded, secret):

        DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(self.PADDING)

        cipher = AES.new(secret)

        decoded = DecodeAES(cipher, encoded)

        return decoded
