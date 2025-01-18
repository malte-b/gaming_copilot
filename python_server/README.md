# Python Server Quick Start Guide

1. **(Optional) Install Poetry** if you don't have it yet:
   see [Poetry's docs](https://python-poetry.org/docs/#installation).

2. **Switch to the `python_server` directory**:

   ```bash
   cd python_server
   ```

3. **Generate `requirements.txt`** using Poetry:

   ```bash
   poetry export --without-hashes --format=requirements.txt > requirements.txt
   ```

4. **Install all dependencies** (no further Poetry usage required):

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the server** (still in `python_server`):
   ```bash
   uvicorn main:app --reload --port 5000
   ```
