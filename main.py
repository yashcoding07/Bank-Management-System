import json
import random
import string
from pathlib import Path


class Bank:
    database = 'data.json'
    data = []

    try:
        if Path(database).exists():
            with open(database) as fs:
                data = json.loads(fs.read())
        else:
            print("no such file exist.")
    except Exception as err:
        print(f"An exception occurred as {err}")

    @classmethod
    def __update(cls):
        with open(cls.database, 'w') as fs:
            fs.write(json.dumps(cls.data))

    @classmethod
    def __accountGenerate(cls):
        char = random.choices(string.ascii_letters, k = 3)
        num = random.choices(string.digits, k = 3)
        spchar = random.choices("!@#$%^&*", k = 1)
        id = char + num + spchar
        random.shuffle(id)
        return "".join(id)

    def createAccount(self):
        info = {
            "name" : input("Enter your name: "),
            "age" : int(input("Enter your age: ")),
            "email": input("Enter your email: "),
            "pin": int(input("Enter your 4 number pin: ")),
            "accountNo.": Bank.__accountGenerate(),
            "balance": 0
        }
        if info['age'] < 18 or len(str(info['pin'])) != 4:
            print("Sorry your account cannot be created.")
        else:
            print("Your account created successfully.")
            for i in info:
                print(f"{i} : {info[i]}")
            print("Please check your details and note your account no.")

            Bank.data.append(info)
            Bank.__update()

    def depositMoney(self):
        accnumber = input("Enter your account number: ")
        pin = int(input("Enter your pin: "))  # Convert to int

        userData = [i for i in Bank.data if i['accountNo.'] == accnumber and i['pin'] == pin ]
        if not userData:  
            print("Sorry data not found.")
        else:
            amount = int(input("Enter the amount you want to deposit: "))
            if amount > 10000 or amount < 0:
                print("Sorry the amount is too much you can  deposit below 10000 and above 0")
            else:
                userData[0]['balance'] += amount
                Bank.__update()
                print("Amount deposited successfully.")

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
if check == 2:
    user.depositMoney()