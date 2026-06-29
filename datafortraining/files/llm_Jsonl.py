import json

INPUT_PATH = "datafortraining/outputs/final_dataset.json"
OUTPUT_PATH = "datafortraining/outputs/llama_training.jsonl"

INSTRUCTION = (
    "Convert the following natural language intent into structured JSON with "
    "intent.domain, intent.operation, entities, parameters, and modifiers."
)

def to_jsonl(entry):
    nl = entry["input"]           # natural language
    output_obj = entry["output"]  # already structured

    return {
        "instruction": INSTRUCTION,
        "input": nl,
        "output": json.dumps(output_obj, indent=2),
        "response_format": "json"
    }

# Load dataset
with open(INPUT_PATH, "r") as f:
    dataset = json.load(f)

# Write JSONL
with open(OUTPUT_PATH, "w") as f:
    for entry in dataset:
        jsonl_entry = to_jsonl(entry)
        f.write(json.dumps(jsonl_entry) + "\n")

print(f"LLAMA training JSONL created at: {OUTPUT_PATH}")
