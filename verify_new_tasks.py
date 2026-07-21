#!/usr/bin/env python3
"""Verify that new tasks are properly structured."""

from runner.loader import TaskLoader

loader = TaskLoader('tasks')
new_tasks = [
    'calculate-statistics',
    'transform-data-format',
    'fix-broken-script',
    'find-security-issues',
    'optimize-query'
]

print("Verifying new tasks...")
print("-" * 60)

all_valid = True
for task_id in new_tasks:
    try:
        metadata = loader.validate_task_structure(task_id)
        status = "✓ VALID" if metadata.is_valid else "✗ INVALID"
        print(f"{status} - {task_id}")
        
        if not metadata.is_valid:
            all_valid = False
            for error in metadata.validation_errors:
                print(f"    Error: {error}")
        
        # Show task details
        config = metadata.config
        print(f"    Category: {config.category}, Difficulty: {config.difficulty}")
        print(f"    Has instruction: {metadata.has_instruction}")
        print(f"    Has solution: {metadata.has_solution}")
        print(f"    Has tests: {metadata.has_tests}")
        print(f"    Has environment: {metadata.has_environment}")
        print()
    
    except Exception as e:
        print(f"✗ ERROR - {task_id}: {e}\n")
        all_valid = False

print("-" * 60)
if all_valid:
    print("✓ All new tasks are properly structured!")
else:
    print("✗ Some tasks have issues")
