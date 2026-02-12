# SweldoSync MVP (Tauri + Rust + React)

This is the "Local-First" Payroll Computation Engine prototype.

## Prerequisites

1.  **Node.js & npm**
2.  **Rust** (via `rustup`)

## How to Run

1.  **Install Frontend Dependencies:**
    ```bash
    npm install
    ```

2.  **Run Development Mode:**
    ```bash
    npm run tauri dev
    ```
    This will compile the Rust backend and launch the application window.

## Project Structure

*   `src-tauri/src/calculator.rs`: **The Core Logic.** This contains the Philippine Labor Code "Night Differential" logic (10 PM - 6 AM) using precise decimal math.
*   `src/App.tsx`: The UI to test the logic.

## Key Logic

The core calculation iterates minute-by-minute (for safety in this MVP) to determine exactly how many minutes fall within the 22:00-06:00 window, even across day boundaries (e.g., Shift from 8 PM to 5 AM).
