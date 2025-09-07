# atm_simulation.py
# Module 8 Portfolio Project - ATM State Machine Simulation

class ATM:
    def __init__(self, balance=100, pin="1234", pin_limit=3):
        self.balance = balance
        self.pin = pin
        self.pin_limit = pin_limit
        self.attempts = 0
        self.authenticated = False

    def authenticate(self, entered_pin):
        if entered_pin == self.pin:
            self.authenticated = True
            self.attempts = 0
            print("PIN correct. Access granted.")
        else:
            self.attempts += 1
            print(f"Incorrect PIN. Attempts: {self.attempts}/{self.pin_limit}")
            if self.attempts >= self.pin_limit:
                print("Too many incorrect attempts. Card rejected.")
                self.eject()
                return False
        return self.authenticated

    def withdraw(self, amount):
        if not self.authenticated:
            print("Access denied. Authenticate first.")
            return
        if self.balance == 0:
            print("Account balance is zero. Account closed.")
            return
        if amount <= self.balance:
            self.balance -= amount
            print(f"Dispensed ${amount}. Remaining balance: ${self.balance}")
        else:
            print("Insufficient funds.")

    def eject(self):
        print("Card ejected. Thank you.")
        self.authenticated = False

def demo():
    atm = ATM(balance=50)

    print("\n--- ATM Simulation Demo ---")
    # Wrong PINs
    atm.authenticate("0000")
    atm.authenticate("1111")
    atm.authenticate("2222")  # should reject card

    # New ATM session
    atm = ATM(balance=50)
    atm.authenticate("1234")  # correct PIN
    atm.withdraw(20)
    atm.withdraw(40)          # insufficient funds
    atm.withdraw(30)          # check remaining logic
    atm.eject()

if __name__ == "__main__":
    demo()
