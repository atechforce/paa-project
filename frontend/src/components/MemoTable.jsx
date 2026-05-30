import React from "react";
export default function MemoTable({ memoTable }) {
  if (!memoTable?.length) return null;

  return (
    <section className="card wide-card">
      <div className="section-header">
        <div>
          <p className="eyebrow">Memoization</p>
          <h2>Tabel Memo DP</h2>
        </div>
        <span className="badge">{memoTable.length} state</span>
      </div>
      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>State</th>
              <th>Current Node</th>
              <th>Visited Mask</th>
              <th>Value</th>
              <th>Best Next Node</th>
            </tr>
          </thead>
          <tbody>
            {memoTable.map((row, index) => (
              <tr key={`${row.state}-${index}`}>
                <td><code>{row.state}</code></td>
                <td>{row.currentNode}</td>
                <td><code>{row.visitedMask}</code></td>
                <td>{row.value.toFixed(2)}</td>
                <td>{row.bestNextNode}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
