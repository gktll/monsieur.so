
#-----------------------------------------
# format yaml with consistent indentation.
#-----------------------------------------

# from ruamel.yaml import YAML

# # Initialize YAML with specific formatting options
# yaml = YAML()
# yaml.indent(mapping=2, sequence=4, offset=2)  # Set mapping and sequence indentation
# yaml.preserve_quotes = True  # Preserve any quotes in your original file

# # Load YAML file
# def load_yaml(file_path):
#     with open(file_path, 'r') as f:
#         return yaml.load(f)

# # Save YAML file with corrected indentation
# def save_yaml(data, file_path):
#     with open(file_path, 'w') as f:
#         yaml.dump(data, f)

# # Example usage
# file_path = "/Users/fede/Desktop/git/monsieur_neo/ontologies/analogiesAll.yaml"
# data = load_yaml(file_path)
# save_yaml(data, file_path)

# print("YAML file has been reformatted with consistent indentation.")





# import yaml
# import re

# # Regular expression to validate URI format (basic validation, can be expanded)
# URI_REGEX = re.compile(r"^monsieur:[A-Za-z]+(/[A-Za-z0-9_()]+)*$")

# # Load YAML file
# def load_yaml(file_path):
#     with open(file_path, 'r') as f:
#         return yaml.safe_load(f)

# # Basic validators
# def validate_uri(uri):
#     # Accept URIs that start with either 'monsieur:' or 'http(s)://'
#     return isinstance(uri, str) and (bool(URI_REGEX.match(uri)) or uri.startswith(("http://", "https://")))

# def validate_string(value):
#     return isinstance(value, str) and len(value) > 0

# def validate_boolean(value):
#     return isinstance(value, bool)

# def validate_float(value):
#     return isinstance(value, float)

# def validate_structure(data, structure):
#     for key, validator in structure.items():
#         if key not in data:
#             print(f"Missing required key: {key}")
#             return False
#         if not validator(data[key]):
#             print(f"Invalid value for key {key}: {data[key]}")
#             return False
#     return True

# # Validate different types of properties
# def validate_properties(properties, expected_fields):
#     for prop_name, prop_data in properties.items():
#         for field, validator in expected_fields.items():
#             # Check if the field exists in the property data
#             if field not in prop_data:
#                 print(f"Missing {field} in property '{prop_name}'")
#                 return False
            
#             # Special case for xsd:float validation
#             if prop_data.get("type") == "xsd:float" and field == "default":
#                 if not isinstance(prop_data[field], (float, int)):  # Allow integers and floats as valid defaults
#                     print(f"Invalid default in property '{prop_name}': {prop_data[field]}")
#                     return False
            
#             # Special case for list of strings (e.g., xsd:string[])
#             elif prop_data.get("type") == "xsd:string[]" and field == "default":
#                 # Check that the default is an empty list or a list of strings
#                 if not (isinstance(prop_data[field], list) and all(isinstance(item, str) for item in prop_data[field])):
#                     print(f"Invalid default in property '{prop_name}': {prop_data[field]}")
#                     return False
            
#             # General case for other types
#             elif not validator(prop_data[field]):
#                 print(f"Invalid {field} in property '{prop_name}': {prop_data[field]}")
#                 return False
#     return True

# # Validation for ontology
# def validate_ontology(ontology):
#     ontology_structure = {
#         "uri": validate_uri,
#         "name": validate_string,
#         "description": validate_string,
#         "version": validate_string
#     }
#     return validate_structure(ontology, ontology_structure)

# # Validation for classes, including properties
# def validate_class(class_data):
#     class_structure = {
#         "type": validate_string,
#         "uri": validate_uri,
#         "label": validate_string,
#         "description": validate_string
#     }
#     if not validate_structure(class_data, class_structure):
#         return False
    
#     # Validate defaultProperties if they exist
#     if "defaultProperties" in class_data:
#         default_property_fields = {
#             "type": validate_string,
#             "default": validate_string,
#             "description": validate_string
#         }
#         if not validate_properties(class_data["defaultProperties"], default_property_fields):
#             print("Invalid defaultProperties in class")
#             return False
    
#     # Validate classProperties if they exist
#     if "classProperties" in class_data:
#         class_property_fields = {
#             "type": validate_string,
#             "default": validate_string,
#             "description": validate_string
#         }
#         if not validate_properties(class_data["classProperties"], class_property_fields):
#             print("Invalid classProperties in class")
#             return False
    
#     # Validate subClassProperties if they exist
#     if "subClassProperties" in class_data:
#         subclass_property_fields = {
#             "type": validate_string,
#             "default": lambda x: validate_boolean(x) or validate_string(x),  # Accepts boolean or string
#             "description": validate_string
#         }
#         if not validate_properties(class_data["subClassProperties"], subclass_property_fields):
#             print("Invalid subClassProperties in class")
#             return False
    
#     return True

# # Validate instances without cross-referencing
# def validate_instance(instance_data):
#     instance_structure = {
#         "uri": validate_uri,
#         "label": validate_string,
#         "description": validate_string
#     }
#     return validate_structure(instance_data, instance_structure)

# # Validate analogy and relationship properties without cross-referencing
# def validate_analogy_properties(properties):
#     for i, prop in enumerate(properties):
#         try:
#             if "targetEntity" not in prop or not validate_uri(prop["targetEntity"].get("uri", "")):
#                 print(f"Invalid or missing targetEntity in analogy {i}: {prop}")
#                 return False
#             if "analogySystem" not in prop or not validate_uri(prop["analogySystem"].get("uri", "")):
#                 print(f"Invalid or missing analogySystem in analogy {i}: {prop}")
#                 return False
#             if "confidence" in prop:
#                 confidence = prop["confidence"]
#                 if confidence is None or not isinstance(confidence, dict):
#                     print(f"Invalid confidence structure in analogy {i}: {prop}")
#                     return False
#                 if "score" not in confidence or not validate_float(confidence["score"]):
#                     print(f"Invalid confidence score in analogy {i}: {prop}")
#                     return False
#         except Exception as e:
#             print(f"Error validating analogy {i}: {e}")
#             return False
#     return True

# # Run validation on individual YAML data structure components
# def validate_yaml_data(data):
#     if "ontology" in data and not validate_ontology(data["ontology"]):
#         print("Ontology section is missing or invalid.")
#         return False
    
#     if "classes" in data:
#         for class_name, class_data in data["classes"].items():
#             if not validate_class(class_data):
#                 print(f"Invalid class: {class_name}")
#                 return False
    
#     if "instances" in data:
#         for instance_name, instance_data in data["instances"].items():
#             if not validate_instance(instance_data):
#                 print(f"Invalid instance: {instance_name}")
#                 return False
#             if "analogyProperties" in instance_data:
#                 if not validate_analogy_properties(instance_data["analogyProperties"].get("hasAnalogyWith", [])):
#                     print(f"Invalid analogyProperties in instance: {instance_name}")
#                     return False
#     print("Validation complete. No issues found for structural format.")


# # Example usage:
# file_path = "/Users/fede/Desktop/git/monsieur_neo/ontologies/colorEntity.yaml"
# yaml_data = load_yaml(file_path)
# validate_yaml_data(yaml_data)





from ruamel.yaml import YAML
import re

def modify_uri(uri):
    match = re.search(r'(monsieur:MagicHourEntity/)(.+)', uri)
    if match:
        modified_suffix = re.sub(r'(?<!^)(?=[A-Z])', '_', match.group(2))
        return f"{match.group(1)}{modified_suffix}"
    return uri

def transform_hour_label(label):
    match = re.match(r'(\d+)\w* Hour of the (\w+) - (\w+)', label)
    if match:
        number, day, week = match.groups()
        return f"{number}th_Of_{day}_{week}"
    return label

def transform_nested_dict(data):
    for key, value in data.items() if isinstance(data, dict) else enumerate(data):
        if isinstance(value, (dict, list)):
            transform_nested_dict(value)
        elif key == 'uri' and isinstance(value, str):
            data[key] = modify_uri(value)
        elif key == 'label' and isinstance(value, str):
            data[key] = transform_hour_label(value)

def edit_yaml(input_file, output_file):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)
    
    with open(input_file, "r") as file:
        data = yaml.load(file)
    
    transform_nested_dict(data)
    
    with open(output_file, "w") as file:
        yaml.dump(data, file)


# Example usage
input_file = "/Users/fede/Desktop/git/monsieur_neo/ontologies/spiritualEntity.yaml"
output_file = "/Users/fede/Desktop/git/monsieur_neo/ontologies/spiritualEntity_edit_hours.yaml"
edit_yaml(input_file, output_file)
