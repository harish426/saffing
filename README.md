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
    The server will be available at `http://127.0.0.1:8001`.




### Issues in using google gen AI
1. pip install --upgrade protobuf grpcio-tools langgraph-api for having similar working environment as in the documentation

# Easy Setup Guide: DB URL + Gemini API Key + Run Docker Images

This guide shows:
1) How to get `DATABASE_URL` (Neon)  
2) How to get `GEMINI_API_KEY` (Google AI Studio)  
3) How to run **frontend** + **backend** Docker images on the same Docker network

---

## 1) Create a Database and Get `DATABASE_URL` (Neon)

Most apps expect:

- `DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require`

### Steps (Neon)
1. Sign in to Neon and **create a Project** (this creates a Postgres database).
2. Open your **Project Dashboard**.
3. Click **Connect** (Connection Details).
4. Select:
   - **Branch**
   - **Database**
   - **Role/User**
   - (Optional) **Pooled** vs **Direct**
5. Copy the generated connection string → this is your `DATABASE_URL`.

Example:
```env
DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require"