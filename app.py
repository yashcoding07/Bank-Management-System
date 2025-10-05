import json
import random
import string
from pathlib import Path
import streamlit as st


class Bank:
    database = 'data.json'
    data = []

    @classmethod
    def load(cls):
        if Path(cls.database).exists():
            with open(cls.database, "r") as fs:
                try:
                    cls.data = json.load(fs)
                except json.JSONDecodeError:
                    cls.data = []
        else:
            cls.data = []

    @classmethod
    def save(cls):
        with open(cls.database, "w") as fs:
            json.dump(cls.data, fs, indent=4)

    @classmethod
    def generate_account(cls):
        chars = random.choices(string.ascii_uppercase, k=3)
        nums = random.choices(string.digits, k=3)
        sp = random.choices("!@#$%^&*", k=1)
        acc_id = chars + nums + sp
        random.shuffle(acc_id)
        return "".join(acc_id)

    @classmethod
    def create_account(cls, name, age, email, pin):
        if age < 18 or len(str(pin)) != 4:
            return False, "Account creation failed (age < 18 or pin not 4 digits)."
        
        account = {
            "name": name,
            "age": age,
            "email": email,
            "pin": int(pin),
            "accountNo": cls.generate_account(),
            "balance": 0
        }
        cls.data.append(account)
        cls.save()
        return True, account

    @classmethod
    def authenticate(cls, accnumber, pin):
        for user in cls.data:
            if user["accountNo"] == accnumber and user["pin"] == pin:
                return user
        return None

    @classmethod
    def deposit(cls, accnumber, pin, amount):
        user = cls.authenticate(accnumber, pin)
        if not user:
            return False, "Account not found."
        if amount <= 0 or amount > 10000:
            return False, "Deposit must be between 1 and 10000."
        user["balance"] += amount
        cls.save()
        return True, f"Deposited {amount}. Current balance: {user['balance']}"

    @classmethod
    def withdraw(cls, accnumber, pin, amount):
        user = cls.authenticate(accnumber, pin)
        if not user:
            return False, "Account not found."
        if amount <= 0 or amount > user["balance"]:
            return False, "Insufficient balance or invalid amount."
        user["balance"] -= amount
        cls.save()
        return True, f"Withdrawn {amount}. Current balance: {user['balance']}"

    @classmethod
    def update(cls, accnumber, pin, name=None, email=None, newpin=None):
        user = cls.authenticate(accnumber, pin)
        if not user:
            return False, "Account not found."

        if name:
            user["name"] = name
        if email:
            user["email"] = email
        if newpin and len(str(newpin)) == 4:
            user["pin"] = int(newpin)

        cls.save()
        return True, "Details updated successfully."

    @classmethod
    def delete(cls, accnumber, pin):
        user = cls.authenticate(accnumber, pin)
        if not user:
            return False, "Account not found."
        cls.data.remove(user)
        cls.save()
        return True, "Account deleted successfully."


# Load existing data
Bank.load()

# ---------------- STREAMLIT APP ----------------
st.title("🏦 Simple Bank Management System")

menu = ["Create Account", "Deposit Money", "Withdraw Money", "Show Details", "Update Details", "Delete Account"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Create Account":
    st.subheader("Create a New Account")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, step=1)
    email = st.text_input("Email")
    pin = st.text_input("4-digit PIN", type="password")
    if st.button("Create Account"):
        if pin.isdigit() and len(pin) == 4:
            success, msg = Bank.create_account(name, age, email, pin)
            if success:
                st.success("Account Created Successfully!")
                st.json(msg)
            else:
                st.error(msg)
        else:
            st.error("PIN must be 4 digits.")

elif choice == "Deposit Money":
    st.subheader("Deposit Money")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1, max_value=10000, step=1)
    if st.button("Deposit"):
        success, msg = Bank.deposit(acc, int(pin), amount)
        st.success(msg) if success else st.error(msg)

elif choice == "Withdraw Money":
    st.subheader("Withdraw Money")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    amount = st.number_input("Amount", min_value=1, step=1)
    if st.button("Withdraw"):
        success, msg = Bank.withdraw(acc, int(pin), amount)
        st.success(msg) if success else st.error(msg)

elif choice == "Show Details":
    st.subheader("Show Account Details")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    if st.button("Show"):
        user = Bank.authenticate(acc, int(pin))
        if user:
            st.json(user)
        else:
            st.error("No such account found.")

elif choice == "Update Details":
    st.subheader("Update Account Details")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    new_name = st.text_input("New Name")
    new_email = st.text_input("New Email")
    new_pin = st.text_input("New PIN (4-digit)", type="password")
    if st.button("Update"):
        success, msg = Bank.update(acc, int(pin), new_name, new_email, new_pin)
        st.success(msg) if success else st.error(msg)

elif choice == "Delete Account":
    st.subheader("Delete Account")
    acc = st.text_input("Account Number")
    pin = st.text_input("PIN", type="password")
    if st.button("Delete"):
        success, msg = Bank.delete(acc, int(pin))
        st.success(msg) if success else st.error(msg)
