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

def update_remark_in_file(row_index, column=None, value=None, remark_values=None):
    """Update a specific row's remark in the CSV file"""
    try:
        global remark_columns
        rows = []

        # Read current data
        with open(remarks_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            current_headers = list(reader.fieldnames)
            rows = list(reader)

        # Mode 1: Set specific column value
        if column is not None and value is not None:
            # Add column if it doesn't exist
            if column not in current_headers:
                current_headers.append(column)

            # Update the specific row
            if 0 <= row_index < len(rows):
                rows[row_index][column] = value

        # Mode 2: Add comma-separated values to Remark_N columns
        elif remark_values is not None:
            num_new_cols = len(remark_values)

            # Check if we need to add new columns
            existing_remark_cols = [h for h in current_headers if h.startswith("Remark_")]
            if len(existing_remark_cols) < num_new_cols:
                for i in range(len(existing_remark_cols), num_new_cols):
                    current_headers.append(f"Remark_{i+1}")

            # Update the specific row
            if 0 <= row_index < len(rows):
                for i, val in enumerate(remark_values):
                    col_name = f"Remark_{i+1}"
                    rows[row_index][col_name] = val.strip()

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

def rename_remark_column(old_name, new_name):
    """Rename a remark column in the CSV file"""
    try:
        global remark_columns
        rows = []

        with open(remarks_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            current_headers = list(reader.fieldnames)
            rows = list(reader)

        if old_name not in current_headers:
            return False

        # Rename in headers
        header_index = current_headers.index(old_name)
        current_headers[header_index] = new_name

        # Rename in all rows
        for row in rows:
            if old_name in row:
                row[new_name] = row.pop(old_name)

        # Write back to file
        with open(remarks_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=current_headers)
            writer.writeheader()
            writer.writerows(rows)

        get_remark_columns()
        return True
    except Exception as e:
        print(f"Error renaming column: {e}")
        return False

def add_remark_column(column_name):
    """Add a new remark column to the CSV file"""
    try:
        global remark_columns
        rows = []

        with open(remarks_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            current_headers = list(reader.fieldnames)
            rows = list(reader)

        if column_name in current_headers:
            return False  # Column already exists

        current_headers.append(column_name)

        # Add empty value to all rows
        for row in rows:
            row[column_name] = ''

        # Write back to file
        with open(remarks_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=current_headers)
            writer.writeheader()
            writer.writerows(rows)

        get_remark_columns()
        return True
    except Exception as e:
        print(f"Error adding column: {e}")
        return False

def delete_remark_column(column_name):
    """Delete a remark column from the CSV file"""
    try:
        global remark_columns
        rows = []

        with open(remarks_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            current_headers = list(reader.fieldnames)
            rows = list(reader)

        if column_name not in current_headers or column_name in headers:
            return False  # Can't delete original headers

        current_headers.remove(column_name)

        # Remove from all rows
        for row in rows:
            if column_name in row:
                del row[column_name]

        # Write back to file
        with open(remarks_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=current_headers)
            writer.writeheader()
            writer.writerows(rows)

        get_remark_columns()
        return True
    except Exception as e:
        print(f"Error deleting column: {e}")
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

    # Mode 1: Set specific column
    if 'column' in data and 'value' in data:
        column = data.get('column')
        value = data.get('value', '')

        success = update_remark_in_file(row_index, column=column, value=value)

        if success:
            return jsonify({
                "success": True,
                "row_index": row_index,
                "column": column,
                "value": value,
                "file": remarks_file
            })
        else:
            return jsonify({"error": "Failed to update remark"}), 500

    # Mode 2: Comma-separated values (legacy support)
    elif 'remark' in data:
        remark = data.get('remark', '')
        remark_values = [v.strip() for v in remark.split(',') if v.strip()]

        if not remark_values:
            return jsonify({"error": "No remark values provided"}), 400

        success = update_remark_in_file(row_index, remark_values=remark_values)

        if success:
            return jsonify({
                "success": True,
                "row_index": row_index,
                "remark_values": remark_values,
                "file": remarks_file
            })
        else:
            return jsonify({"error": "Failed to update remark"}), 500

    return jsonify({"error": "Invalid request data"}), 400

@app.route("/api/remark-columns", methods=["POST"])
def manage_remark_columns():
    """Add, rename, or delete remark columns"""
    data = request.get_json()
    action = data.get('action')

    if action == 'add':
        column_name = data.get('name')
        if not column_name:
            return jsonify({"error": "Column name required"}), 400

        success = add_remark_column(column_name)
        if success:
            return jsonify({"success": True, "remark_columns": remark_columns})
        else:
            return jsonify({"error": "Column already exists or error occurred"}), 400

    elif action == 'rename':
        old_name = data.get('old_name')
        new_name = data.get('new_name')
        if not old_name or not new_name:
            return jsonify({"error": "Both old_name and new_name required"}), 400

        success = rename_remark_column(old_name, new_name)
        if success:
            return jsonify({"success": True, "remark_columns": remark_columns})
        else:
            return jsonify({"error": "Failed to rename column"}), 400

    elif action == 'delete':
        column_name = data.get('name')
        if not column_name:
            return jsonify({"error": "Column name required"}), 400

        success = delete_remark_column(column_name)
        if success:
            return jsonify({"success": True, "remark_columns": remark_columns})
        else:
            return jsonify({"error": "Failed to delete column"}), 400

    return jsonify({"error": "Invalid action"}), 400

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
    app.run(debug=False, port=5010)
