import os
import time
import argparse
import dotenv
import json
import pandas as pd
from pathlib import Path
from langsmith import Client

dotenv.load_dotenv()

client = Client()

def langsmith_init_data(csv_file: str, input_keys: list[str], output_keys: list[str], data_dir: str = "data"):
    path = Path(data_dir) / f"{csv_file}.csv"
    start = time.perf_counter()
    
    # Read the CSV file
    df = pd.read_csv(path)
    total_rows = len(df)
    
    # Check if dataset exists, otherwise create it
    try:
        dataset = client.read_dataset(dataset_name=csv_file)
        raise ValueError(f"Dataset '{csv_file}' already exists in LangSmith. Please delete it first or use a different dataset name.")
    except ValueError:
        # Re-raise ValueError (dataset exists)
        raise
    except Exception:
        # Dataset doesn't exist, create it
        dataset = client.create_dataset(
            dataset_name=csv_file,
            description=f"Dataset created from {csv_file} CSV file with {total_rows} rows"
        )
        print(f"Created dataset: {dataset.name}")
    
    # Calibrate chunk size to avoid sending too much at once
    chunk_size = 1000
    num_chunks = (total_rows + chunk_size - 1) // chunk_size
    
    print(f"Uploading {total_rows} rows in {num_chunks} chunks to dataset {dataset.name}...")
    
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, total_rows)
        
        # Create chunk dataframe
        chunk_df = df.iloc[start_idx:end_idx]
        
        # Prepare lists of inputs and outputs
        inputs_list = [{key: row[key] for key in input_keys if key in row} for _, row in chunk_df.iterrows()]
        outputs_list = [{key: row[key] for key in output_keys if key in row} for _, row in chunk_df.iterrows()] if output_keys else None
        
        # Upload chunk to the dataset
        client.create_examples(
            inputs=inputs_list,
            outputs=outputs_list,
            dataset_id=dataset.id
        )
        print(f"Uploaded chunk {i+1}/{num_chunks}: {len(inputs_list)} examples")
    
    end = time.perf_counter()
    print(f"LangSmith dataset {dataset.name} uploaded in {end - start} seconds")
    print(f"Total examples uploaded: {total_rows}")
    return (end - start, dataset.name, total_rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Upload CSV data to LangSmith dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python upload_data.py 10k-long-emails --data-dir data
        """
    )
    parser.add_argument(
        "dataset_name",
        type=str,
        help="Name of the dataset to upload (must exist in config.json)"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data",
        help="Directory containing the CSV data file (default: data)"
    )
    
    args = parser.parse_args()
    
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    if args.dataset_name not in config["data_files"]:
        raise ValueError(f"Dataset '{args.dataset_name}' not found in config.json")
    if "inputs" not in config["data_files"][args.dataset_name] or "outputs" not in config["data_files"][args.dataset_name]:
        raise ValueError(f"Dataset '{args.dataset_name}' does not have inputs or outputs in config.json")
    
    dataset_config = config["data_files"][args.dataset_name]
    langsmith_results = langsmith_init_data(args.dataset_name, dataset_config["inputs"], dataset_config["outputs"], args.data_dir)
    print(f"LangSmith results: {langsmith_results}")