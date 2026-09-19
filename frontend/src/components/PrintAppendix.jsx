import { CATEGORY_LABELS, SEVERITY } from './status'

const ORDER = ['error', 'warning', 'info', 'pass']

export default function PrintAppendix({ findings, diagnostics = [] }) {
  const grouped = Object.keys(CATEGORY_LABELS)
    .map((category) => ({
      category,
      items: findings
        .filter((f) => f.category === category)
        .sort((a, b) => ORDER.indexOf(a.severity) - ORDER.indexOf(b.severity)),
    }))
    .filter((group) => group.items.length)

  return (
    <section className="print-appendix">
      <h2>Complete check results</h2>
      <p className="appendix-intro">
        Every check that ran, grouped by category and ordered by severity. This listing ignores
        the filters used on screen.
      </p>

      {grouped.map(({ category, items }) => (
        <section key={category} className="appendix-group">
          <h3>
            {CATEGORY_LABELS[category]} <span>{items.length} checks</span>
          </h3>

          <table className="appendix-table">
            <thead>
              <tr>
                <th scope="col">Result</th>
                <th scope="col">Check</th>
                <th scope="col">What to do</th>
              </tr>
            </thead>
            <tbody>
              {items.map((finding, index) => (
                <tr key={`${finding.title}-${index}`} className={`row-${finding.severity}`}>
                  <td className="appendix-severity">{SEVERITY[finding.severity].label}</td>
                  <td>
                    <strong>{finding.title}</strong>
                    {finding.detail && <span className="appendix-detail">{finding.detail}</span>}
                    {finding.evidence && <pre className="appendix-evidence">{finding.evidence}</pre>}
                  </td>
                  <td className="appendix-fix">{finding.recommendation || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      ))}

      {diagnostics.length > 0 && (
        <section className="appendix-group">
          <h3>Scanner diagnostics</h3>
          <ul className="appendix-diagnostics">
            {diagnostics.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </section>
      )}
    </section>
  )
}
