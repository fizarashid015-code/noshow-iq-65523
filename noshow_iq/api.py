from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from noshow_iq.model import predict as model_predict

app = Flask(__name__)

# Get MongoDB URI from environment variable — NEVER hardcode it
client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017"))
db = client["noshow_iq"]
predictions_col = db["predictions"]
training_runs_col = db["training_runs"]


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    result = model_predict(data)

    doc = {
        "timestamp": datetime.utcnow(),
        "raw_input": data,
        "risk_level": result["risk_level"],
        "probability": result["probability"],
        "recommendation": result["recommendation"],
    }
    predictions_col.insert_one(doc)

    return jsonify(result)


@app.route("/history")
def history():
    docs = list(predictions_col.find(
        {}, {"_id": 0}
    ).sort("timestamp", -1).limit(20))
    return jsonify(docs)


@app.route("/stats")
def stats():
    pipeline = [
        {
            "$facet": {
                "total": [{"$count": "count"}],
                "high_risk": [
                    {"$match": {"risk_level": "high"}},
                    {"$count": "count"}
                ],
                "low_risk": [
                    {"$match": {"risk_level": "low"}},
                    {"$count": "count"}
                ],
                "avg_prob": [
                    {"$group": {
                        "_id": None,
                        "avg": {"$avg": "$probability"}
                    }}
                ]
            }
        }
    ]
    result = list(predictions_col.aggregate(pipeline))[0]

    last_run = training_runs_col.find_one(
        {}, sort=[("timestamp", -1)]
    )

    return jsonify({
        "total_predictions": result["total"][0]["count"] if result["total"] else 0,
        "high_risk_count": result["high_risk"][0]["count"] if result["high_risk"] else 0,
        "low_risk_count": result["low_risk"][0]["count"] if result["low_risk"] else 0,
        "average_probability": round(result["avg_prob"][0]["avg"], 4) if result["avg_prob"] else 0,
        "last_trained": last_run["timestamp"].isoformat() if last_run else None,
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)