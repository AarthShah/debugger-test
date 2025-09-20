# Quick Start Guide

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Get Gemini API Key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Set environment variable:
     ```bash
     export GEMINI_API_KEY="your_api_key_here"
     ```

## Basic Usage

### 1. Index Your Codebase
```bash
python main.py index --project-path .
```

### 2. Search for Code
```bash
python main.py search "function that calculates average"
```

### 3. Diagnose Errors
```bash
python main.py diagnose "ZeroDivisionError: division by zero"
```

### 4. Get Explanations
```bash
python main.py explain --file-path sample_buggy_code.py --function calculate_average
```

### 5. Get Improvements
```bash
python main.py improve --file-path sample_buggy_code.py --function process_user_data
```

## Example Error Scenarios

Try these with the included `sample_buggy_code.py`:

1. **Division by Zero:**
   ```bash
   python sample_buggy_code.py  # Run to see errors
   python main.py diagnose "ZeroDivisionError: division by zero"
   ```

2. **Name Error:**
   ```bash
   python main.py diagnose "NameError: name 'username' is not defined"
   ```

3. **Index Error:**
   ```bash
   python main.py diagnose "IndexError: list index out of range"
   ```

## Demo Without Dependencies

Run the lightweight demo to see core parsing:
```bash
python demo.py
```

This shows how the system parses your codebase into semantic chunks without requiring the ML dependencies.