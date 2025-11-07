import asyncio
import argparse
import random
import dotenv
import time
from langsmith import traceable, Client

dotenv.load_dotenv()
client = Client()

@traceable(run_type="llm", metadata={"ls_provider": "openai", "ls_model_name": "gpt-4o-mini"})
async def mock_chat_completion(*, model, messages):
    # Sleep for 3 seconds each time
    await asyncio.sleep(3)
    input_tokens = random.randint(10000, 12000)
    output_tokens = random.randint(1000, 2000)
    return {
        "role": "assistant",
        "content": "This is a summary of the information provided.",
        "usage_metadata": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
    }

# Will be traced by default
async def target(inputs: dict) -> dict:
    messages = [
        {
            "role": "system",
            "content": "You are an expert summarizer."
        },
        # This dataset has inputs as a dict with a "email" key
        {"role": "user", "content": "Summarize this information:\n\n" + str(inputs)},
    ]
    res = await mock_chat_completion(
        model="gpt-4o-mini",
        messages=messages
    )

    return { "summary": res }


@traceable(run_type="llm", metadata={"ls_provider": "openai", "ls_model_name": "o3-mini"})
async def mock_evaluator_chat_completion(*, model, messages):
    await asyncio.sleep(2)
    # Mock return value
    input_tokens = random_number = random.randint(10000, 12000)
    output_tokens = random.randint(10, 20)
    return {
        "role": "assistant",
        "content": str(random.random()),
        "usage_metadata": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
        },
    }

async def mock_quality_evaluator(inputs: dict, outputs: dict):
    messages = [
        {
            "role": "system",
            "content": "Assign a quality score for the generated summary of an email."
        },
        {
            "role": "user",
            "content": f"""
Input info: {str(inputs)}
output: {outputs["summary"]}
"""
        },
    ]
    res = await mock_evaluator_chat_completion(
        model="o3-mini",
        messages=messages
    )
    return {
        "key": "quality",
        "score": float(res["content"]),
        "comment": "Score justification or other comments can go here.",
    }



async def run_eval(dataset_name: str):
    print("Starting LangSmith experiment!")
    start = time.perf_counter()

    experiment_results = await client.aevaluate(
        target,
        # dataset with 10,000 examples
        data=dataset_name, #"10k-long-emails"
        evaluators=[
            mock_quality_evaluator,
            # can add multiple evaluators here
        ],
        max_concurrency=1000,
    )

    finish_time = time.perf_counter()
    print(f"Experiment finished in {finish_time - start} seconds")
    client.flush()
    flush_time = time.perf_counter()
    print(f"All runs flushed to LangSmith in {flush_time - finish_time} seconds")
    return (finish_time - start, dataset_name, len(experiment_results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run evaluation on a LangSmith dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python eval_data.py 10k-long-emails
        """
    )
    parser.add_argument(
        "dataset_name",
        type=str,
        help="Name of the LangSmith dataset to evaluate"
    )
    
    args = parser.parse_args()
    results = asyncio.run(run_eval(args.dataset_name))
    print(results)