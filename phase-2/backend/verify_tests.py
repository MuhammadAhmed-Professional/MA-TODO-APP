#!/usr/bin/env python3
"""
Verification Script for Task Service Unit Tests

This script performs static analysis on the test file to verify:
1. All required tests are present
2. Test naming conventions are followed
3. Proper imports are included
4. Test structure is correct
"""

import ast
import sys
from pathlib import Path


def analyze_test_file(test_file_path: Path) -> dict:
    """
    Analyze the test file and extract information.

    Returns:
        dict with test counts, classes, and methods
    """
    with open(test_file_path, 'r') as f:
        tree = ast.parse(f.read())

    test_classes = []
    test_methods = []
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if node.name.startswith('Test'):
                test_classes.append(node.name)
                # Count methods in this class
                class_methods = [
                    m.name for m in node.body
                    if isinstance(m, ast.FunctionDef) and m.name.startswith('test_')
                ]
                test_methods.extend(class_methods)

        if isinstance(node, ast.ImportFrom):
            imports.append(f"from {node.module} import ...")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")

    return {
        'test_classes': test_classes,
        'test_methods': test_methods,
        'test_count': len(test_methods),
        'class_count': len(test_classes),
        'imports': imports
    }


def verify_required_tests(test_methods: list) -> tuple[list, list]:
    """
    Verify that all required tests are present.

    Returns:
        (found_tests, missing_tests)
    """
    required_tests = [
        # Task Creation
        'test_create_task_success',
        'test_create_task_raises_error_for_empty_title',

        # Get User Tasks
        'test_get_user_tasks_returns_only_owned_tasks',
        'test_get_user_tasks_empty_list',
        'test_get_user_tasks_filters_by_completion_status',

        # Get Task
        'test_get_task_success',
        'test_get_task_not_found',
        'test_get_task_ownership_validation_fails',

        # Update Task
        'test_update_task_success',
        'test_update_task_ownership_validation',
        'test_update_task_not_found',
        'test_update_task_raises_error_for_empty_title',

        # Toggle Complete
        'test_toggle_complete_updates_status',
        'test_toggle_complete_idempotent',
        'test_toggle_complete_ownership_check',

        # Delete Task
        'test_delete_task_removes_from_db',
        'test_delete_task_ownership_check',
        'test_delete_task_not_found',
    ]

    found = [t for t in required_tests if t in test_methods]
    missing = [t for t in required_tests if t not in test_methods]

    return found, missing


def main():
    """Main verification function"""
    test_file = Path(__file__).parent / 'tests' / 'unit' / 'test_task_service.py'

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        sys.exit(1)

    print("=" * 70)
    print("Task Service Unit Tests - Verification Report")
    print("=" * 70)
    print()

    # Analyze test file
    analysis = analyze_test_file(test_file)

    # Print summary
    print(f"📊 Test Summary:")
    print(f"   Total test classes: {analysis['class_count']}")
    print(f"   Total test methods: {analysis['test_count']}")
    print()

    # Print test classes
    print(f"📁 Test Classes:")
    for cls in analysis['test_classes']:
        print(f"   ✓ {cls}")
    print()

    # Verify required tests
    found, missing = verify_required_tests(analysis['test_methods'])

    print(f"✅ Required Tests Found ({len(found)}/{len(found) + len(missing)}):")
    for test in found:
        print(f"   ✓ {test}")
    print()

    if missing:
        print(f"❌ Missing Required Tests ({len(missing)}):")
        for test in missing:
            print(f"   ✗ {test}")
        print()

    # Print all test methods
    print(f"📝 All Test Methods ({len(analysis['test_methods'])}):")
    for i, method in enumerate(analysis['test_methods'], 1):
        print(f"   {i:2d}. {method}")
    print()

    # Print imports
    print(f"📦 Key Imports:")
    key_imports = [
        'import pytest',
        'from fastapi import HTTPException',
        'from src.models.task import',
        'from src.services.task_service import'
    ]
    for imp in analysis['imports']:
        if any(key in imp for key in key_imports):
            print(f"   ✓ {imp}")
    print()

    # Final verdict
    print("=" * 70)
    if missing:
        print("⚠️  VERIFICATION: INCOMPLETE - Some required tests are missing")
        print("=" * 70)
        sys.exit(1)
    else:
        print("✅ VERIFICATION: PASSED - All required tests are present")
        print("=" * 70)
        print()
        print("Next steps:")
        print("1. Run tests: uv run pytest tests/unit/test_task_service.py -v")
        print("2. Check coverage: uv run pytest tests/unit/test_task_service.py --cov=src.services.task_service")
        print()
        sys.exit(0)


if __name__ == '__main__':
    main()
