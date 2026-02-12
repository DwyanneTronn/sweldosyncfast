#![cfg_attr(
  all(not(debug_assertions), target_os = "windows"),
  windows_subsystem = "windows"
)]

mod types;
mod calculator;

use tauri::command;
use types::{TimeLog, ComputationResult, BatchSummary};
use calculator::{compute_payroll, process_csv_file};

#[command]
fn process_shift(log: TimeLog) -> Result<ComputationResult, String> {
  compute_payroll(log)
}

#[command]
fn process_csv(file_path: String) -> Result<BatchSummary, String> {
  process_csv_file(file_path)
}

fn main() {
  tauri::Builder::default()
    .invoke_handler(tauri::generate_handler![process_shift, process_csv])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}
