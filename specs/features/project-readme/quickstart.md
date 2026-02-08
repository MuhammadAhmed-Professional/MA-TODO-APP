# Quickstart Guide: Phase I Console Application

**Feature**: 003-project-readme (as documentation for Phase I)
**Date**: 2025-12-06

This document provides a concise quickstart guide for setting up and running the Phase I "Evolution of Todo" console application. These instructions will be integrated into the main `README.md` file.

## Prerequisites

*   **Operating System**: WSL 2 (for Windows users) or a native Linux environment.
*   **Python**: Python 3.13 or higher.
*   **UV**: Python package installer and resolver.

## Setup Instructions

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/evolution-of-todo.git
    cd evolution-of-todo
    ```
    (Note: Replace `https://github.com/your-repo/evolution-of-todo.git` with the actual repository URL.)

2.  **Install UV (if not already installed)**:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
    Ensure `uv` is in your PATH. You might need to add `~/.cargo/bin` to your shell's PATH.

3.  **Install Dependencies**:
    Navigate to the project root and install the Phase I dependencies using UV.
    ```bash
    uv init  # If pyproject.toml is not already set up
    uv pip install -r requirements.txt # Or uv add <package> if using pyproject.toml
    ```
    (Note: This assumes a `requirements.txt` or `pyproject.toml` exists for Phase I dependencies. If not, manual `uv add` commands would be needed for `pytest` or any other dependencies.)

4.  **Run the Application**:
    From the project root, run the console application as a Python module:
    ```bash
    python3 -m src.todo_app.main
    ```

5.  **Interact**:
    Follow the on-screen menu prompts to add, view, update, complete, or delete tasks.
