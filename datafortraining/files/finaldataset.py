import json
import re

SOURCE_DATASET = "datafortraining/outputs/intent_dataset.json"
TARGET_DATASET = "datafortraining/outputs/final_dataset.json"

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# Detect conditional modifiers
def detect_conditional(text):
    text = text.lower()
    conditional_phrases = [
        "if possible",
        "when you get a chance",
        "as soon as you can",
        "whenever that works",
        "if you can",
        "just to be clear"
    ]
    return any(p in text for p in conditional_phrases)

def convert_entry(entry):
    natural = entry["natural_language"]
    params = entry["parameters"]

    intent_type = entry["intent_type"]
    intent_action = entry["intent_action"]   # <-- USE THIS DIRECTLY
    intent_sub_type = entry["intent_sub_type"]
    device = params["device"]
    constraints = entry.get("policy", {}).get("constraints", {})
    platform = params["platform"]["id"]
    interface = params.get("interface")
    port = params.get("port")
    conditional = detect_conditional(natural)

    # Build parameters excluding device/platform/interface/port
    parameters = {
        k: v for k, v in params.items()
        if k not in ["device", "platform", "interface", "port"]
    }

    # Build entities
    entities = {"device": device}
    if interface:
        entities["interface"] = interface
    if port:
        entities["port"] = port

    converted = {
        "input": natural,
        "output": {
            "intent": {
                "domain": intent_type,
                "sub_domain": intent_sub_type,
                "operation": intent_action 
            },
            "entities": entities,
            "parameters": parameters,
            "modifiers": {
                "conditional": conditional
            }
        }
    }

    return converted

def convert_dataset():
    dataset = load_json(SOURCE_DATASET)
    converted = [convert_entry(item) for item in dataset]
    save_json(TARGET_DATASET, converted)
    print(f"Converted dataset saved to {TARGET_DATASET}")

if __name__ == "__main__":
    convert_dataset()
