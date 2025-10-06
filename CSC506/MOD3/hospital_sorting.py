# hospital_sorting.py
# Author: Justan Dunn
# Date: October 6, 2025
# Purpose: Compare Bubble Sort and Merge Sort for patient record organization

# Sample dataset: simulated hospital patient IDs (unsorted)
patients = [
    {"patient_id": 1042, "name": "Anderson, Maria"},
    {"patient_id": 1008, "name": "Li, Wei"},
    {"patient_id": 1075, "name": "Patel, Ravi"},
    {"patient_id": 1021, "name": "Johnson, Claire"},
    {"patient_id": 1050, "name": "Nguyen, Tuan"},
]


# --------- Bubble Sort Implementation ---------
def bubble_sort(records, key):
    n = len(records)
    for i in range(n):
        for j in range(0, n - i - 1):
            if records[j][key] > records[j + 1][key]:
                records[j], records[j + 1] = records[j + 1], records[j]
    return records


# --------- Merge Sort Implementation ---------
def merge_sort(records, key):
    if len(records) <= 1:
        return records
    mid = len(records) // 2
    left_half = merge_sort(records[:mid], key)
    right_half = merge_sort(records[mid:], key)
    return merge(left_half, right_half, key)


def merge(left, right, key):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i][key] <= right[j][key]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# --------- Program Execution ---------
if __name__ == "__main__":
    print("Original Patient List:")
    for record in patients:
        print(record)
    print("\nBubble Sort by patient_id:")
    bubble_sorted = bubble_sort(patients.copy(), "patient_id")
    for record in bubble_sorted:
        print(record)
    print("\nMerge Sort by name:")
    merge_sorted = merge_sort(patients.copy(), "name")
    for record in merge_sorted:
        print(record)
