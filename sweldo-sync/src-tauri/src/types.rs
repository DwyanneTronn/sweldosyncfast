use serde::{Deserialize, Serialize};
use rust_decimal::Decimal;

#[derive(Debug, Serialize, Deserialize)]
pub struct TimeLog {
    #[serde(alias = "EmployeeID", alias = "employee_id")]
    pub employee_id: String,
    // ISO 8601 strings
    #[serde(alias = "ShiftStart", alias = "shift_start")]
    pub shift_start: String, 
    #[serde(alias = "ShiftEnd", alias = "shift_end")]
    pub shift_end: String,
    #[serde(alias = "DailyRate", alias = "daily_rate")]
    pub daily_rate: Decimal,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ComputationResult {
    pub employee_id: String,
    pub total_hours: Decimal,
    pub regular_hours: Decimal,
    pub night_diff_hours: Decimal,
    pub regular_pay: Decimal,
    pub night_diff_pay: Decimal,
    pub total_pay: Decimal,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct BatchSummary {
    pub processed_count: usize,
    pub total_payroll_cost: Decimal,
    pub errors: Vec<String>,
    pub details: Vec<ComputationResult>,
}
