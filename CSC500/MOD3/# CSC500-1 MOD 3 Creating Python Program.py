# CSC500-1 MOD 3 Creating Python Programs
# Part 1: Meal cost calculator
meal_cost = float(input("Enter the charge for the food: "))

# Calculate the tip, sales tax, and total cost
tip = meal_cost * 0.18
sales_tax = meal_cost * 0.07
total_cost = meal_cost + tip + sales_tax

# Output the results
print(f"Tip amount: ${tip:.2f}")
print(f"Sales tax amount: ${sales_tax:.2f}")
print(f"Total cost: ${total_cost:.2f}")

# Part 2: Alarm clock calculator
current_time = int(input("Enter the current time (0-23): "))
wait_hours = int(input("Enter the number of hours to wait for the alarm: "))

# Calculate the alarm time
alarm_time = (current_time + wait_hours) % 24

# Output the results
print(f"The alarm will go off at {alarm_time}:00")