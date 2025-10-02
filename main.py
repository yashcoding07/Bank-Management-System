import json
import random
import string
from pathlib import Path


class Bank:
    database = 'data.json'
    data = []

    with open(database) as fs:
        data = json.loads(fs.read())

    def createAccount(self):
        pass

user = Bank()
print("Press 1 for creating an account")
print("Press 2 for depositing the money in the account")
print("Press 3 for withdrawing the money from the account")
print("Press 4 for details")
print("Press 5 for updating the details")
print("Press 6 for deleting the account")

check = int(input("tell your response:- "))

if check == 1:
    user.createAccount()
