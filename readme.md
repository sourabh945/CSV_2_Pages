```markdown
# CSV Viewer - Complete Documentation

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [API Reference](#api-reference)
5. [Frontend Structure](#frontend-structure)
6. [Configuration](#configuration)
7. [Scripting Guide](#scripting-guide)
8. [Storage & Persistence](#storage--persistence)
9. [Customization](#customization)
10. [Examples](#examples)
11. [Troubleshooting](#troubleshooting)

---

## Overview

CSV Viewer is a Flask-based web application for viewing, filtering, and annotating CSV data. It provides:

- **Table View**: Traditional spreadsheet-like view with filtering and search
- **Card View**: Individual record view with navigation
- **Remarks System**: Add annotations/notes to records
- **Custom Scripts**: Automate tasks with JavaScript
- **Analytics**: Run analysis scripts on data

---

## Architecture

### File Structure

```
project/
├── app.py                 # Flask backend
├── templates/
│   └── index.html         # Frontend (HTML/CSS/JS)
├── utils/
│   ├── ui.py              # UI runner (file selection)
│   └── fileprocessor.py   # CSV loading utilities
└── data/
    ├── yourfile.csv       # Original CSV
    └── yourfile_with_remarks.csv  # CSV with remarks
```

### Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  CSV File   │────▶│   Flask     │────▶│  Frontend   │
│             │     │   Backend   │     │  (Browser)  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  Remarks    │
                    │  CSV File   │
                    └─────────────┘
```

---

## Installation & Setup

### Requirements

```bash
pip install flask
```

### Project Files

**utils/ui.py** (example):
```python
def UI_runner():
    """Return path to CSV file"""
    return "path/to/your/file.csv"
```

**utils/fileprocessor.py** (example):
```python
import csv

def load_data(filepath):
    """Load CSV and return headers and data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = list(reader)
    return headers, data
```

### Running

```bash
python app.py
```

Access at: `http://localhost:5001`

---

## API Reference

### GET /api/headers

Returns CSV headers and remark columns.

**Response:**
```json
{
    "headers": ["Name", "Email", "City"],
    "remark_columns": ["Remark_1", "Status", "Notes"]
}
```

---

### GET /api/data

Returns filtered data with remarks.

**Query Parameters:**

| Parameter | Type   | Description                    |
|-----------|--------|--------------------------------|
| column    | string | Column name to filter by       |
| value     | string | Value to match in column       |
| search    | string | Search term (searches all columns) |

**Example:**
```
GET /api/data?column=City&value=New York&search=john
```

**Response:**
```json
{
    "data": [
        {
            "Name": "John Doe",
            "Email": "john@example.com",
            "City": "New York",
            "Remark_1": "Called on 2024-01-15",
            "_index": 0
        }
    ],
    "total": 1,
    "remark_columns": ["Remark_1", "Status"]
}
```

**Note:** `_index` is the original row index in the CSV file.

---

### GET /api/filter-options

Returns unique values for each column (for filter dropdowns).

**Response:**
```json
{
    "Name": ["Alice", "Bob", "Charlie"],
    "City": ["Boston", "New York", "Seattle"],
    "Status": ["Active", "Inactive"]
}
```

---

### POST /api/remarks/{row_index}

Add or update remarks for a specific row.

**URL Parameters:**

| Parameter  | Type | Description           |
|------------|------|-----------------------|
| row_index  | int  | Row index in CSV      |

**Request Body (Mode 1 - Set specific column):**
```json
{
    "column": "Status",
    "value": "Contacted on 2024-01-15"
}
```

**Request Body (Mode 2 - Comma-separated values):**
```json
{
    "remark": "value1, value2, value3"
}
```

This creates `Remark_1`, `Remark_2`, `Remark_3` columns.

**Response:**
```json
{
    "success": true,
    "row_index": 0,
    "column": "Status",
    "value": "Contacted on 2024-01-15",
    "file": "data/file_with_remarks.csv"
}
```

---

### POST /api/remark-columns

Manage remark columns (add, rename, delete).

**Add Column:**
```json
{
    "action": "add",
    "name": "NewColumn"
}
```

**Rename Column:**
```json
{
    "action": "rename",
    "old_name": "OldName",
    "new_name": "NewName"
}
```

**Delete Column:**
```json
{
    "action": "delete",
    "name": "ColumnToDelete"
}
```

**Response:**
```json
{
    "success": true,
    "remark_columns": ["Remark_1", "Status", "NewColumn"]
}
```

---

## Frontend Structure

### Global State Variables

```javascript
let filteredData = [];        // Current filtered data
let headers = [];             // CSV column headers
let remarkColumns = [];       // Remark column names
let filterOptions = {};       // Unique values per column
let currentView = "table";    // "table" or "card"
let currentCardIndex = -1;    // Current card index
let sidebarVisible = true;    // Sidebar state
let visibleCardFields = {};   // Card field visibility
let visibleTableCols = {};    // Table column visibility
let sidebarDisplayCol = "";   // Column shown in sidebar
let cardScripts = [];         // Card action scripts
let tableScripts = [];        // Table analytics scripts
let analyticsResults = {};    // Script output storage
let pendingWindows = [];      // Blocked popup URLs
```

### Core Functions

#### Data Loading

```javascript
// Load headers from backend
async function loadHeaders()

// Load filter dropdown options
async function loadFilterOptions()

// Load data with current filters
async function loadData()
```

#### View Rendering

```javascript
// Render table view
function renderTable()

// Render card navigation sidebar
function renderCardNav()

// Show specific card
function showCard(idx)

// Navigate cards
function navCard(direction)  // direction: -1 or 1
```

#### View Switching

```javascript
// Switch between table and card view
function switchView(view)  // view: "table" or "card"

// Open card from table
function openCard(idx)

// Close card view
function closeCard()
```

#### Filtering

```javascript
// Apply current filters
function applyFilters()

// Clear all filters
function clearFilters()
```

#### Remarks

```javascript
// Open remarks edit modal
function openRemarksModal()

// Save all remarks
async function saveAllRemarks()

// Quick add single remark
async function quickAddRemark()

// Insert date into remark input
function insertDate(type)  // type: "today", "now", "time"
```

#### Remark Columns

```javascript
// Add new remark column
async function addRemarkColumn()

// Rename remark column
async function renameRemarkColumn(oldName)

// Delete remark column
async function deleteRemarkColumn(name)
```

#### Configuration

```javascript
// Open table config modal
function openTableConfig()

// Save table config
function saveTableConfig()

// Open card config modal
function openCardConfig()

// Save card config
function saveCardConfig()
```

#### Scripts

```javascript
// Open script editor
function openScriptEditor(type, idx)  // type: "card" or "table"

// Save script
function saveScript()

// Run card script
function runCardScript(idx)

// Run table script
function runTableScript(idx)
```

---

## Configuration

### Table Configuration

Access via **TABLE CONFIG** button in controls.

| Option | Description |
|--------|-------------|
| Visible Columns | Show/hide columns in table view |
| Table Scripts | Analytics scripts for data analysis |

### Card Configuration

Access via **CONFIG** button in card view.

| Option | Description |
|--------|-------------|
| Sidebar Display Column | Which column to show in navigation |
| Visible Fields | Show/hide fields in card view |
| Remark Columns | Add, rename, delete remark columns |
| Card Scripts | Action scripts for card operations |

---

## Scripting Guide

### Card Scripts

Card scripts run in the context of the current card/record.

#### Available Variables

| Variable | Type | Description |
|----------|------|-------------|
| `data` | object | Current card data |
| `index` | number | Current card index |
| `headers` | array | Column headers |
| `remarkColumns` | array | Remark column names |

#### Available Functions

##### Data Access

```javascript
// Get field value from current card
getValue(fieldName)
// Example: getValue('Email')  // Returns "john@example.com"
```

##### Remarks

```javascript
// Set remark value (replaces existing)
await setRemark(columnName, value)
// Example: await setRemark('Status', 'Completed')

// Add to existing remark (appends with comma)
await addToRemark(columnName, value)
// Example: await addToRemark('Notes', 'Called today')
```

##### Date/Time

```javascript
// Get today's date (YYYY-MM-DD)
dateToday()
// Returns: "2024-01-15"

// Get current datetime (YYYY-MM-DD HH:MM:SS)
dateNow()
// Returns: "2024-01-15 14:30:45"

// Get current time (HH:MM:SS)
timeNow()
// Returns: "14:30:45"
```

##### Windows/URLs

```javascript
// Open URL in new tab
openWindow(url)
// Example: openWindow('https://google.com')

// Open multiple URLs
openWindows([url1, url2, url3])
// Example: openWindows([
//     'https://google.com/search?q=term1',
//     'https://google.com/search?q=term2'
// ])

// Generate Google search URL
googleSearch(query)
// Returns: "https://google.com/search?q=encoded+query"
```

##### Clipboard & Messages

```javascript
// Copy text to clipboard
copyToClipboard(text)
// Example: copyToClipboard(getValue('Email'))

// Show success message
showAlert(message)
// Example: showAlert('Done!')
```

#### Card Script Examples

**Example 1: Google Search**
```javascript
const name = getValue('Name');
openWindow(googleSearch(name));
```

**Example 2: Multi-Search with Remark**
```javascript
const keyword = getValue('Keyword');
const city = getValue('City');
const specialty = getValue('Specialty');

// Copy keyword to clipboard
copyToClipboard(keyword);

// Open multiple searches
openWindows([
    googleSearch('dr ' + keyword),
    googleSearch('dr ' + keyword + ' ' + specialty + ' ' + city),
    googleSearch('dr ' + keyword + ' ' + specialty + ' ' + city + ' reviews')
]);

// Add remark with date
addToRemark('Searched', dateToday());
```

**Example 3: Quick Status Update**
```javascript
setRemark('Status', 'Contacted on ' + dateNow());
showAlert('Status updated!');
```

**Example 4: Copy Multiple Fields**
```javascript
const info = `Name: ${getValue('Name')}
Email: ${getValue('Email')}
Phone: ${getValue('Phone')}`;

copyToClipboard(info);
showAlert('Contact info copied!');
```

**Example 5: Conditional Logic**
```javascript
const email = getValue('Email');
if (email) {
    openWindow('mailto:' + email);
    addToRemark('Emailed', dateToday());
} else {
    showAlert('No email address!');
}
```

---

### Table Scripts

Table scripts run on the entire filtered dataset.

#### Available Variables

| Variable | Type | Description |
|----------|------|-------------|
| `headers` | array | Column headers |
| `remarkColumns` | array | Remark column names |

#### Available Functions

##### Data Access

```javascript
// Get all filtered data
getAllData()
// Returns: [{...}, {...}, ...]

// Get all values of a column
getColumn(fieldName)
// Returns: ["value1", "value2", ...]
```

##### Counting

```javascript
// Count total rows
count()
// Returns: 150

// Count rows where field equals value
countWhere(fieldName, value)
// Example: countWhere('City', 'New York')  // Returns: 25
```

##### Math

```javascript
// Sum numeric column
sum(fieldName)
// Example: sum('Amount')  // Returns: 15000

// Average of numeric column
average(fieldName)
// Example: average('Age')  // Returns: 35.5
```

##### Grouping & Unique

```javascript
// Get unique values
unique(fieldName)
// Example: unique('City')  // Returns: ["Boston", "New York", "Seattle"]

// Group by field and count
groupBy(fieldName)
// Returns: { "New York": 25, "Boston": 18, "Seattle": 12 }
```

##### Filtering

```javascript
// Filter data by field value
filterData(fieldName, value)
// Returns: [{...}, {...}]  // Matching rows only
```

##### Output

```javascript
// Display result in analytics panel
showResult(label, value)
// Example: showResult('Total Records', 150)

// Clear all results
clearResults()
```

##### Export

```javascript
// Export data to CSV file
exportCSV(data, filename)
// Example: exportCSV(getAllData(), 'export.csv')
// Example: exportCSV(filterData('Status', 'Active'), 'active.csv')
```

##### Utilities

```javascript
// Date functions (same as card scripts)
dateToday()
dateNow()

// Show message
showAlert(message)

// Copy to clipboard
copyToClipboard(text)
```

#### Table Script Examples

**Example 1: Basic Statistics**
```javascript
clearResults();
showResult('Total Records', count());
showResult('Unique Cities', unique('City').length);
showResult('Average Age', average('Age').toFixed(1));
```

**Example 2: Group Analysis**
```javascript
clearResults();
showResult('By City', groupBy('City'));
showResult('By Status', groupBy('Status'));
showResult('By Category', groupBy('Category'));
```

**Example 3: Filtered Export**
```javascript
const active = filterData('Status', 'Active');
showResult('Active Count', active.length);

if (active.length > 0) {
    exportCSV(active, 'active_records_' + dateToday() + '.csv');
}
```

**Example 4: Summary Report**
```javascript
clearResults();

const total = count();
const cities = unique('City');
const statuses = groupBy('Status');

showResult('Total', total);
showResult('Cities', cities.join(', '));
showResult('Active', statuses['Active'] || 0);
showResult('Inactive', statuses['Inactive'] || 0);
showResult('Completion Rate', 
    ((statuses['Completed'] || 0) / total * 100).toFixed(1) + '%'
);
```

**Example 5: Find Duplicates**
```javascript
clearResults();

const emails = getColumn('Email');
const seen = {};
const duplicates = [];

emails.forEach(email => {
    if (seen[email]) duplicates.push(email);
    else seen[email] = true;
});

showResult('Total Emails', emails.length);
showResult('Unique Emails', Object.keys(seen).length);
showResult('Duplicates', duplicates.length);

if (duplicates.length > 0) {
    showResult('Duplicate List', duplicates.join(', '));
}
```

**Example 6: Date-based Analysis**
```javascript
clearResults();

const today = dateToday();
const searchedToday = getAllData().filter(row => 
    (row['Searched'] || '').includes(today)
);

showResult('Searched Today', searchedToday.length);
showResult('Remaining', count() - searchedToday.length);

// Export remaining
const remaining = getAllData().filter(row => 
    !(row['Searched'] || '').includes(today)
);
if (remaining.length > 0) {
    exportCSV(remaining, 'remaining_' + today + '.csv');
}
```

---

## Storage & Persistence

### Local Storage Keys

All settings are stored in browser's localStorage with file-specific keys.

| Key Pattern | Description |
|-------------|-------------|
| `cardFields_{hash}` | Card field visibility settings |
| `tableCols_{hash}` | Table column visibility settings |
| `sidebarCol_{hash}` | Sidebar display column |
| `cardScripts_{hash}` | Card scripts array |
| `tableScripts_{hash}` | Table scripts array |
| `sidebar_{hash}` | Sidebar visibility state |
| `lastVisited_{hash}` | Last visited card index |

`{hash}` is generated from the URL pathname to keep settings per-file.

### Storage Functions

```javascript
// Save to localStorage
save(key, value)
// Example: save('cardFields', { Name: true, Email: false })

// Load from localStorage
load(key, defaultValue)
// Example: load('cardFields', {})
```

### Remarks Storage

Remarks are stored in a separate CSV file:
- Original: `data/yourfile.csv`
- With remarks: `data/yourfile_with_remarks.csv`

---

## Customization

### Adding New Date Formats

```javascript
// In frontend, add to quick buttons
function formatCustomDate() {
    const d = new Date();
    return d.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}
// Returns: "Monday, January 15, 2024"
```

### Custom Script Functions

Add new helper functions for scripts:

```javascript
// Add to frontend script section

// LinkedIn search
const linkedInSearch = (query) => 
    'https://linkedin.com/search/results/all/?keywords=' + 
    encodeURIComponent(query);

// Twitter search
const twitterSearch = (query) => 
    'https://twitter.com/search?q=' + encodeURIComponent(query);

// Custom API call
const fetchAPI = async (url) => {
    const res = await fetch(url);
    return await res.json();
};
```

Then include in script execution:

```javascript
function runCardScript(idx) {
    const s = cardScripts[idx];
    try {
        new Function(
            'getValue', 'setRemark', 'addToRemark', 
            'openWindow', 'openWindows', 'googleSearch',
            'linkedInSearch', 'twitterSearch',  // Add new functions
            'showAlert', 'copyToClipboard',
            'dateToday', 'dateNow', 'timeNow',
            'headers', 'remarkColumns', 'data', 'index',
            s.code
        )(
            getValue, setRemark, addToRemark,
            openWindow, openWindows, googleSearch,
            linkedInSearch, twitterSearch,  // Pass new functions
            showAlert, copyToClipboard,
            dateToday, dateNow, timeNow,
            headers, remarkColumns, 
            filteredData[currentCardIndex], currentCardIndex
        );
    } catch (e) { 
        showMessage("Script error: " + e.message, "error"); 
    }
}
```

### Styling Customization

Key CSS variables to customize:

```css
/* Primary color */
--primary: #1e40af;
--primary-light: #dbeafe;
--primary-dark: #1e3a8a;

/* Accent colors */
--success: #059669;
--warning: #f59e0b;
--error: #dc2626;
--purple: #7c3aed;

/* Border radius */
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 20px;
```

---

## Examples

### Complete Workflow: Doctor Search

**Scenario:** Search for doctors and track progress.

**1. Create Remark Columns:**
- Go to Card Config
- Add columns: `Searched`, `Status`, `Notes`

**2. Create Card Script - "Search All":**
```javascript
const name = getValue('Name');
const specialty = getValue('Specialty');
const city = getValue('City');

// Copy name
copyToClipboard(name);

// Build queries
const q1 = 'dr ' + name;
const q2 = q1 + ' ' + specialty;
const q3 = q2 + ' ' + city;

// Open searches
openWindows([
    googleSearch(q1),
    googleSearch(q2),
    googleSearch(q3)
]);

// Mark as searched
addToRemark('Searched', dateToday());
showAlert('Searches opened!');
```

**3. Create Card Script - "Mark Complete":**
```javascript
setRemark('Status', 'Completed - ' + dateNow());
showAlert('Marked complete!');
```

**4. Create Table Script - "Daily Summary":**
```javascript
clearResults();

const today = dateToday();
const all = getAllData();

const searchedToday = all.filter(r => 
    (r['Searched'] || '').includes(today)
).length;

const completed = all.filter(r => 
    (r['Status'] || '').includes('Completed')
).length;

showResult('Total Records', count());
showResult('Searched Today', searchedToday);
showResult('Completed', completed);
showResult('Remaining', count() - completed);
```

**5. Create Table Script - "Export Pending":**
```javascript
const pending = getAllData().filter(r => 
    !r['Status'] || !r['Status'].includes('Completed')
);

showResult('Pending Count', pending.length);
exportCSV(pending, 'pending_' + dateToday() + '.csv');
```

---

### Complete Workflow: Contact Management

**1. Remark Columns:**
- `Last Contact`
- `Next Action`
- `Priority`

**2. Card Script - "Log Call":**
```javascript
const name = getValue('Name');
addToRemark('Last Contact', 'Called ' + dateNow());
setRemark('Next Action', 'Follow up in 1 week');
showAlert('Call logged for ' + name);
```

**3. Card Script - "Send Email":**
```javascript
const email = getValue('Email');
const name = getValue('Name');

if (email) {
    openWindow('mailto:' + email + '?subject=Follow%20Up');
    addToRemark('Last Contact', 'Emailed ' + dateNow());
} else {
    showAlert('No email for ' + name);
}
```

**4. Table Script - "Priority Report":**
```javascript
clearResults();
const priorities = groupBy('Priority');
showResult('High Priority', priorities['High'] || 0);
showResult('Medium Priority', priorities['Medium'] || 0);
showResult('Low Priority', priorities['Low'] || 0);
```

---

## Troubleshooting

### Common Issues

**1. Popups Blocked**
- Browser blocks multiple `window.open()` calls
- Solution: Click individual buttons in popup modal, or allow popups for site

**2. Remarks Not Saving**
- Check Flask console for errors
- Verify file permissions on remarks CSV
- Check `_index` is present in data

**3. Scripts Not Running**
- Check browser console for JavaScript errors
- Verify function names are correct
- Use `try/catch` in scripts for debugging

**4. Data Not Loading**
- Check Flask server is running
- Verify CSV file path is correct
- Check for encoding issues (use UTF-8)

### Debugging Scripts

Add console logging to scripts:

```javascript
console.log('Data:', data);
console.log('Value:', getValue('FieldName'));

try {
    // Your code here
} catch (e) {
    console.error('Error:', e);
    showAlert('Error: ' + e.message);
}
```

### Reset All Settings

Clear localStorage for this file:

```javascript
// In browser console
const hash = /* your file hash */;
Object.keys(localStorage)
    .filter(k => k.includes(hash))
    .forEach(k => localStorage.removeItem(k));
location.reload();
```

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Escape` | Close modal / Exit card view |
| `Left Arrow` | Previous card (in card view) |
| `Right Arrow` | Next card (in card view) |
| `Enter` | Apply search filter (when in search input) |

---

## Version History

| Version | Changes |
|---------|---------|
| 1.0 | Initial release |
| 1.1 | Added card scripts |
| 1.2 | Added table scripts and analytics |
| 1.3 | Added remark column management |
| 1.4 | Separated table/card configurations |
| 1.5 | Added remarks edit modal |

---

## License

MIT License - Free to use and modify.
```

This documentation file covers:

1. **Complete API reference** with request/response examples
2. **All frontend functions** with descriptions
3. **Detailed scripting guide** with examples for both card and table scripts
4. **All available helper functions** with usage examples
5. **Configuration options** explained
6. **Storage/persistence** mechanism
7. **Customization guide** for extending functionality
8. **Complete workflow examples** for real-world use cases
9. **Troubleshooting** section for common issues
10. **Keyboard shortcuts** reference
