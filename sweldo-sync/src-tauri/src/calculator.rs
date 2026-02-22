use crate::types::{TimeLog, ComputationResult, BatchSummary};

// OBSOLETE: This file previously contained monolithic logic for computing payroll from raw time logs.
// The new architecture uses the Python-based API engine (Line-Item Architecture).
// This file is kept as a placeholder if local Rust-based pre-processing is needed in the future.

pub fn compute_payroll(_log: TimeLog) -> Result<ComputationResult, String> {
    Err("This function is deprecated. Please use the Python API engine.".to_string())
}

pub fn process_csv_file(_file_path: String) -> Result<BatchSummary, String> {
    Err("This function is deprecated. Please use the Python API engine.".to_string())
}
