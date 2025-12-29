import csv
import sys

def load_data(filePath):

    data = []
    header = []

    try:
        with open(filePath, 'r') as file:
            reader = csv.reader(file)
            data = list(reader)
            header = data.pop(0)
        return header, data

    except PermissionError:
        print(f"❌ Error: You don't have permission to read '{filename}'.")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"❌ Error: '{filename}' is not a readable text/CSV file.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
