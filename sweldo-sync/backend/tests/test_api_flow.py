from unittest.mock import patch
from app.routers.payroll import process_batch as real_process_batch

def test_full_payroll_flow(client, api_key, session):
    headers = {"X-API-Key": api_key}

    # 1. Sync Employee
    employee_payload = {
        "external_id": "EMP001",
        "first_name": "Juan",
        "last_name": "Dela Cruz",
        "daily_rate": 1000.0,
        "monthly_rate": 22000.0,
        "email": "juan@test.com",
        "tenant_id": 1
    }
    response = client.post("/api/employees/", json=employee_payload, headers=headers)
    assert response.status_code == 200
    
    # 2. Ingest Line Items
    payload = {
        "period_start": "2023-11-01",
        "period_end": "2023-11-15",
        "payout_date": "2023-11-15",
        "employees": [
            {
                "external_employee_id": "EMP001",
                "items": [
                    {"description": "Basic Pay", "amount": 11000.0, "category": "basic"},
                    {"description": "Overtime", "amount": 2500.0, "category": "overtime"},
                    {"description": "Late Deduction", "amount": 500.0, "category": "deduction"}
                ]
            }
        ]
    }
    
    # Patch process_batch to prevent it from running automatically (and failing on DB mismatch)
    with patch("app.routers.payroll.process_batch") as mock_task:
        response = client.post("/api/payroll/batch/ingest", json=payload, headers=headers)
        assert response.status_code == 200
        run_data = response.json()
        run_id = run_data["id"]
        
        # Verify background task was scheduled
        mock_task.assert_called()
    
    # 3. Manually Trigger Calculation with the correct test session
    real_process_batch(run_id, db_session=session)
    
    # 4. Check Results
    response = client.get(f"/api/payroll/batch/{run_id}/results", headers=headers)
    assert response.status_code == 200
    results = response.json()
    
    assert len(results) == 1
    result = results[0]
    
    print("\n--- Computation Result ---")
    print(f"Gross: {result['gross_income']}")
    print(f"Net Pay: {result['net_pay']}")
    
    assert result['gross_income'] == 13500.0
    assert abs(result['net_pay'] - 12022.50) < 0.01
