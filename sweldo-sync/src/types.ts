export interface TimeLog {
  employee_id: string;
  shift_start: string; // ISO 8601
  shift_end: string;
  daily_rate: number;
}

export interface ComputationResult {
  employee_id: string;
  total_hours: number;
  regular_hours: number;
  night_diff_hours: number;
  regular_pay: number;
  night_diff_pay: number;
  total_pay: number;
}

export interface BatchSummary {
  processed_count: number;
  total_payroll_cost: number;
  errors: string[];
  details: ComputationResult[];
}
