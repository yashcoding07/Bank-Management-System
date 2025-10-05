import json
import random
import string
from pathlib import Path
import streamlit as st
import hashlib # For secure PIN hashing

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

    # Helper method to hash PINs for security
    @staticmethod
    def _hash_pin(pin):
        """Hashes a PIN using SHA-256 for secure storage."""
        return hashlib.sha256(str(pin).encode()).hexdigest()

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
        # Centralized validation for new accounts
        if age < 18:
            return False, "Account creation failed. You must be at least 18 years old."
        if not str(pin).isdigit() or len(str(pin)) != 4:
            return False, "Account creation failed. PIN must be exactly 4 digits."
        
        account = {
            "name": name,
            "age": age,
            "email": email,
            "pin_hash": cls._hash_pin(pin),
            "accountNo": cls.generate_account(),
            "balance": 0
        }
        cls.data.append(account)
        cls.save()
        # Return a safe version of the account details for display
        display_account = account.copy()
        del display_account['pin_hash']
        return True, display_account

    @classmethod
    def authenticate(cls, accnumber, pin):
        # Compare the hash of the input pin with the stored hash.
        pin_hash = cls._hash_pin(pin)
        for user in cls.data:
            if user["accountNo"] == accnumber and user["pin_hash"] == pin_hash:
                return user
        return None

    @classmethod
    def deposit(cls, accnumber, pin, amount):
        user = cls.authenticate(accnumber, pin)
        if not user:
            return False, "Authentication failed. Incorrect Account Number or PIN."
        if amount <= 0 or amount > 10000:
            return False, "Deposit must be between 1 and 10000."
        user["balance"] += amount
        cls.save()
        return True, f"Successfully deposited ${amount:,.2f}."

    @classmethod
    def withdraw(cls, accnumber, pin, amount):
        user = cls.authenticate(accnumber, pin)
        if not user:
            return False, "Authentication failed. Incorrect Account Number or PIN."
        if amount <= 0 or amount > user["balance"]:
            return False, "Insufficient balance or invalid amount."
        user["balance"] -= amount
        cls.save()
        return True, f"Successfully withdrawn {amount:,.2f}. Your remaining balance is {user['balance']:,.2f}."

    @classmethod
    def update(cls, accnumber, pin, name=None, email=None, newpin=None):
        user = cls.authenticate(accnumber, pin)
        if not user:
            return False, "Authentication failed. Incorrect Account Number or PIN."

        updated = False
        if name:
            user["name"] = name
            updated = True
        if email:
            user["email"] = email
            updated = True
        if newpin:
            if not str(newpin).isdigit() or len(str(newpin)) != 4:
                return False, "Update failed. New PIN must be 4 digits."
            user["pin_hash"] = cls._hash_pin(newpin)
            updated = True
        
        if updated:
            cls.save()
            return True, "Details updated successfully."
        else:
            return False, "No new details provided to update."

    @classmethod
    def delete(cls, accnumber, pin):
        user = cls.authenticate(accnumber, pin)
        if not user:
            return False, "Authentication failed. Incorrect Account Number or PIN."
        cls.data.remove(user)
        cls.save()
        return True, "Account deleted successfully."


# Load existing data at the start of the script
Bank.load()

# ---------------- STREAMLIT APP ----------------
st.set_page_config(layout="wide", page_title="Simple Bank", page_icon="🏦")
st.title("🏦 Simple Bank Management System")

menu = ["Create Account", "Deposit Money", "Withdraw Money", "Show Details", "Update Details", "Delete Account"]
choice = st.sidebar.selectbox("Menu", menu)

# Utility function for safe PIN input to prevent app crashes.
def get_pin():
    pin_input = st.text_input("PIN", type="password", key=f"pin_{choice}")
    if not pin_input:
        return None
    try:
        # This safely checks if the pin is a valid integer.
        pin = int(pin_input)
        return pin
    except ValueError:
        st.error("PIN must be a number.")
        return None

if choice == "Create Account":
    st.subheader("Create a New Account")
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=18, step=1)
    email = st.text_input("Email")
    pin = st.text_input("4-digit PIN", type="password")
    if st.button("Create Account"):
        success, msg = Bank.create_account(name, age, email, pin)
        if success:
            st.success("Account Created Successfully!")
        else:
            st.error(msg)

elif choice == "Deposit Money":
    st.subheader("Deposit Money")
    acc = st.text_input("Account Number")
    pin = get_pin() # Using the safe PIN input function
    amount = st.number_input("Amount", min_value=1.0, max_value=10000.0, step=0.01)
    if st.button("Deposit"):
        if acc and pin is not None:
            success, msg = Bank.deposit(acc, pin, amount)
            st.success(msg) if success else st.error(msg)
        else:
            st.warning("Please fill in all fields.")

elif choice == "Withdraw Money":
    st.subheader("Withdraw Money")
    acc = st.text_input("Account Number")
    pin = get_pin()
    amount = st.number_input("Amount", min_value=1.0, step=0.01)
    if st.button("Withdraw"):
        if acc and pin is not None:
            success, msg = Bank.withdraw(acc, pin, amount)
            st.success(msg) if success else st.error(msg)
        else:
            st.warning("Please fill in all fields.")

elif choice == "Show Details":
    st.subheader("Show Account Details")
    acc = st.text_input("Account Number")
    pin = get_pin()
    if st.button("Show"):
        if acc and pin is not None:
            user = Bank.authenticate(acc, pin)
            if user:
                # Create a safe copy of details to show, excluding the PIN hash.
                details_to_show = {
                    "Name": user["name"],
                    "Age": user["age"],
                    "Email": user["email"],
                    "Account Number": user["accountNo"],
                    "Balance": f"${user['balance']:,.2f}"
                }
            else:
                st.error("Authentication failed. Incorrect Account Number or PIN.")
        else:
            st.warning("Please fill in all fields.")

elif choice == "Update Details":
    st.subheader("Update Account Details")
    st.info("First, authenticate with your current credentials. Then, fill in only the fields you wish to change.")
    acc = st.text_input("Account Number")
    pin = get_pin()
    
    st.write("---")
    new_name = st.text_input("New Name (optional)")
    new_email = st.text_input("New Email (optional)")
    new_pin = st.text_input("New 4-digit PIN (optional)", type="password")
    
    if st.button("Update"):
        if acc and pin is not None:
            success, msg = Bank.update(acc, pin, new_name or None, new_email or None, new_pin or None)
            st.success(msg) if success else st.error(msg)
        else:
            st.warning("Please provide Account Number and current PIN to update.")

elif choice == "Delete Account":
    st.subheader("Delete Account")
    st.warning("WARNING: This action is irreversible.")
    acc = st.text_input("Account Number")
    pin = get_pin()
    if st.button("Delete Account Permanently"):
        if acc and pin is not None:
            success, msg = Bank.delete(acc, pin)
            st.success(msg) if success else st.error(msg)
        else:
            st.warning("Please fill in all fields.")


