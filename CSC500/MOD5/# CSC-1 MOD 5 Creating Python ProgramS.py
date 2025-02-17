# CSC-1 MOD 5 Creating Python ProgramS

# Part 1: Rainfall Calculation
num_years = int(input("Enter the number of years: "))

total_rainfall = 0
months = 0

for year in range(1, num_years + 1):
    for month in range(1, 13):
        rainfall = float(input(f"Enter the inches of rainfall for Year {year}, Month {month}: "))
        total_rainfall += rainfall
        months += 1

average_rainfall = total_rainfall / months

print("\nRainfall Data Summary:")
print(f"Total months: {months}")
print(f"Total inches of rainfall: {total_rainfall:.2f}")
print(f"Average rainfall per month: {average_rainfall:.2f}")

# Part 2: Bookstore Points System
num_books = int(input("Enter the number of books purchased this month: "))

if num_books == 0:
    points = 0
elif num_books == 2:
    points = 5
elif num_books == 4:
    points = 15
elif num_books == 6:
    points = 30
elif num_books >= 8:
    points = 60
else:
    points = 0

print(f"You have earned {points} points this month.")