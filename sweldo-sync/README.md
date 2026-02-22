# SweldoSync MVP (Tauri + React + Python Backend)

This is the "Local-First" Payroll Computation Engine prototype. It leverages a hybrid architecture combining the performance and system integration of Tauri (Rust) with the rapid development and rich ecosystem of Python for backend logic.

## Architecture

-   **Frontend:** React + TypeScript (Vite) for the user interface.
-   **Backend:** Python (FastAPI + SQLModel) for payroll logic, data persistence (SQLite), and API endpoints.
-   **Desktop Wrapper:** Tauri (Rust) for native OS integration and window management.

## Prerequisites

1.  **Node.js & npm** (v16+)
2.  **Rust** (via `rustup`)
3.  **Python** (v3.10+)

## Setup & Installation

### 1. Backend Setup (Python)

Navigate to the backend directory, create a virtual environment, and install dependencies:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend Setup (React + Tauri)

In the root directory, install the Node.js dependencies:

```bash
npm install
```

## How to Run (Development)

You will need two terminal windows running concurrently.

### Terminal 1: Python Backend

Start the FastAPI server:

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
*The backend API will be available at `http://localhost:8000` (Docs: `http://localhost:8000/docs`).*

### Terminal 2: Tauri Application

Launch the desktop application in development mode:

```bash
npm run tauri dev
```
*This will compile the Rust backend and launch the application window, which connects to the running Python server.*

## Project Structure

*   `backend/`: The Python backend service.
    *   `app/core/calculator.py`: **The Core Logic.** Contains the Philippine Labor Code "Night Differential" logic (10 PM - 6 AM) using precise decimal math.
    *   `app/models.py`: Database models (Employees, TimeLogs, etc.).
    *   `app/routers/`: API endpoints.
*   `src-tauri/src/`: The Rust/Tauri native shell.
    *   `calculator.rs`: *Deprecated* (Logic moved to Python backend).
*   `src/`: The React frontend application.

## Key Logic

The core payroll calculation logic (now in Python) iterates minute-by-minute to determine exactly how many minutes fall within the 22:00-06:00 window (Night Differential), ensuring precision even across day boundaries (e.g., shifts from 8 PM to 5 AM).
