from typing import Tuple
import asyncio
import argparse
from eval_data import run_eval


def format_results(ls_results: Tuple[float, str, int]) -> str:
    """Format benchmark results."""
    ls_time, _, ls_examples = ls_results
    
    # Use the number of examples from the results
    num_examples = ls_examples
    
    avg_ls = ls_time / num_examples if num_examples else 0
    
    return f"""\
Langsmith Benchmark Results
===========================
Time Breakdown:
    Total time      {ls_time:7.3f}s

Performance:
    Total Examples    {num_examples}
"""

async def run_benchmark(dataset_name: str):
    print("Running Langsmith benchmark...")
    langsmith_results = await run_eval(dataset_name)
    table = format_results(langsmith_results)
    
    # Print to console
    print("\nBenchmark Results:\n")
    print(table)
    
    # Save results to a file
    with open("benchmark_results_evals.txt", "w") as f:
        f.write(table)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Benchmark evaluation performance on a LangSmith dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python benchmark_evals.py 10k-long-emails
        """
    )
    parser.add_argument(
        "dataset_name",
        type=str,
        help="Name of the LangSmith dataset to benchmark"
    )
    
    args = parser.parse_args()
    asyncio.run(run_benchmark(args.dataset_name))