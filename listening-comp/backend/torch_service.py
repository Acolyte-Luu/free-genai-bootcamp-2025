# A separate service that runs PyTorch operations
import torch
from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/embed', methods=['POST'])
def embed_text():
    # Use PyTorch here
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(port=5000) 