# CSC-1 MOD 7 Creating Python Programs

# Course information dictionaries
room_numbers = {
    "CSC101": "3004",
    "CSC102": "4501",
    "CSC103": "6755",
    "NET110": "1244",
    "COM241": "1411"
}

instructors = {
    "CSC101": "Haynes",
    "CSC102": "Alvarado",
    "CSC103": "Rich",
    "NET110": "Burke",
    "COM241": "Lee"
}

meeting_times = {
    "CSC101": "8:00 a.m.",
    "CSC102": "9:00 a.m.",
    "CSC103": "10:00 a.m.",
    "NET110": "11:00 a.m.",
    "COM241": "1:00 p.m."
}

def get_course_info(course_number):
    """Retrieve and display course details based on course number."""
    if course_number in room_numbers:
        print(f"Course: {course_number}")
        print(f"Room Number: {room_numbers[course_number]}")
        print(f"Instructor: {instructors[course_number]}")
        print(f"Meeting Time: {meeting_times[course_number]}")
    else:
        print("Error: Course number not found.")

def main():
    """Main function to handle user input and course lookups."""
    while True:
        course_number = input("Enter a course number (or type 'exit' to quit): ").strip().upper()
        if course_number == "EXIT":
            print("Exiting program. Goodbye!")
            break
        get_course_info(course_number)
        print("\n")

if __name__ == "__main__":
    main()