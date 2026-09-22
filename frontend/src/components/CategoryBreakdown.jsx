import { CATEGORY_LABELS, SEVERITY_COLORS, STATUS_COLORS, scoreBand } from './status'

const STACK = ['error', 'warning', 'info', 'pass']

export default function CategoryBreakdown({ byCategory, findings, active, onSelect }) {
  const counts = {}
  for (const finding of findings) {
    counts[finding.category] ??= { error: 0, warning: 0, info: 0, pass: 0, total: 0 }
    counts[finding.category][finding.severity] += 1
    counts[finding.category].total += 1
  }

  const rows = Object.entries(byCategory).sort(([, a], [, b]) => a - b)

  return (
    <figure className="chart chart-breakdown">
      <figcaption>
        <span>Category breakdown</span>
        <strong>Tap to filter</strong>
      </figcaption>

      <ul className="breakdown">
        {rows.map(([key, score]) => {
          const band = scoreBand(score)
          const tally = counts[key] ?? { total: 0 }
          const isActive = active === key
          const summary = STACK.filter((s) => tally[s]).map((s) => `${tally[s]} ${s}`).join(', ')

          return (
            <li key={key}>
              <button
                type="button"
                className={isActive ? 'breakdown-row active' : 'breakdown-row'}
                onClick={() => onSelect(isActive ? 'all' : key)}
                aria-pressed={isActive}
                title={`${CATEGORY_LABELS[key]}: ${score}/100 (${band.label}) — ${summary}. Click to filter.`}
              >
                <span className="breakdown-name">
                  <span className={`dot dot-${key}`} aria-hidden="true" />
                  {CATEGORY_LABELS[key]}
                </span>

                <span className="breakdown-score" style={{ color: STATUS_COLORS[band.role] }}>
                  {score}
                </span>

                <span className="breakdown-track">
                  {STACK.filter((severity) => tally[severity] > 0).map((severity) => (
                    <span
                      key={severity}
                      style={{
                        flexGrow: tally[severity],
                        background: SEVERITY_COLORS[severity],
                      }}
                    />
                  ))}
                </span>

                <span className="breakdown-count">{tally.total}</span>
              </button>
            </li>
          )
        })}
      </ul>

      <ul className="legend legend-row">
        {STACK.map((severity) => (
          <li key={severity}>
            <span className="swatch" style={{ background: SEVERITY_COLORS[severity] }} aria-hidden="true" />
            <span className="legend-label">{severity}</span>
          </li>
        ))}
      </ul>
    </figure>
  )
}
