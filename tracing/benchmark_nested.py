import argparse
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Tuple

import orjson
import dotenv
import humanize

from langsmith import Client

dotenv.load_dotenv()

def get_directory_size(directory: str) -> int:
    """Calculate total size of all JSONL files in directory."""
    total_size = 0
    for path in Path(directory).glob("*.jsonl"):
        total_size += path.stat().st_size
    return total_size

class LangsmithReplay:
    @staticmethod
    def replay_trace(run_ops_file: Path, logger: Client) -> None:
        with open(run_ops_file, 'rb') as f:
            for line in f:
                operation = orjson.loads(line)
                
                if operation["operation"] == "post":
                    create_params = {
                        "name": operation.get("name"),
                        "start_time": operation.get("start_time"),
                        "inputs": operation.get("inputs", {}),
                        "run_type": operation.get("run_type"),
                        "serialized": operation.get("serialized", {}),
                        "extra": operation.get("extra", {}),
                        "tags": operation.get("tags", []),
                        "trace_id": operation.get("trace_id"),
                        "dotted_order": operation.get("dotted_order"),
                        "parent_run_id": operation.get("parent_run_id"),
                        "id": operation.get('id'),
                    }
                    create_params = {k: v for k, v in create_params.items() if v is not None}
                    logger.create_run(**create_params)
                    
                elif operation["operation"] == "patch":
                    end_time = operation.get("end_time")
                    if end_time and isinstance(end_time, str):
                        try:
                            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                        except ValueError:
                            end_time = None
                    
                    update_params = {
                        "run_id": operation.get("id"),
                        "end_time": end_time,
                        "outputs": operation.get("outputs", {}),
                        "error": operation.get("error"),
                        "trace_id": operation.get("trace_id"),
                        "dotted_order": operation.get("dotted_order"),
                        "parent_run_id": operation.get("parent_run_id"),
                    }
                    update_params = {k: v for k, v in update_params.items() if v is not None}
                    logger.update_run(**update_params)


def run_ls_benchmark(data_dir: str) -> Tuple[float, float, float, int]:
    """Run the Langsmith benchmark."""
    logger = Client()
    
    data_path = Path(data_dir)
    run_ops_files = list(data_path.glob("processed_run_ops_*.jsonl"))
    run_ops_files.sort()
    num_traces = len(run_ops_files)
    
    user_perceived_start = time.perf_counter()
    for run_ops_file in run_ops_files:
        try:
            LangsmithReplay.replay_trace(run_ops_file, logger)
        except Exception as e:
            print(f"Error replaying {run_ops_file}: {str(e)}", file=sys.stderr)
    
    user_perceived_time = time.perf_counter() - user_perceived_start
    
    flush_start = time.perf_counter()
    logger.flush()
    flush_time = time.perf_counter() - flush_start
    
    total_time = user_perceived_time + flush_time
    return user_perceived_time, flush_time, total_time, num_traces

def format_results(ls_results: Tuple[float, float, float, int],
                   data_dir: str) -> str:
    """Format benchmark results."""
    _, _, ls_total, num_traces = ls_results
    
    total_size = get_directory_size(data_dir)
    size_human = humanize.naturalsize(total_size)
    
    avg_ls = ls_total / num_traces if num_traces else 0
    
    return f"""\
Langsmith Benchmark Results
===========================
Time Breakdown:
    Total time      {ls_total:7.3f}s

Performance:
    Total Traces    {num_traces}
    Total Size      {size_human}
    Avg time/trace  {avg_ls:7.3f}s
"""


def main(data_dir: str):
    print("Running Langsmith benchmark...")
    ls_results = run_ls_benchmark(data_dir)
    
    results = format_results(ls_results, data_dir)
    print(results)
    
    with open("benchmark_results_nested.txt", "w") as f:
        f.write(results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark nested tracing performance (runs properly nested under parents)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python benchmark_nested.py data
        """
    )
    parser.add_argument(
        "data_dir",
        type=str,
        help="Directory containing processed_run_ops_*.jsonl trace files"
    )
    
    args = parser.parse_args()
    main(args.data_dir)
