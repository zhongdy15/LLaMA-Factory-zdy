from transformers import AutoTokenizer
import json
from pathlib import Path

tokenizer = AutoTokenizer.from_pretrained(
    "/mnt/zdy/Meta-Llama-3-8B-Instruct",
    use_fast=True
)

data_path = Path("../data/knn_sft_dataset_construction/output4_sft_training_data.json")

lengths = []

with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for sample in data:
    text = ""
    if "instruction" in sample:
        text += sample["instruction"]
    if "input" in sample and sample["input"]:
        text += sample["input"]
    if "output" in sample:
        text += sample["output"]

    tokens = tokenizer(text, add_special_tokens=False)["input_ids"]
    lengths.append(len(tokens))

lengths.sort()

def p(pct):
    return lengths[int(len(lengths) * pct)]

print(f"Total samples: {len(lengths)}")
print(f"Min tokens: {min(lengths)}")
print(f"Max tokens: {max(lengths)}")
print(f"P50 tokens: {p(0.5)}")
print(f"P90 tokens: {p(0.9)}")
print(f"P95 tokens: {p(0.95)}")
print(f"P99 tokens: {p(0.99)}")
