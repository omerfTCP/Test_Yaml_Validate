import yaml

def validate_yaml(file_path):
    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        return data, None
    except yaml.YAMLError as exc:
        return None, str(exc)

def check_custom_rules(data, rules):
    errors = []
    for rule in rules:
        path = rule.get("path")
        condition = rule.get("condition")
        message = rule.get("message")
        
        # Traverse the YAML structure based on the path
        keys = path.split('.')
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list) and key.isdigit() and int(key) < len(value):
                value = value[int(key)]
            else:
                value = None
                break
        
        # Apply the condition on the extracted value
        if not condition(value):
            errors.append(message)
    
    return errors

# Custom validation rules
rules = [
    {
        "path": "servers",
        "condition": lambda x: isinstance(x, list) and len(x) == 1,
        "message": "YAML should have exactly one server."
    },
    {
        "path": "paths",
        "condition": lambda paths: all(
            'x-amazon-apigateway-integration' in path_data for path_data in paths.values()
        ),
        "message": "Each endpoint must have a 'x-amazon-apigateway-integration' entry."
    },
    {
        "path": "paths",
        "condition": lambda paths: all(
            'x-api-key' in path_data.get('parameters', [{}])[0].get('name', '').lower() for path_data in paths.values()
        ),
        "message": "Each endpoint should include the 'X-API-KEY' tag in the parameters."
    },
    {
        "path": "components.schemas",
        "condition": lambda schemas: all(
            'description' in schema and 'example' in schema for schema in schemas.values()
        ),
        "message": "Each schema should include a description and an example value."
    },
    {
        "path": "paths",
        "condition": lambda paths: all(
            'description' in method for path_data in paths.values() for method in path_data.values()
        ),
        "message": "Each endpoint should have a description."
    },
    {
        "path": "components.schemas",
        "condition": lambda schemas: all(
            isinstance(schema.get('$ref', ''), str) for schema in schemas.values()
        ),
        "message": "Request and Response JSON schemas must be referenced, not inline."
    }
]

# Path to the YAML file
yaml_file_path = "portal_2.0_oas.yaml"

# Validate YAML
data, error = validate_yaml(yaml_file_path)
if error:
    print(f"YAML validation error: {error}")
    exit(1)
else:
    # Check custom rules
    rule_errors = check_custom_rules(data, rules)
    if rule_errors:
        print("Custom rule violations found:")
        for err in rule_errors:
            print(f" - {err}")
        exit(1)
    else:
        print("YAML content is valid and meets all custom rules.")
