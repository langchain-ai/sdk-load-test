import re
from pathlib import Path
from datetime import date, timedelta


def update_json_dates(content):
    today = date.today()
    
    # Collect all unique dates from the content
    all_dates = set()
    
    # Find all dates in start_time fields
    start_time_pattern = r'("start_time":\s*")(\d{4}-\d{2}-\d{2})T'
    start_time_matches = re.findall(start_time_pattern, content)
    for match in start_time_matches:
        all_dates.add(match[1])
    
    # Find all dates in end_time fields
    end_time_pattern = r'("end_time":\s*")(\d{4}-\d{2}-\d{2})T'
    end_time_matches = re.findall(end_time_pattern, content)
    for match in end_time_matches:
        all_dates.add(match[1])
    
    # Find all dates in start events
    start_event_pattern = r'("name":"start","time":")(\d{4}-\d{2}-\d{2})T'
    start_event_matches = re.findall(start_event_pattern, content)
    for match in start_event_matches:
        all_dates.add(match[1])
    
    # Find all dates in end events
    end_event_pattern = r'("name":"end","time":")(\d{4}-\d{2}-\d{2})T'
    end_event_matches = re.findall(end_event_pattern, content)
    for match in end_event_matches:
        all_dates.add(match[1])
    
    if not all_dates:
        print("No dates found to update.")
        return content
    
    # Create date mapping: latest date -> today, second latest -> yesterday, etc.
    sorted_dates = sorted(all_dates)
    date_mapping = {}
    for i, old_date in enumerate(sorted_dates):
        days_back = len(sorted_dates) - 1 - i
        new_date = today - timedelta(days=days_back)
        date_mapping[old_date] = new_date.isoformat()
    
    print(f"Date mapping:")
    for old_date, new_date in date_mapping.items():
        print(f"  {old_date} -> {new_date}")
    
    updated_content = content
    
    # Apply mapping to start_time fields
    for old_date, new_date in date_mapping.items():
        updated_content = re.sub(
            f'("start_time":\\s*"){old_date}T',
            f'"start_time":"{new_date}T',
            updated_content
        )
    
    # Apply mapping to end_time fields
    for old_date, new_date in date_mapping.items():
        updated_content = re.sub(
            f'("end_time":\\s*"){old_date}T',
            f'"end_time":"{new_date}T',
            updated_content
        )
    
    # Apply mapping to start events
    for old_date, new_date in date_mapping.items():
        updated_content = re.sub(
            f'("name":"start","time":")({old_date})T',
            f'"name":"start","time":"{new_date}T',
            updated_content
        )
    
    # Apply mapping to end events
    for old_date, new_date in date_mapping.items():
        updated_content = re.sub(
            f'("name":"end","time":")({old_date})T',
            f'"name":"end","time":"{new_date}T',
            updated_content
        )
    
    return updated_content


def process_json_file(input_path, output_path):
    """Process the JSON file and write updated content to output file."""
    try:
        with open(input_path, 'r') as file:
            content = file.read()
        
        updated_content = update_json_dates(content)
        
        with open(output_path, 'w') as file:
            file.write(updated_content)
        
        print(f"Successfully processed file. Output written to: {output_path}")
            
    except Exception as e:
        print(f"Error processing file: {str(e)}")


# Process all files in data directory
data_path = Path("data")
if data_path.exists():
    run_ops_files = list(data_path.glob("*.jsonl"))
    run_ops_files.sort()

    for input_file in run_ops_files:
        output_file = input_file.parent / f"{input_file.name}"
        process_json_file(str(input_file), str(output_file))
else:
    print(f"Directory not found: {data_path}. Make sure to run this script from the root directory of the project.")