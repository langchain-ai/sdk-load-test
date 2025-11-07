import orjson
from pathlib import Path
import dotenv
import time
from datetime import datetime

from langsmith import Client

dotenv.load_dotenv()

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


def replay_all_traces(data_dir: str = "data") -> None:
    logger = Client()

    data_path = Path(data_dir)
    run_ops_files = list(data_path.glob("processed_run_ops_*.jsonl"))
    run_ops_files.sort()

    user_percieved_start_time = time.perf_counter()
    for run_ops_file in run_ops_files:
        try:
            replay_trace(run_ops_file, logger)
        except Exception as e:
            print(f"Error replaying {run_ops_file}: {str(e)}")

    user_percieved_time = time.perf_counter() - user_percieved_start_time
    print(f"User perceived time taken: {user_percieved_time} seconds")

    flush_time = time.perf_counter()
    logger.flush()
    flush_time = time.perf_counter() - flush_time
    print(f"Flush time: {flush_time} seconds")
    

if __name__ == "__main__":
    start_time = time.perf_counter()
    try:
        replay_all_traces()
    finally:
        end_time = time.perf_counter()
        print(f"Total time taken: {end_time - start_time} seconds")