import { useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { open } from '@tauri-apps/api/dialog';
import { BatchSummary } from './types';
import './index.css';

function App() {
  const [filePath, setFilePath] = useState<string>('');
  const [summary, setSummary] = useState<BatchSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function selectFile() {
    try {
      const selected = await open({
        multiple: false,
        filters: [{
          name: 'CSV Files',
          extensions: ['csv']
        }]
      });
      
      if (typeof selected === 'string') {
        setFilePath(selected);
        setSummary(null);
        setError(null);
      }
    } catch (err) {
      console.error(err);
    }
  }

  async function processBatch() {
    if (!filePath) return;
    setLoading(true);
    try {
      const res = await invoke<BatchSummary>("process_csv", { filePath });
      setSummary(res);
      setError(null);
    } catch (e) {
      setError(String(e));
      setSummary(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container">
      <h1>SweldoSync Engine</h1>
      <p className="subtitle">Enterprise Payroll Batch Processor</p>
      
      <div className="card">
        <div className="input-group">
          <label>Source Data (CSV)</label>
          <div className="file-select-row">
            <input 
              type="text" 
              readOnly 
              value={filePath} 
              placeholder="Select a timesheet file..."
            />
            <button className="secondary" onClick={selectFile}>Browse</button>
          </div>
        </div>

        <button onClick={processBatch} disabled={!filePath || loading}>
          {loading ? 'Processing...' : 'Run Batch Calculation'}
        </button>
      </div>

      {error && <div className="error">{error}</div>}

      {summary && (
        <div className="result">
          <h2>Batch Audit Report</h2>
          <div className="summary-grid">
            <div className="stat-box">
              <h3>Processed</h3>
              <p>{summary.processed_count}</p>
            </div>
            <div className="stat-box">
              <h3>Total Cost</h3>
              <p>₱ {summary.total_payroll_cost.toLocaleString()}</p>
            </div>
            <div className="stat-box error-box">
              <h3>Errors</h3>
              <p>{summary.errors.length}</p>
            </div>
          </div>

          {summary.errors.length > 0 && (
            <div className="error-log">
              <h4>Error Log</h4>
              <ul>
                {summary.errors.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </div>
          )}

          <div className="details-table">
            <h4>Employee Breakdown</h4>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Hours</th>
                  <th>ND Hrs</th>
                  <th>Net Pay</th>
                </tr>
              </thead>
              <tbody>
                {summary.details.slice(0, 10).map((d) => (
                  <tr key={d.employee_id}>
                    <td>{d.employee_id}</td>
                    <td>{d.total_hours}</td>
                    <td>{d.night_diff_hours}</td>
                    <td>₱ {d.total_pay}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {summary.details.length > 10 && <p className="more-text">...and {summary.details.length - 10} more rows.</p>}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
