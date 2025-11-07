# 🦜🛠 LangSmith SDK Benchmarks

## Pre-requisites

### 0. Install Python 3.11, poetry

If you use Homebrew, you can install poetry with:

```commandline
brew install poetry
```

### 1. Install Dependencies
```commandline
poetry install
```
### 2. Set Environment Variables
After installing dependencies, copy the `.env.example` file contents into `.env` and set the required values:
```commmandline
cp .env.example .env
```

<br>

## Running Benchmarks

This package provides an interactive script to run benchmarks end-to-end. Simply run:

```commandline
python run_benchmarks.py
```

This will present you with a menu to choose between:
1. **Tracing Benchmarks** - Benchmarks trace ingestion performance
2. **Evaluation Benchmarks** - Benchmarks evaluation performance
3. **Exit**

You can customize defaults for each benchmark type, or press Enter to use the defaults.

### Non-Interactive Mode

To run benchmarks without prompts (uses defaults - runs evaluation benchmarks):

```commandline
python run_benchmarks.py --non-interactive
```

<br>

## Tracing Benchmarks

### Overview
Tracing benchmarks measure the performance of ingesting traces into LangSmith. The script automatically:
1. Prepares trace files (replaces UUIDs and updates dates)
2. Runs flat tracing benchmark (runs get their own traces)
3. Runs nested tracing benchmark (runs properly nested under parents)

### Requirements
- Trace data files in JSONL format (`processed_run_ops_*.jsonl`) in the specified data directory
- Default data directory: `tracing/data`

### Running Tracing Benchmarks

**Via interactive script:**
```commandline
python run_benchmarks.py
# Select option 1 (Tracing Benchmarks)
# Enter data directory (default: data)
```

**Directly:**
```commandline
cd tracing
poetry run python benchmark_flat.py [data_dir]
poetry run python benchmark_nested.py [data_dir]
```

### Results
Results are printed to the terminal and saved to:
- `tracing/benchmark_results_flat.txt`
- `tracing/benchmark_results_nested.txt`

<br>

## Evaluation Benchmarks

### Overview
Evaluation benchmarks measure the performance of running evaluations on LangSmith datasets. The script automatically:
1. Benchmarks data upload performance (uploads CSV data to LangSmith)
2. Runs evaluation benchmarks on the uploaded dataset

**Note:** If the dataset already exists in LangSmith, the upload step will be skipped and the script will proceed directly to running evaluations.

### Requirements
- CSV data file in `evals/data/` directory
- Dataset configuration in `evals/config.json`
- Default dataset: `10k-long-emails-example`
- Default data directory: `evals/data`

### 1. Prepare Your Data

Place your CSV file in the `evals/data/` directory. The CSV file must be named `{dataset_name}.csv` where `{dataset_name}` matches the name you'll use in `config.json`.

### 2. Configure Dataset Mapping

You must specify in the ```evals/config.json``` file which CSV columns should be mapped to dataset inputs, and which columns should map to dataset outputs.

**Configuration Details:**
* **`inputs`**: A list of CSV column names that will be extracted from each row and set as the input data for each example in the LangSmith dataset. These columns will be converted to dictionaries (one per row) and passed to `client.create_examples(inputs=...)`.
* **`outputs`**: A list of CSV column names that will be extracted from each row and set as the expected outputs (ground truth) for each example in the LangSmith dataset. These columns will be converted to dictionaries (one per row) and passed to `client.create_examples(outputs=...)`. If empty (`[]`), no outputs will be uploaded.

**Example `config.json` structure:**
```json
{
    "_instructions": "This configuration file maps CSV datasets to LangSmith dataset structure...",
    "data_files": {
        "your-dataset-name": {
            "inputs": ["column1", "column2"],
            "outputs": ["expected_output"]
        }
    }
}
```

The CSV file must be named `{dataset_name}.csv` and placed in the `evals/data/` directory. The column names in `inputs` and `outputs` must match the column headers in your CSV file.

### 3. Run Evaluation Benchmarks

**Via interactive script:**
```commandline
python run_benchmarks.py
# Select option 2 (Evaluation Benchmarks)
# Enter dataset name (default: 10k-long-emails-example)
# Enter data directory (default: data)
```

**Directly:**
```commandline
cd evals
# First, benchmark data upload
poetry run python benchmark_upload.py [data_dir] [dataset_name]

# Then, run evaluation benchmarks
poetry run python benchmark_evals.py [dataset_name]
```

### Results
Results are printed to the terminal and saved to:
- `evals/benchmark_results_upload_data.txt` (upload benchmark results)
- `evals/benchmark_results_evals.txt` (evaluation benchmark results)

<br>

## Notes

- **Dataset Upload**: Data will be uploaded to LangSmith as part of the evaluation benchmarks workflow. If a dataset with the same name already exists in LangSmith, the upload step will be automatically skipped and the script will proceed directly to running evaluations.

- **Data Directory**: Both tracing and evaluation benchmarks allow you to specify custom data directories. Defaults are `data` for tracing and `evals/data` for evaluations.

- **Trace Data Preparation**: For tracing benchmarks, UUID replacement and date updates are automatically handled before running benchmarks. These steps run silently in the background.