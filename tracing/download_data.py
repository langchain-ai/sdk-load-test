from langsmith import Client
import orjson
import dotenv


trace_ids = { # Replace with your trace ids
    "1efcf279-c279-613f-b5c6-4705c507f3e7",
    "1efcf279-6c93-6b57-8468-788f550a4171",
    "1efcf237-d278-65a7-a2da-d75c39571b51",
    "1efcf1f3-3ee1-6643-9513-f19ec6ea38cd",
    "1efcf164-fcce-66e1-bb63-0673854ee9f4",
    "1efcf15f-521f-642b-92b3-9cc39ad0e414",
    "1efcf15f-2725-61b3-a8fc-ad30facd29bd",
    "1efcf12d-d85d-6780-9300-cf174385be8d",
    "1efcf134-212d-6350-af0e-01e79b5c5b02",
    "1efcf115-bfd6-6945-a028-11213eca6861",
    "1efcf108-9282-6966-8ef1-d0c5f16d23da",
    "1efcf102-e767-6629-bd02-16bafbb1bfb4",
    "1efcf0d6-43bf-6ff8-b12a-47a79c940b6e",
    "1efcf0d4-2007-6727-be94-9884ee1c0cbe",
    "1efcf0d2-5e61-6a0d-b6d3-e9666f398dfa",
    "1efcf0cf-d5e7-6b82-9635-7ee2bb254b18",
    "1efcf0cd-a49f-665b-9894-52d508078fc1",
    "1efcf0be-fc26-6bee-9361-51e9631e9f99",
    "1efcf09b-9bcb-68e6-8cc5-da2673832877",
    "1efcf072-10ee-684d-ab63-51194ccc7955",
    "1efcf06c-ec82-63c2-a2ec-1e69717454c1",
    "1efcf05a-5bac-6bba-98d1-978315c98f98",
    "1efcf04a-a9ae-60a6-b899-19ba02b2c8ea",
    "1efcf01f-fb89-61bd-a8ba-1123f9f48458",
    "1efcefe2-7fe1-6ff4-9ea8-300f343970e1",
    "1efcef47-59e3-6165-bac0-1a6524c25453",
    "1efceee0-a5ba-6a89-b1eb-181a839b2a28",
    "1efceed5-37db-6423-a76f-974355024b85",
    "1efceecb-b89e-6a62-8140-0d9edfbe5225",
    "1efceec9-8695-6c1b-a4eb-eaab38afce6c",
    "1efcee40-3791-6296-a156-5207b6f9291c",
}

def produce_run_ops_jsonl_files():
    client = Client()
    for trace_id in trace_ids:
        results = client.list_runs(
            project_name='example-project', # Replace with your project name
            trace_id=trace_id,
        )
        results = list(results)
        results.sort(key=lambda x: x.dotted_order)
        with open(f'data/processed_run_ops_{trace_id}.jsonl', 'wb') as run_ops_file:
            for run in results:
                run_dict = dict(run)
                post = {
                    "operation": "post",
                    "id": run_dict["id"],
                    "name": run_dict["name"],
                    "start_time": run_dict["start_time"],
                    "serialized": run_dict["serialized"],
                    "events": run_dict["events"],
                    "inputs": run_dict["inputs"],
                    "run_type": run_dict["run_type"],
                    "extra": run_dict["extra"],
                    "tags": run_dict["tags"],
                    "trace_id": run_dict["trace_id"],
                    "dotted_order": run_dict["dotted_order"],
                    "parent_run_id": run_dict["parent_run_id"],
                }
                run_ops_file.write(orjson.dumps(post))
                run_ops_file.write(b'\n')
                patch = {
                    "operation": "patch",
                    "id": run_dict["id"],
                    "name": run_dict["name"],
                    "end_time": run_dict["end_time"],
                    "error": run_dict["error"],
                    "outputs": run_dict["outputs"],
                    "trace_id": run_dict["trace_id"],
                    "dotted_order": run_dict["dotted_order"],
                    "parent_run_id": run_dict["parent_run_id"],
                }
                run_ops_file.write(orjson.dumps(patch))
                run_ops_file.write(b'\n')

if __name__ == "__main__":
    dotenv.load_dotenv()
    produce_run_ops_jsonl_files()