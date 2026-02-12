# SweldoSync - Project Status & Roadmap
**Date:** February 12, 2026
**Version:** MVP Phase 1 (Prototype)

## 1. Project Overview
**SweldoSync** is a "Local-First" Payroll Computation Engine designed for the Philippine BPO market. It addresses the need for accurate, offline, and secure payroll audits that handle complex "layered" labor laws (Night Differential, Holidays, Rest Days) without data leaving the client's intranet.

## 2. Technical Architecture
*   **Core Engine:** Rust (`sweldo-sync/src-tauri`)
    *   Uses `rust_decimal` for precise fixed-point financial math.
    *   Uses `chrono` for robust datetime handling.
    *   Uses `csv` crate for high-performance batch processing.
*   **Frontend UI:** React + TypeScript (`sweldo-sync/src`)
    *   Communicates with Rust via Tauri IPC bridge.
    *   Accepts CSV files and displays audit summaries.
*   **Distribution:** Tauri
    *   Compiles to a lightweight native binary (MacOS/Windows).
    *   Offline-capable by default.

## 3. Current Implementation Status
- [x] **Project Scaffolding:** Tauri + React + TypeScript set up.
- [x] **Core Logic (Rust):**
    - [x] Minute-level iteration for accuracy.
    - [x] Night Differential calculation (10 PM - 6 AM).
    - [x] Shift duration & Regular pay calculation.
- [x] **Batch Processing:**
    - [x] CSV file ingestion.
    - [x] Mass calculation loop.
    - [x] Error handling (skips bad rows, reports errors).
    - [x] Audit Report generation (Total Cost + Breakdown).
- [x] **UI/UX:**
    - [x] File Picker integration.
    - [x] "Browse & Compute" workflow.
    - [x] Results Dashboard.

## 4. Immediate Next Steps (Roadmap)
1.  **Holiday & Rest Day Logic:**
    *   Extend `calculator.rs` to accept a list of "Holiday Dates".
    *   Implement "Rest Day" logic (requires employee schedule context).
2.  **Configuration UI:**
    *   Allow users to set custom "Daily Rates" or "Shift Schedules" in the UI (currently hardcoded or purely CSV-driven).
3.  **Export Feature:**
    *   Add a button to export the `ComputationResult` back to a clean CSV/Excel file for the user to download.
4.  **Licensing:**
    *   Implement `machine-uid` check for the offline activation mechanism.

## 5. How to Resume Work
1.  **Navigate to project:** `cd sweldo-sync`
2.  **Run Dev Server:** `npm run tauri dev`
3.  **Test File:** Use `timesheets_sample.csv` in the root folder.
