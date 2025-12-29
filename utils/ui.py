import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import sys

def get_files():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilenames(
        title="Select the csv with you wanted as HTML",
        filetypes=[("CSV Files", "*.csv"), ],
    )

def UI_runner():

    files = get_files()

    if not files:
        messagebox.showerror("Fail", "files are not given")
        sys.exit(1)

    if files.__len__() > 1:
        messagebox.showerror("Fail", "Please select only one file at a time")
        sys.exit(2)

    return files[0]
