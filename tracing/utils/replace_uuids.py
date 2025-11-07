import uuid
import re
from pathlib import Path

def generate_uuid_mapping(content):
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    old_uuids = set(re.findall(uuid_pattern, content))
    return {old: str(uuid.uuid4()) for old in old_uuids}

def update_json_content(content, uuid_mapping):
    updated_content = content
    
    # Sort UUIDs by length in descending order to avoid partial replacements
    for old_uuid in sorted(uuid_mapping.keys(), key=len, reverse=True):
        new_uuid = uuid_mapping[old_uuid]
        updated_content = updated_content.replace(old_uuid, new_uuid)
    
    return updated_content

def process_json_file(input_path, output_path):
    """Process the JSON file and write updated content to output file."""
    try:
        with open(input_path, 'r') as file:
            content = file.read()
        
        uuid_mapping = generate_uuid_mapping(content)
        
        updated_content = update_json_content(content, uuid_mapping)
        
        with open(output_path, 'w') as file:
            file.write(updated_content)
        
        print(f"Successfully processed file. Output written to: {output_path}")
        print(f"UUID mappings:")
        for old, new in uuid_mapping.items():
            print(f"Old: {old}")
            print(f"New: {new}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")

# Process all files in data directory
data_path = Path("data")
run_ops_files = list(data_path.glob("*.jsonl"))
run_ops_files.sort()

for input_file in run_ops_files:
    output_file = input_file.parent / f"{input_file.name}"
    process_json_file(str(input_file), str(output_file))