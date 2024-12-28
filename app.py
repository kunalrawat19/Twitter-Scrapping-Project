from flask import Flask, render_template, jsonify
from scraper import fetch_trending_topics
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/run-script", methods=["POST"])
def run_script():
    try:
        # Fetch trends
        result = fetch_trending_topics()
        print(f"Fetched data: {result}")  # Debugging print statement
        return jsonify(result)
    except Exception as e:
        print(f"Error: {str(e)}")  # Log any error
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
