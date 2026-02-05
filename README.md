# Staffing Solution Project

This repository contains the development code for a Staffing Solution, consisting of a Frontend Web Application and a Backend Processor for mailing and data handling.

## Project Structure

*   **`web-app/`**: A Next.js based web application for the user interface, including Job Entry management and form submissions.
*   **`back_processor/`**: A Python-based backend system handling data processing, mailing automation, and database interactions.

## Work Completed "Up To Now"

### Web Application (`web-app`)
*   **Framework Setup**: Initialized with Next.js.
*   **Job Entry UI**: Enhanced the "Existing Details" page with job entry management features.
*   **Form Submission**: implemented logic for submitting forms on the "Fill In" page.
*   **Configuration**: added `.gitignore` rules to properly ignore `.env` files in all subdirectories.

### Backend Processor (`back_processor`)
*   **Server Setup**: Implemented a FastAPI server (`mailing_system/main.py`).
*   **Database Integration**: Configured connection to Neon Database using SQLAlchemy (`mailing_system/database.py`).
*   **API Endpoints**:
    *   `/`: Health check serving "Python Server is running".
    *   `/db-test`: Endpoint to verify database connectivity.
    *   `/send-remark`, `/check-status`, `/groupby_vendor`, `/groupby_location`, `/get_contact_vendor_details`: Placeholder endpoints for future logic.
*   **Resume Handling**: Basic structure in `resume_handling.py`.

## Getting Started

### 1. Web Application

**Prerequisites:** Node.js installed.

1.  Navigate to the web app directory:
    ```bash
    cd web-app
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```
    The app will be available at `http://localhost:3000`.

### 2. Backend Processor

**Prerequisites:** Python installed.

1.  Navigate to the mailing system directory:
    ```bash
    cd back_processor/mailing_system
    ```
2.  Create and activate a virtual environment (recommended):
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```
3.  Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
4.  Run the server using Uvicorn:
    ```bash
    uvicorn main:app --reload
    ```
    The server will be available at `http://127.0.0.1:8000`.

## Configuration

**Environment Variables**:
Both the `web-app` and `back_processor/mailing_system` require `.env` files for configuration (e.g., Database URLs, API keys). 
For frontend and backend, both combine require .env with Database_URL, and for back end require SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,(can be found in application created in google, use chatGPT to create it, for SMTP_SERVER use smtp.gmail.com, SMTP_PORT use 587, SMTP_USERNAME use your email address, SMTP_PASSWORD use app password from google account) GEMINI_API_KEY(can be found in google ai studio, but if you are using mormal gemini instead of pro, you have to setup payment, and charges for token usage.)


# GEMINI_API_KEY="AIzaSyBkdszygU23v6Guzf5eLwd4JAill-BV20k"
GEMINI_API_KEY="AIzaSyAX9Cfya415gniHG4b49xtHBVlg2p4sYHY"
Ensure these are created based on requirements (not committed to git).

---
*Created: January 13, 2026*


### Issues in using google gen AI
1. pip install --upgrade protobuf grpcio-tools langgraph-api for having similar working environment as in the documentation