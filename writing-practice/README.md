# Japanese Writing Practice App

A Gradio-based application for practicing Japanese writing with automatic feedback.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure your LocalLLM wrapper is properly configured.

3. Ensure the vocabulary API is running at `localhost:5000/api/groups/:id/raw`

4. Run the application:
   ```
   python app.py
   ```

## Features

- Generates simple Japanese practice sentences using JLPT N5 grammar
- OCR for submitted handwritten Japanese
- Automatic translation and grading of submissions
- Interactive UI with practice and review modes 