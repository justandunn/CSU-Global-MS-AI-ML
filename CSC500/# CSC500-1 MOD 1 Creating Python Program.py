# CSC500-1 MOD 1 Creating Python Programs
# Part 1: Addition and Subtraction
num1 = float(input("Enter the first number: "))
num2 = float(input("Enter the second number: "))

# Perform addition and subtraction
addition = num1 + num2
subtraction = num1 - num2

# Output results
print(f"Addition of {num1} and {num2} is {addition}")
print(f"Subtraction of {num1} and {num2} is {subtraction}")

# Part 2: Multiplication and Division
num3 = float(input("Enter the third number: "))
num4 = float(input("Enter the fourth number: "))

# Perform multiplication and division
multiplication = num1 * num2
if num2 != 0:
    division = num1 / num2
else:
    division = "undefined (division by zero is not allowed)"

# Output results
print(f"Multiplication of {num1} and {num2} is {multiplication}")
print(f"Division of {num1} by {num2} is {division}")
