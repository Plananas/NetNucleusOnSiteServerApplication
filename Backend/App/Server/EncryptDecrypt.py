from Crypto.Cipher import AES
import random

class CeasarCipher:

    def __init__(self):
        # self.ENCRYPTION_KEY = key
        self.alphabet = "abcdefghijklmnopqrstuvwxyz"
        self.alphabetCaps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # probably the least efficient ceasar cipher, lots of code to hopefully remove all the errors it could get.
    def encrypt(self, msg, key):
        newStr = ""
        key = int(key)
        # key = self.key
        for letter in msg:
            # Checks to see if the letter is capital, lowercase, or any other character.
            # error checks to make sure if we chose a letter past Z it goes back to the start.
            if letter in self.alphabet:
                alphanum = self.alphabet.index(letter)
                if (alphanum + key) > (len(self.alphabet) - 1):
                    newStr += self.alphabet[(alphanum + key) - 26]
                else:
                    newStr += self.alphabet[alphanum + key]

            elif letter in self.alphabetCaps:
                alphanum = self.alphabetCaps.index(letter)
                if (alphanum + int(key)) > (len(self.alphabetCaps) - 1):
                    newStr += self.alphabetCaps[(alphanum + key) - 26]
                else:
                    newStr += self.alphabetCaps[alphanum + key]

            else:
                newStr += letter
        return newStr

    def decrypt(self, msg, key):
        newStr = ""
        key = int(key)
        for letter in msg:
            # Checks to see if the letter is capital, lowercase, or any other character.
            # error checks to make sure if we chose a letter past Z it goes back to the start.
            if letter in self.alphabet:
                alphanum = self.alphabet.index(letter)
                if (alphanum - int(key)) < 0:
                    newStr += self.alphabet[(alphanum - key) + 26]
                else:
                    newStr += self.alphabet[alphanum - key]
            elif letter in self.alphabetCaps:
                alphanum = self.alphabetCaps.index(letter)
                if (alphanum - int(key)) < 0:
                    newStr += self.alphabetCaps[(alphanum - key) + 26]
                else:
                    newStr += self.alphabetCaps[alphanum - key]
            else:
                newStr += letter
        return newStr
        pass

# *♬♪ listening to star wars ambience while we coding ♬♪*
# This will take a string and do a ceasar cipher on it based on the key
class VigenereCipher:

    def __init__(self):
        self.alphabet = "abcdefghijklmnopqrstuvwxyz1234567890"
        self.Ceasar = CeasarCipher()

    def createKey(self, key, original):
        key = self.stringToNumbers(key)
        newKey = ""
        while len(newKey) < len(original):
            for y in range(0, len(key)):
                newKey += str(key[y])
        return newKey

    def stringToNumbers(self, theString):
        newKey = []
        theString = theString.lower()
        for letter in theString:
            if letter in self.alphabet:
                newKey.append(self.alphabet.index(letter))
            else:
                newKey.append(1)
        return(newKey)

    def encrypt(self, original, key):
        newStr = ""

        key = self.createKey(str(key), original)
        for x in range(0, len(original)):
            if original[x] != " ":
                newStr += self.Ceasar.encrypt(original[x], key[x])
            else:
                newStr += " "
        return newStr

    def decrypt(self, original, key):
        newStr = ""
        key = self.createKey(key, original)

        for x in range(0, len(original)):
            if original[x] != " ":
                newStr += self.Ceasar.decrypt(original[x], key[x])
            else:
                newStr += " "
        return newStr


# This is how we will get a key between us and the client without leaking the whole key.
class DiffieHellman:
    def __init__(self):
        # these are the public values of the key
        self.g = 5012
        self.p = 5411112
        # private key is set when the program starts

        self.privateKey = random.randint(100000, 999999)

    # we create the key to send by using this equation on our private key using the public key
    # B = g**b % p
    def publicPrivateKey(self):
        B = (self.g) ** self.privateKey % self.p
        return B

    def key(self, B):
        key = (B ** self.privateKey) % self.p
        key = str(key)
        # we need to make the key 16 bytes long to be used in AES.
        # I am going to repeat the string until it reaches 16 characters.
        newkey = ""
        keyreversed = reversed(key)
        while len(newkey) < 16:
            for x in key:
                if len(newkey) < 16:
                    newkey += x
                else:
                    break
            for x in keyreversed:
                if len(newkey) < 16:
                    newkey += x
                else:
                    break
        return newkey

# main encryption for network traffic
# we get 3 values to send along to the client or server. the key is also needed to decrypt or it won't work.
# the tag is unique to the message so noone can tamper with it.
class AESCipher():
    def __init__(self, _key):
        self.key = _key.encode('utf-8')

    def encrypt(self, msg):
        msg = msg.encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(msg)
        print(nonce, ciphertext, tag)
        return nonce, ciphertext, tag

    def decrypt(self, nonce, ciphertext, tag):

        cipher = AES.new(self.key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)

        #if someone is trying to do a replay attack the tag and key should help stop them from doing so.
        try:
            cipher.verify(tag)
            return plaintext
        except ValueError:
            print("Mac Check Failed :(")
