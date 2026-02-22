# SweldoSync Project Status Report - MVP V1 (Python Backend Pivot)

## 🚀 Major Architectural Pivot: API-First Modular Engine

**Date:** February 22, 2026
**Status:** MVP - Backend Core Implemented & Tested

### 1. The Core Shift: "Line-Item" Architecture
We have successfully transitioned away from the monolithic, time-log-dependent calculation engine (Rust) to a modular, **API-First Payroll Engine** built with **Python (FastAPI)**.

This aligns strictly with the directive: **"Metering SHOULD be different from billing."**

-   **Old Way (Monolith):** The app ingested raw `TimeIn/TimeOut` logs and calculated tardiness, overtime, and net pay in one go. This was brittle and coupled timekeeping logic with financial logic.
-   **New Way (Modular):**
    1.  **Metering (Input):** External systems (or a future module) process raw time logs and produce "Line Items" (e.g., `Base Pay: 15,000`, `Overtime: 2,500`, `Absences: -500`).
    2.  **Billing (Engine):** Our new Python engine accepts these pre-computed line items and applies statutory deductions (SSS, PhilHealth, Pag-IBIG) and Tax to compute the final Net Pay.

### 2. Tech Stack & Implementation
The new backend is located in `sweldo-sync/backend/` and is built on:

-   **Language:** Python 3.10+
-   **Framework:** FastAPI (High performance, easy to document)
-   **Database:** SQLModel (SQLAlchemy + Pydantic) for ORM
-   **Testing:** Pytest (Unit & Integration tests)

### 3. Key Features Implemented

#### A. Statutory Computations
The engine now correctly computes mandatory Philippine government contributions based on the "Gross Income" derived from the line items.
-   **SSS:** Computed based on compensation brackets (simplified for MVP).
-   **PhilHealth:** Computed as a percentage of the basic salary.
-   **Pag-IBIG (HDMF):** Computed with mandatory employee/employer share caps.
-   **Withholding Tax:** Applied on taxable income after statutory deductions.

#### B. Multi-Tenancy & Security
-   **Tenant Isolation:** Every database record (Employee, Payroll Run) is stamped with a `tenant_id`.
-   **API Key Auth:** All API endpoints are secured via `X-API-Key` header. The system automatically scopes data access to the tenant associated with the provided key.

#### C. Asynchronous Processing
-   **Background Tasks:** Payroll calculation is triggered asynchronously. The API accepts the batch, returns a "Draft" status immediately, and processes the computation in the background to handle large employee volumes without blocking.

### 4. Folder Structure (New Backend)

```
sweldo-sync/backend/
├── app/
│   ├── core/           # Core computation logic (The "Brain")
│   ├── routers/        # API Endpoints (Payroll, Employees)
│   ├── models.py       # Database Schemas (SQLModel)
│   ├── auth.py         # API Key Security & Tenant Context
│   └── main.py         # App Entry Point
├── tests/              # Automated Test Suite
└── requirements.txt    # Python Dependencies
```

### 5. What About Rust? (The "Shell")
The original Rust code in `src-tauri` has been **deprecated** but kept as a "thin shell".
-   `src-tauri/src/calculator.rs`: The old monolithic logic has been removed and replaced with a placeholder error message ("Use Python API").
-   **Why?** This allows the team to continue using Tauri for a desktop application window if desired, without needing to maintain complex Rust logic. All business logic now lives in Python.

### 6. How to Run & Test

**Prerequisites:** Python 3.10+

1.  **Navigate to Backend:**
    ```bash
    cd sweldo-sync/backend
    ```

2.  **Setup Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Run the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    -   API Docs: `http://127.0.0.1:8000/docs`

4.  **Run Tests:**
    ```bash
    pytest tests/test_api_flow.py
    ```
    -   This runs a full end-to-end simulation: Creating a Tenant -> Syncing an Employee -> Ingesting Line Items -> Verifying Net Pay.

### 7. Next Steps
-   [ ] Connect the Frontend (React) to the new Python API.
-   [ ] Implement the actual statutory table lookups (currently using simplified logic).
-   [ ] Deploy the backend to a cloud provider (e.g., Render, AWS, DigitalOcean).
