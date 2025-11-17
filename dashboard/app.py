from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.get("/metrics")
def get_metrics():
    with open("metrics.json") as f:
        data = json.load(f)
    return data

@app.get("/")
def home():
    return "Distributed Monitoring Dashboard Running!"
