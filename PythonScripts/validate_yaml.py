import yaml
import sys

# Custom SafeLoader to avoid automatic date parsing
class NoDatesSafeLoader(yaml.SafeLoader):
    def construct_yaml_timestamp(self, node):
        # Override to avoid parsing dates
        return str(node.value)

# Attach the overridden method to avoid timestamp parsing
NoDatesSafeLoader.add_constructor(
    'tag:yaml.org,2002:timestamp',
    NoDatesSafeLoader.construct_yaml_timestamp
)

def validate_yaml(yaml_file):
    with open(yaml_file, 'r') as file:
        try:
            yaml_content = yaml.load(file, Loader=NoDatesSafeLoader)
        except yaml.YAMLError as exc:
            print(f"Error in YAML file: {exc}")
            return False

    # Check for the basic structure requirements
    if 'servers' not in yaml_content:
        print("YAML is missing 'servers' key.")
        return False
    if len(yaml_content['servers']) != 1:
        print("YAML must have exactly one server.")
        return False

    if 'paths' not in yaml_content:
        print("YAML is missing 'paths' key.")
        return False

    for path, methods in yaml_content['paths'].items():
        for method, details in methods.items():
            # Check for x-amazon-apigateway-integration
            if 'x-amazon-apigateway-integration' not in details:
                print(f"Path {path} method {method} is missing 'x-amazon-apigateway-integration'.")
                return False

            # Check for parameters in each method
            if 'parameters' in details:
                api_key_present = any(
                    param['name'].lower() == 'x-api-key' and param['in'] == 'header'
                    for param in details['parameters']
                )
                if not api_key_present:
                    print(f"Path {path} method {method} is missing 'X-API-KEY' header parameter.")
                    return False
            else:
                print(f"Path {path} method {method} has no parameters defined.")
                return False

            # Check for $ref in request and response schemas
            if 'requestBody' in details and 'content' in details['requestBody']:
                for content_type, content_details in details['requestBody']['content'].items():
                    if 'schema' in content_details and '$ref' not in content_details['schema']:
                        print(f"Path {path} method {method} requestBody schema is not referenced using $ref.")
                        return False

            if 'responses' in details:
                for status_code, response_details in details['responses'].items():
                    if 'content' in response_details:
                        for content_type, content_details in response_details['content'].items():
                            if 'schema' in content_details and '$ref' not in content_details['schema']:
                                print(f"Path {path} method {method} response schema for status {status_code} is not referenced using $ref.")
                                return False

    print("YAML structure is valid.")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_yaml.py <yaml_file>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    is_valid = validate_yaml(yaml_file)
    if not is_valid:
        sys.exit(1)
