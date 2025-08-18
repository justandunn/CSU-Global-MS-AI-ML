# phtrs_use_case.py

actors = [
    "Citizen",
    "Repair Crew",
    "Public Works Admin",
    "Claims Department"
]

use_cases = [
    "Report Pothole",
    "Check Pothole Status",
    "Report Damage",
    "Assign Work Order",
    "Update Repair Status",
    "Log Hours/Materials",
    "Generate Repair Report",
    "Process Damage Claim"
]

def print_summary():
    print("=== Pothole Tracking and Repair System (PHTRS) ===\n")
    print("Actors in the system:")
    for i, actor in enumerate(actors, start=1):
        print(f"{i}. {actor}")
    
    print("\nUse Cases:")
    for i, uc in enumerate(use_cases, start=1):
        print(f"{i}. {uc}")
    
    print("\nDiagram Description:")
    print("The PHTRS use case diagram illustrates how citizens, repair crews, "
          "administrators, and claims staff interact with the system. "
          "Citizens report potholes and damages, while repair crews update statuses "
          "and log resources. Administrators oversee work orders and costs, and "
          "the claims department processes damages. Together, these use cases "
          "ensure efficient reporting, tracking, and resolution of pothole issues.")

if __name__ == "__main__":
    print_summary()
