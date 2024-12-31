import re

# def modify_uri(original_uri):
#     # Match everything after monsieur:MagicHourEntity/
#     match = re.search(r'(monsieur:MagicHourEntity/)(.+)', original_uri)
#     if match:
#         # Add underscore before capital letters, except the first character
#         modified_suffix = re.sub(r'(?<!^)(?=[A-Z])', '_', match.group(2))
#         return f"{match.group(1)}{modified_suffix}"
#     return original_uri

# # Test the function
# test_uri = "monsieur:MagicHourEntity/3rdOfNightSunday"
# result = modify_uri(test_uri)
# print(result)

# def modify_string(original_string):
#     # Add underscore before capital letters, except the first character
#     modified_string = re.sub(r'(?<!^)(?=[A-Z])', '_', original_string)
#     return modified_string

# # Test the function
# test_string = "3rdOfNightSunday"
# result = modify_string(test_string)
# print(result)


import re

def transform_hour_label(label):
    # Match labels starting with a number
    match = re.match(r'(\d+)\w* Hour of the (\w+) - (\w+)', label)
    if match:
        number, day, week = match.groups()
        return f"{number}th_Of_{day}_{week}"
    return label

# Test the function
labels = [
    "8th Hour of the Day - Tuesday",
    "9th Hour of the Day - Tuesday"
]

for label in labels:
    transformed = transform_hour_label(label)
    print(f"Original: {label}")
    print(f"Transformed: {transformed}")