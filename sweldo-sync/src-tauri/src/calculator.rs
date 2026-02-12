use chrono::{DateTime, Timelike};
use rust_decimal::Decimal;
use rust_decimal::prelude::*;
use rust_decimal_macros::dec;
use crate::types::{TimeLog, ComputationResult, BatchSummary};
use std::fs::File;
use std::io::BufReader;

// Constants for PH Labor Code
const ND_START_HOUR: u32 = 22; // 10 PM
const ND_END_HOUR: u32 = 6;    // 6 AM
const ND_PREMIUM: Decimal = dec!(0.10); // 10% premium

pub fn compute_payroll(log: TimeLog) -> Result<ComputationResult, String> {
    // 1. Parse Input Times
    let start = DateTime::parse_from_rfc3339(&log.shift_start)
        .map_err(|_| "Invalid start time format")?;
    let end = DateTime::parse_from_rfc3339(&log.shift_end)
        .map_err(|_| "Invalid end time format")?;

    if end <= start {
        return Err("End time must be after start time".to_string());
    }

    // 2. Calculate Total Duration
    let duration = end.signed_duration_since(start);
    let total_minutes = duration.num_minutes();
    let total_hours = Decimal::from_i64(total_minutes).unwrap() / dec!(60.0);

    // 3. Calculate Night Differential Hours
    // We iterate minute by minute for absolute safety in this MVP. 
    // Optimized range overlap logic would be used for production performance, 
    // but iteration guarantees "Chemical Testing" correctness for complex cross-day shifts.
    let mut nd_minutes = 0;
    let mut current = start;
    
    // Iterate through every minute of the shift
    while current < end {
        let h = current.hour();
        // Check if current minute falls within 22:00 - 06:00
        // Cases: 
        // 22, 23 (Late night)
        // 0, 1, 2, 3, 4, 5 (Early morning)
        if h >= ND_START_HOUR || h < ND_END_HOUR {
            nd_minutes += 1;
        }
        current = current + chrono::Duration::minutes(1);
    }

    let nd_hours = Decimal::from_i64(nd_minutes).unwrap() / dec!(60.0);
    let regular_hours = total_hours - nd_hours;

    // 4. Financial Calculation (using Fixed Point Math)
    let hourly_rate = log.daily_rate / dec!(8.0); // Assuming 8 hour work day divisor
    
    let regular_pay = regular_hours * hourly_rate;
    let nd_pay_base = nd_hours * hourly_rate;
    let nd_premium_amt = nd_pay_base * ND_PREMIUM;
    let total_nd_pay = nd_pay_base + nd_premium_amt; // ND Hours are paid at 110% total (or Base + 10%)

    // Note: Usually "Regular Pay" includes the base of the ND hours, and "ND Pay" is just the premium.
    // However, for audit clarity, we often separate:
    // - Basic Pay for Total Hours
    // - ND Differential Amount (the extra 10%)
    // Let's stick to the struct:
    // regular_pay: Pay for non-ND hours? Or Base pay?
    // Let's define: 
    // Regular Pay = (Regular Hours * Rate)
    // ND Pay = (ND Hours * Rate * 1.10)
    
    let total_pay = regular_pay + total_nd_pay;

    Ok(ComputationResult {
        employee_id: log.employee_id,
        total_hours: total_hours.round_dp(2),
        regular_hours: regular_hours.round_dp(2),
        night_diff_hours: nd_hours.round_dp(2),
        regular_pay: regular_pay.round_dp(2),
        night_diff_pay: total_nd_pay.round_dp(2),
        total_pay: total_pay.round_dp(2),
    })
}

pub fn process_csv_file(file_path: String) -> Result<BatchSummary, String> {
    let file = File::open(file_path).map_err(|e| format!("Failed to open file: {}", e))?;
    let mut rdr = csv::Reader::from_reader(BufReader::new(file));
    
    let mut results = Vec::new();
    let mut errors = Vec::new();
    let mut total_cost = Decimal::ZERO;

    for result in rdr.deserialize() {
        let record: TimeLog = match result {
            Ok(rec) => rec,
            Err(e) => {
                errors.push(format!("Row parse error: {}", e));
                continue;
            }
        };

        match compute_payroll(record) {
            Ok(comp) => {
                total_cost += comp.total_pay;
                results.push(comp);
            },
            Err(e) => errors.push(format!("Calculation error: {}", e)),
        }
    }

    Ok(BatchSummary {
        processed_count: results.len(),
        total_payroll_cost: total_cost.round_dp(2),
        errors,
        details: results,
    })
}
