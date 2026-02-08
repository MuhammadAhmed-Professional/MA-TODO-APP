#!/bin/bash
# Script to run TaskCard and TaskForm tests

cd "$(dirname "$0")"
echo "Running TaskCard and TaskForm unit tests..."
npm test -- tests/unit/TaskCard.test.tsx tests/unit/TaskForm.test.tsx --reporter=verbose
