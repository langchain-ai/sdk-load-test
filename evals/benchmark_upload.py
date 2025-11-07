import os
import argparse
import json
import humanize
from pathlib import Path
from typing import Tuple
from upload_data import langsmith_init_data

def get_directory_size(data_dir: str, csv_file: str) -> int:
    """Calculate total size of CSV file in a directory."""
    csv_path = Path(data_dir) / f"{csv_file}.csv"
    if csv_path.exists():
        return csv_path.stat().st_size
    return 0


def format_results(ls_results: Tuple[float, str, int],
                   data_dir: str,
                   csv_file: str) -> str:
    """Format benchmark results."""
    ls_time, _, ls_examples = ls_results
    
    # Use the number of examples from the results
    num_examples = ls_examples
    
    total_size = get_directory_size(data_dir, csv_file)
    size_human = humanize.naturalsize(total_size)
    
    avg_ls = ls_time / num_examples if num_examples else 0
    
    return f"""\
Langsmith Benchmark Results
===========================
Time Breakdown:
    Total time      {ls_time:7.3f}s

Performance:
    Total Examples    {num_examples}
    Total Size      {size_human}
    Avg time/example  {avg_ls:7.3f}s
"""

def run_benchmark(data_dir: str, csv_file: str):
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Get dataset configuration
    if csv_file not in config["data_files"]:
        raise ValueError(f"Dataset '{csv_file}' not found in config.json")
    if "inputs" not in config["data_files"][csv_file] or "outputs" not in config["data_files"][csv_file]:
        raise ValueError(f"Dataset '{csv_file}' does not have inputs or outputs in config.json")
    
    dataset_config = config["data_files"][csv_file]
    print(f"Dataset config: {dataset_config}")
    print("Running Langsmith benchmark...")
    langsmith_results = langsmith_init_data(csv_file, dataset_config["inputs"], dataset_config["outputs"], data_dir)
    table = format_results(langsmith_results, data_dir, csv_file)
    
    # Print to console
    print("\nBenchmark Results:\n")
    print(table)
    
    # Save results to a file
    with open("benchmark_results_upload_data.txt", "w") as f:
        f.write(table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark dataset upload performance to LangSmith",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python benchmark_upload.py data 10k-long-emails
        """
    )
    parser.add_argument(
        "data_dir",
        type=str,
        help="Directory containing the CSV data file"
    )
    parser.add_argument(
        "csv_file",
        type=str,
        help="Name of the CSV file (without .csv extension, must exist in config.json)"
    )
    
    args = parser.parse_args()
    run_benchmark(args.data_dir, args.csv_file)