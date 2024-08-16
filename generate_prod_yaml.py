import yaml
import os
from collections import OrderedDict

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

# Custom SafeDumper to maintain key order
class OrderedDumper(yaml.SafeDumper):
    pass

def dict_representer(dumper, data):
    return dumper.represent_dict(data.items())

OrderedDumper.add_representer(OrderedDict, dict_representer)

def generate_prod_yaml(file_path, replacements):
 +   # Load the YAML file with preserved order
    with open(file_path, 'r') as file:
        yaml_content = yaml.load(file, Loader=NoDatesSafeLoader)

    # Recursively search and replace the text
    def recursive_replace(content):
        if isinstance(content, dict):
            return OrderedDict((key, recursive_replace(value)) for key, value in content.items())
        elif isinstance(content, list):
            return [recursive_replace(item) for item in content]
        elif isinstance(content, str):
            for find_text, replace_text in replacements:
                content = content.replace(find_text, replace_text)
            return content
        else:
            return content
    
    modified_content = recursive_replace(yaml_content)
 
    # Generate new filename by replacing DEV_ with PROD_
    dir_name, base_name = os.path.split(file_path)
    new_file_name = base_name.replace("DEV_", "PROD_")
    output_path = os.path.join(dir_name, new_file_name)

    # Write the modified YAML back to a new file with preserved order
    with open(output_path, 'w') as file:
        yaml.dump(modified_content, file, Dumper=OrderedDumper, default_flow_style=False)
    
    print(f"Modified YAML saved to: {output_path}")

