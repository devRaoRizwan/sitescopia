import { CATEGORY_LABELS, SEVERITY } from './status'

export default function FindingCard({ finding }) {
  const severity = SEVERITY[finding.severity]

  return (
    <article className={`finding finding-${finding.severity}`}>
      <span className="sev" aria-hidden="true">
        {severity.icon}
      </span>
      <div className="finding-body">
        <div className="finding-head">
          <h4>{finding.title}</h4>
          <span className="sr-only">{severity.label}</span>
          <span className={`cat dot-${finding.category}`}>{CATEGORY_LABELS[finding.category]}</span>
        </div>
        {finding.detail && <p className="detail">{finding.detail}</p>}
        {finding.evidence && <pre className="evidence">{finding.evidence}</pre>}
        {finding.recommendation && (
          <p className="fix">
            <strong>Fix</strong> {finding.recommendation}
          </p>
        )}
      </div>
    </article>
  )
}
