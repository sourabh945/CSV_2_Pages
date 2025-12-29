
from flask import Flask, jsonify, render_template
from flask.json import load

from utils.ui import UI_runner
from utils.fileprocessor import load_data

csv_data = []
headers = []

filePath = UI_runner()
headers, csv_data = load_data(filePath)

app = Flask(__name__, template_folder='templates')


@app.route(f"/api/data/<id>", methods=["GET"])
def get_next_row(id):
    if not csv_data:
        return jsonify({"error": "No CSV data loaded."}), 404

    try:
        # Convert the id from the URL into an integer
        row_index = int(id)

        # Check if the index is valid
        if 0 <= row_index < len(csv_data):
            row = csv_data[row_index]
            return jsonify(row)
        else:
            # If the index is out of bounds, return an error
            return jsonify({"error": "Row not found."}), 404

    except (ValueError, IndexError):
        # Handle cases where id is not a number or index is out of range
        return jsonify({"error": "Invalid row ID."}), 404


@app.route("/api/headers", methods=["GET"])
def get_headers():
    if not headers:
        return jsonify({"error": "No CSV headers found."}), 404
    return jsonify(headers)



@app.route("/", methods=["GET"])
def ui_page():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=False)
