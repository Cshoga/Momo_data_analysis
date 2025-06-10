# MTN MoMo SMS Data Project

## Overview

This project is about building a fullstack app that can read MTN MoMo SMS messages in XML format, clean and organize the data, store it in a database, and show useful insights on a website dashboard.

wE worked on everything from parsing the data to creating a simple, interactive frontend where users can view and analyze transactions.

---

## What the Project Does

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
| Backend     | Python / Node.js              |
| Database    | SQLite / MySQL / PostgreSQL   |
| Frontend    | HTML, CSS, JavaScript         |
| Charts      | Chart.js (for visualizations) |
| Parsing     | xml.etree.ElementTree / lxml  |
| (Optional) API | Flask / FastAPI / Express  |

---

