# MTN MoMo SMS Data Project

## Overview

This project is designed to creqate a fullstatck applicationthat  that reads MTN MoMo SMS messages in XML format, cleans and organizes the data, stores it in a database, and later displays these information on a website dashboard as prompted by the user.

We worked on parsing the data, created a simple, interactive frontend where users can view and analyze information on the transactions made via MTN MOMO.

---

## What the Project Does

The application works in a sequence that;

- Reads and parses SMS data from an XML file
- Cleans and fixes the data (e.g., amounts, dates)
- Sorts messages into categories like:
  - Incoming Money
  - Payments to people or services
  - Transfers and withdrawals
  - Airtime and bundles
  - Utility payments (like cash power)
- Stores clean data in a database (SQLite/MySQL/PostgreSQL)
- Shows data using a web dashboard (charts, search, filter, etc.)

---

## Tools we Used

| Area        | Tools/Technologies            |
|-------------|-------------------------------|
| Backend     | Python                        |
| Database    | SQLite                        |
| Frontend    | HTML, CSS, JavaScript         |
| Charts      | Chart.js (for visualizations) |
| Parsing     | xml.etree.ElementTree / lxml  |

---

## Setup Instructions

### Prerequisites
- Python 3.x
- Node.js (for serving the frontend)
- SQLite3 (included with Python)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install flask flask-cors
   ```

3. Initialize the database:
   ```bash
   sqlite3 momo.db < schema.sql
   ```

4. Start the backend server:
   ```bash
   python app.py
   ```
   The backend will run on `http://localhost:5000`

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Serve the frontend using a local server. You can use Python's built-in server:
   ```bash
   python -m http.server 8000
   ```
   Or use Node.js's `http-server`:
   ```bash
   npx http-server
   ```

3. Open your browser and visit:
   - If using Python server: `http://localhost:8000`
   - If using http-server: `http://localhost:8080`

### Data Import
The project comes with a sample database (`momo.db`). If you want to import your own data:
1. Place your XML file in the backend directory
2. Run the parser:
   ```bash
   python parser.py
   ```

### Troubleshooting
- If you get CORS errors, ensure the backend is running and CORS is properly configured
- If the database is empty, check if the schema was properly initialized
- Make sure both frontend and backend servers are running simultaneously
