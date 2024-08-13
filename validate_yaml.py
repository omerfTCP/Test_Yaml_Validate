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
            else:
                value = None
                break
        
        # Apply the condition on the extracted value
        if not condition(value):
            errors.append(message)
    
    return errors

# Example custom rules
rules = [
    {
        "path": "config.timeout",
        "condition": lambda x: isinstance(x, int) and x > 0,
        "message": "config.timeout should be a positive integer."
    },
    {
        "path": "services.database.host",
        "condition": lambda x: isinstance(x, str) and len(x) > 0,
        "message": "services.database.host should be a non-empty string."
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
