#!/usr/bin/env python3
"""
Interactive script to run benchmarks end-to-end.

This script provides a menu interface to:
- Run tracing benchmarks (with UUID replacement and date updates)
- Run evaluation benchmarks (with data upload)
- Customize defaults for each benchmark type
"""
import argparse
import subprocess
import sys
from pathlib import Path
import dotenv

dotenv.load_dotenv()

def run_command(cmd, cwd, description, check=True, verbose=True):
    """Run a command and handle errors."""
    if verbose:
        print(f"\n{'='*60}")
        print(f"Running: {description}")
        print(f"{'='*60}")
        print(f"Command: {' '.join(cmd)}")
        print(f"Working directory: {cwd}\n")
    
    # Always capture output so we can check for specific errors
    result = subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True)
    
    # Check if this is an "already exists" error before printing output
    error_output = ""
    if result.stdout:
        error_output += result.stdout
    if result.stderr:
        error_output += result.stderr
    
    is_already_exists_error = "already exists" in error_output.lower()
    
    if verbose and not is_already_exists_error:
        # Print output in real-time fashion for verbose mode (unless it's an expected error)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    
    if check and result.returncode != 0:
        if not verbose:
            print(f"\nError: {description} failed with exit code {result.returncode}")
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
        elif not is_already_exists_error:
            # Only print error details if it's not an expected "already exists" error
            print(f"\nError: {description} failed with exit code {result.returncode}")
        return False, result
    return True, result

def run_tracing_benchmarks(data_dir="data"):
    """Run tracing benchmarks end-to-end."""
    project_root = Path(__file__).parent.absolute()
    tracing_dir = project_root / "tracing"
    
    if not tracing_dir.exists():
        print(f"Error: Tracing directory not found at {tracing_dir}")
        return False
    
    print("\n" + "="*60)
    print("TRACING BENCHMARKS")
    print("="*60)
    
    # Step 1: Run replace_uuids (silent)
    success, _ = run_command(
        [sys.executable, "utils/replace_uuids.py"],
        cwd=str(tracing_dir),
        description="Preparing trace files",
        check=True,
        verbose=False
    )
    if not success:
        return False
    
    # Step 2: Run update_dates (silent)
    success, _ = run_command(
        [sys.executable, "utils/update_dates.py"],
        cwd=str(tracing_dir),
        description="Preparing trace files",
        check=True,
        verbose=False
    )
    if not success:
        return False
    
    # Step 3: Run flat benchmark
    print("\nSTEP 1: Running flat tracing benchmark")
    success, _ = run_command(
        [sys.executable, "benchmark_flat.py", data_dir],
        cwd=str(tracing_dir),
        description="Flat tracing benchmark"
    )
    if not success:
        return False
    
    # Step 4: Run nested benchmark
    print("\nSTEP 2: Running nested tracing benchmark")
    success, _ = run_command(
        [sys.executable, "benchmark_nested.py", data_dir],
        cwd=str(tracing_dir),
        description="Nested tracing benchmark"
    )
    if not success:
        return False
    
    print("\n" + "="*60)
    print("SUCCESS: All tracing benchmarks completed!")
    print("="*60)
    print(f"\nResults saved to:")
    print(f"  - {tracing_dir}/benchmark_results_flat.txt")
    print(f"  - {tracing_dir}/benchmark_results_nested.txt")
    return True

def run_evals_benchmarks(dataset="10k-long-emails-example", data_dir="data"):
    """Run evaluation benchmarks end-to-end."""
    project_root = Path(__file__).parent.absolute()
    evals_dir = project_root / "evals"
    
    if not evals_dir.exists():
        print(f"Error: Evals directory not found at {evals_dir}")
        return False
    
    print("\n" + "="*60)
    print("EVALUATION BENCHMARKS")
    print("="*60)
    
    # Step 1: Benchmark data upload
    print("\nSTEP 1: Benchmarking data upload")
    
    # Run benchmark_upload.py
    success, result = run_command(
        [sys.executable, "benchmark_upload.py", data_dir, dataset],
        cwd=str(evals_dir),
        description=f"Benchmark upload for dataset '{dataset}'",
        check=False
    )
    
    if not success:
        # Check if failure was due to dataset already existing
        error_output = ""
        if result.stdout:
            error_output += result.stdout
        if result.stderr:
            error_output += result.stderr
        
        if "already exists" in error_output.lower():
            print(f"\nDataset '{dataset}' already exists - skipping upload benchmark")
            print("Moving directly to evaluation benchmarks...\n")
        else:
            # Different error, fail
            return False
    
    # Step 2: Run evaluation benchmarks
    print("\nSTEP 2: Running evaluation benchmarks")
    success, _ = run_command(
        [sys.executable, "benchmark_evals.py", dataset],
        cwd=str(evals_dir),
        description=f"Evaluation benchmark for dataset '{dataset}'"
    )
    if not success:
        return False
    
    print("\n" + "="*60)
    print("SUCCESS: All evaluation benchmarks completed!")
    print("="*60)
    print(f"\nResults saved to:")
    print(f"  - {evals_dir}/benchmark_results_evals.txt")
    return True

def get_user_input(prompt, default=None, input_type=str):
    """Get user input with optional default."""
    if default is not None:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    user_input = input(full_prompt).strip()
    
    if not user_input and default is not None:
        return default
    
    if not user_input:
        return None
    
    try:
        return input_type(user_input)
    except ValueError:
        print(f"Invalid input. Please enter a valid {input_type.__name__}.")
        return get_user_input(prompt, default, input_type)

def main():
    parser = argparse.ArgumentParser(
        description="Interactive script to run benchmarks end-to-end",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script provides an interactive menu to run benchmarks:
- Tracing benchmarks: Runs UUID replacement, date updates, and both flat/nested benchmarks
- Evaluation benchmarks: Uploads data and runs evaluation benchmarks

Example:
  python run_benchmarks.py
        """
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Run in non-interactive mode (use defaults)"
    )
    
    args = parser.parse_args()
    
    if args.non_interactive:
        # Non-interactive mode: run all evals by default
        print("Running in non-interactive mode - executing all evaluation benchmarks...")
        success = run_evals_benchmarks()
        sys.exit(0 if success else 1)
    
    # Interactive mode
    print("\n" + "="*60)
    print("LangSmith SDK Benchmarks")
    print("="*60)
    print("\nSelect benchmark type:")
    print("1. Tracing Benchmarks")
    print("2. Evaluation Benchmarks")
    print("3. Exit")
    
    choice = get_user_input("\nEnter your choice", default="2", input_type=int)
    
    if choice == 1:
        # Tracing benchmarks
        print("\n" + "-"*60)
        print("Tracing Benchmarks Configuration")
        print("-"*60)
        data_dir = get_user_input(
            "Enter data directory containing trace files",
            default="data"
        )
        
        if not data_dir:
            print("Error: Data directory is required")
            sys.exit(1)
        
        success = run_tracing_benchmarks(data_dir)
        sys.exit(0 if success else 1)
        
    elif choice == 2:
        # Evaluation benchmarks
        print("\n" + "-"*60)
        print("Evaluation Benchmarks Configuration")
        print("-"*60)
        dataset = get_user_input(
            "Enter dataset name (must exist in config.json)",
            default="10k-long-emails-example"
        )
        data_dir = get_user_input(
            "Enter data directory containing CSV files",
            default="data"
        )
        
        if not dataset:
            print("Error: Dataset name is required")
            sys.exit(1)
        if not data_dir:
            print("Error: Data directory is required")
            sys.exit(1)
        
        success = run_evals_benchmarks(dataset, data_dir)
        sys.exit(0 if success else 1)
        
    elif choice == 3:
        print("\nExiting...")
        sys.exit(0)
    else:
        print("\nInvalid choice. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    main()

