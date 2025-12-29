from flask import Flask, jsonify, render_template, request
import csv
import os
from datetime import datetime
from utils.ui import UI_runner
from utils.fileprocessor import load_data

csv_data = []
headers = []
filePath = ""
remarks_file = ""
remark_columns = []

filePath = UI_runner()
headers, csv_data = load_data(filePath)

# Convert rows to dictionaries if they're lists
if csv_data and isinstance(csv_data[0], list):
    csv_data = [dict(zip(headers, row)) for row in csv_data]

# Generate remarks file name
base_name = os.path.splitext(filePath)[0]
remarks_file = f"{base_name}_with_remarks.csv"

app = Flask(__name__, template_folder='templates')

def get_remark_columns():
    """Get the list of remark columns from the file"""
    global remark_columns
    if os.path.exists(remarks_file):
        with open(remarks_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            file_headers = next(reader)
            # Get columns that are not in original headers
            remark_columns = [h for h in file_headers if h not in headers]
    return remark_columns

def initialize_remarks_file():
    """Create remarks file with headers if it doesn't exist"""
    global remark_columns
    if not os.path.exists(remarks_file):
        remark_columns = []
        with open(remarks_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

            # Write all rows
            for row in csv_data:
                writer.writerow([row.get(h, '') for h in headers])
    else:
        get_remark_columns()

def read_remarks_file():
    """Read existing remarks from file"""
    remarks_data = {}
    if os.path.exists(remarks_file):
        try:
            with open(remarks_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    remarks_data[i] = row
        except Exception as e:
            print(f"Error reading remarks file: {e}")
    return remarks_data

def update_remark_in_file(row_index, remark_values):
    """Update a specific row's remark in the CSV file"""
    try:
        global remark_columns
        rows = []

        # Read current data
        with open(remarks_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            current_headers = reader.fieldnames
            rows = list(reader)

        # Determine new columns needed
        num_new_cols = len(remark_values)
        new_col_names = [f"Remark_{i+1}" for i in range(num_new_cols)]

        # Check if we need to add new columns
        existing_remark_cols = [h for h in current_headers if h.startswith("Remark_")]
        if len(existing_remark_cols) < num_new_cols:
            # Need to add more columns
            for i in range(len(existing_remark_cols), num_new_cols):
                current_headers.append(f"Remark_{i+1}")

        # Update the specific row
        if 0 <= row_index < len(rows):
            for i, value in enumerate(remark_values):
                col_name = f"Remark_{i+1}"
                if col_name not in rows[row_index]:
                    rows[row_index][col_name] = ''
                rows[row_index][col_name] = value.strip()

        # Ensure all rows have all columns
        for row in rows:
            for header in current_headers:
                if header not in row:
                    row[header] = ''

        # Write back to file
        with open(remarks_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=current_headers)
            writer.writeheader()
            writer.writerows(rows)

        get_remark_columns()
        return True
    except Exception as e:
        print(f"Error updating remark: {e}")
        return False

@app.route("/api/data", methods=["GET"])
def get_filtered_data():
    """Get data with optional filtering"""
    if not csv_data:
        return jsonify({"error": "No CSV data loaded."}), 404

    filter_column = request.args.get('column')
    filter_value = request.args.get('value')
    search_term = request.args.get('search', '').lower()

    filtered_data = csv_data.copy()

    if filter_column and filter_value and filter_column in headers:
        filtered_data = [
            row for row in filtered_data
            if str(row.get(filter_column, '')).lower() == filter_value.lower()
        ]

    if search_term:
        filtered_data = [
            row for row in filtered_data
            if any(search_term in str(value).lower() for value in row.values())
        ]

    remarks_data = read_remarks_file()

    result = []
    for i, row in enumerate(csv_data):
        if row in filtered_data:
            row_with_remark = row.copy()
            if i in remarks_data:
                for col in remark_columns:
                    row_with_remark[col] = remarks_data[i].get(col, '')
            row_with_remark['_index'] = i
            result.append(row_with_remark)

    return jsonify({
        "data": result,
        "total": len(result),
        "remark_columns": remark_columns
    })

@app.route("/api/headers", methods=["GET"])
def get_headers():
    """Get CSV headers"""
    if not headers:
        return jsonify({"error": "No CSV headers found."}), 404
    return jsonify({
        "headers": headers,
        "remark_columns": remark_columns
    })

@app.route("/api/remarks/<int:row_index>", methods=["POST"])
def add_remark(row_index):
    """Add or update a remark for a specific row"""
    if not csv_data:
        return jsonify({"error": "No CSV data loaded."}), 404

    if not (0 <= row_index < len(csv_data)):
        return jsonify({"error": "Invalid row index."}), 404

    data = request.get_json()
    remark = data.get('remark', '')

    # Parse comma-separated values
    remark_values = [v.strip() for v in remark.split(',') if v.strip()]

    if not remark_values:
        return jsonify({"error": "No remark values provided"}), 400

    success = update_remark_in_file(row_index, remark_values)

    if success:
        return jsonify({
            "success": True,
            "row_index": row_index,
            "remark_values": remark_values,
            "file": remarks_file
        })
    else:
        return jsonify({"error": "Failed to update remark"}), 500

@app.route("/api/filter-options", methods=["GET"])
def get_filter_options():
    """Get unique values for each column"""
    if not csv_data or not headers:
        return jsonify({"error": "No CSV data loaded."}), 404

    filter_options = {}
    for header in headers:
        unique_values = set()
        for row in csv_data:
            if isinstance(row, dict):
                value = row.get(header, '')
            else:
                try:
                    idx = headers.index(header)
                    value = row[idx] if idx < len(row) else ''
                except (ValueError, IndexError):
                    value = ''

            if value:
                unique_values.add(str(value))
        filter_options[header] = sorted(list(unique_values))

    return jsonify(filter_options)

@app.route("/", methods=["GET"])
def ui_page():
    return render_template("index.html")

if __name__ == "__main__":
    initialize_remarks_file()
    app.run(debug=False)
