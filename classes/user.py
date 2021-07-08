import sqlite3
from configQuotes import Config
from passlib.hash import sha256_crypt

config = Config()

class User:

    def __init__(self):
        # put properties here

        # path is relative to root of app (app.py)
        self.dbPath = config.dbName

    def insertUser(self, username, password, email):

        with sqlite3.connect(self.dbPath) as con:
            
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", [username])
            result = cur.fetchone()

            if result:
                return False

            else:
                passwordHashed = sha256_crypt.encrypt(str(password))

                cur = con.cursor()
                cur.execute("INSERT INTO users (username,password,email) VALUES (?,?,?)",
                            (username, passwordHashed, email))
                con.commit()
                cur.close()
                return True
        
    def authenticateUser(self,username,passwordAttempt):

        with sqlite3.connect(self.dbPath) as con:
            
            # Makes the result a dictionary
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username = ?", [username])
            result = cur.fetchone()
            cur.close()

            if result:
                # get the stored hashed password
                passwordHash = result['password']

                if sha256_crypt.verify(passwordAttempt, passwordHash):
                    return result['id']
                else:
                    return False
            else:
                return False

    def getNameFromId(self, id):
        
        with sqlite3.connect(self.dbPath) as con:

            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute("SELECT username FROM users WHERE id = ?", [id])
            result = cur.fetchone()[0]
            cur.close()

            if result:
               return result
            else:
                return False

