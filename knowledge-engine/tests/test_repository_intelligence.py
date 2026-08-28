import json

from app.repository_intelligence import (
    build_repository_modules,
    repository_summary,
)

with open("data/repository_metadata.json", "r", encoding="utf-8") as f:
    metadata = json.load(f)

print("\n========== REPOSITORY SUMMARY ==========\n")

summary = repository_summary(metadata)

print(json.dumps(summary, indent=2))

print("\n========== SELECTED MODULES ==========\n")

modules = build_repository_modules(
    metadata,
    max_modules=6,
    start_step=1,
)

for module in modules:
    print(json.dumps(module, indent=2))
    print("-" * 80)