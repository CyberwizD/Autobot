# 🤖 Autobot

Autobot is a workflow automation system designed to streamline personal and business data tasks using the **Gemini API** and **Streamlit** for caching and visualization. It allows users to upload files (Excel/CSV), process them into dataframes, and generate meaningful reports such as daily, weekly, monthly, or overall summaries.

---

## 📌 Features

- **Personal Mode**
  - Chat-like interface for simple workflow automation.
  - Natural queries with Gemini API integration.

- **Business Mode**
  - Upload **Excel/CSV** files for automated report generation.
  - Data summarization:
    - Sum of columns
    - Totals per day, week, month
    - User activity summaries
  - Cached results for faster response and consistency.

- **Reports Dashboard**
  - Every downloaded Excel/CSV file is stored in the Reports section.
  - Dataframes can be viewed interactively using `st.dataframe`.

---

## ⚙️ System Design Overview

### 1. **Frontend (Autobot Dashboard)**
- Two main modes:
  - **Personal Mode** → Text-based queries handled via Gemini API.
  - **Business Mode** → File upload system for Excel/CSV processing.
- All uploaded/downloaded files are tracked in the **Reports** subpage.

### 2. **Gemini API Server**
- Handles requests from Autobot.
- Generates dataframes and processes calculations:
  - Column summation
  - Daily, weekly, and monthly totals
  - Summary reports of all users
- Sends processed data back to Autobot.

### 3. **Streamlit Cache**
- Stores schema and dataframe structures of reports.
- Ensures faster response by comparing requested outputs with cached data.
- If a new request matches an existing cached schema, the result is served directly.

---

## 🛠️ How It Works (Behind the Scenes)

1. **Upload & Conversion**
   - Uploaded Excel/CSV files are converted into dataframes.
   - Files are viewable using `st.dataframe(df)` before processing.

2. **Data Processing**
   - When a user clicks the ➡️ button:
     - A Python function formats, adds, and structures the dataframe.
     - A request is sent to Gemini API with the dataframe and a prompt.
     - Gemini API performs summations and calculations.

3. **Response Handling**
   - Results are compared with Streamlit Cache.
   - If results are similar, cache returns the dataframe.
   - If not, Gemini API iterates until correct, then sends response.

4. **Report Viewing**
   - Generated dataframes can be zoomed and interacted with, similar to using `st.dataframe(data)`.
   - Reports are saved and accessible in the **Reports** dashboard.

---

## 🚀 Use Cases

- Automating repetitive **Excel/CSV** report tasks.  
- Quickly generating summaries from structured datasets.  
- Switching seamlessly between **personal chat automation** and **business reporting**.  
- Efficient caching for reducing redundant computations.  

---

## 📂 Reports

- Every generated **Excel/CSV** is stored in the **Reports** section.  
- Dataframes can be **re-opened and zoomed in** for deeper inspection.  
- Reports are **versioned per upload and request**.  

---

## 📌 Summary

Autobot combines the power of:  

- **Gemini API** → For intelligent dataframe processing.  
- **Streamlit Cache** → For efficient caching and schema management.  
- **Interactive Dashboard** → For switching between personal and business modes, uploading files, and viewing reports.  

This makes **Autobot** a **flexible, scalable, and efficient automation assistant** for both individuals and businesses.  
