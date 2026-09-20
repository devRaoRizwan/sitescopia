import { STATUS_COLORS, scoreBand } from './status'

export default function ScoreTile({ label, score, hero = false, errors = 0, warnings = 0, notes = 0 }) {
  const band = scoreBand(score)
  const statusLabel =
    band.role === 'good'
      ? 'Strong foundation'
      : band.role === 'warning'
        ? 'Needs attention'
        : band.role === 'serious'
          ? 'At risk'
          : 'Critical issues'
  const issues = errors + warnings + notes
  const issueLabel = issues === 1 ? '1 item to review' : `${issues} items to review`
  const summary =
    errors > 0
      ? `${errors} critical ${errors === 1 ? 'issue needs' : 'issues need'} attention first.`
      : issues > 0
        ? `${issueLabel} before this page is fully polished.`
        : 'All checks are currently passing cleanly.'

  return (
    <div className={hero ? 'tile tile-hero' : 'tile'}>
      <div className="score-heading">
        <span className="tile-label">{label}</span>
        <span className="score-status" style={{ color: STATUS_COLORS[band.role] }}>
          <span className="score-status-dot" aria-hidden="true" />
          {statusLabel}
        </span>
      </div>

      <div className="score-value-row">
        <span className="tile-value">{score}</span>
        <span className="score-denominator">/100</span>
      </div>

      <div
        className="meter"
        role="meter"
        aria-valuenow={score}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${label}: ${score} out of 100`}
      >
        <span style={{ width: `${score}%`, background: STATUS_COLORS[band.role] }} />
      </div>

      <div className="score-scale" aria-hidden="true">
        <span>Needs attention</span>
        <span>Excellent</span>
      </div>

      <p className="score-summary">{summary}</p>
      {issues > 0 && (
        <a className="score-review-link" href="#findings">
          Review findings <span aria-hidden="true">↓</span>
        </a>
      )}
    </div>
  )
}
