import { CATEGORY_LABELS, SEVERITY_COLORS } from './status'

const STACK = ['error', 'warning', 'info', 'pass']

export default function CategoryBars({ findings, active, onSelect }) {
  const totals = {}
  for (const finding of findings) {
    totals[finding.category] ??= { error: 0, warning: 0, info: 0, pass: 0, total: 0 }
    totals[finding.category][finding.severity] += 1
    totals[finding.category].total += 1
  }

  const rows = Object.entries(totals).sort(([, a], [, b]) => b.total - a.total)
  const max = Math.max(...rows.map(([, counts]) => counts.total), 1)

  return (
    <figure className="chart chart-stack">
      <figcaption>Findings per category</figcaption>

      <ul className="bars">
        {rows.map(([category, counts]) => {
          const isActive = active === category
          const summary = STACK.filter((s) => counts[s]).map((s) => `${counts[s]} ${s}`).join(', ')
          return (
            <li key={category}>
              <button
                type="button"
                className={isActive ? 'bar-row active' : 'bar-row'}
                onClick={() => onSelect(isActive ? 'all' : category)}
                aria-pressed={isActive}
                title={`${CATEGORY_LABELS[category]}: ${summary}`}
              >
                <span className="bar-label">{CATEGORY_LABELS[category]}</span>
                <span className="bar-track">
                  <span className="bar-stack" style={{ width: `${(counts.total / max) * 100}%` }}>
                    {STACK.filter((severity) => counts[severity] > 0).map((severity) => (
                      <span
                        key={severity}
                        style={{ flexGrow: counts[severity], background: SEVERITY_COLORS[severity] }}
                      />
                    ))}
                  </span>
                </span>
                <span className="bar-value">{counts.total}</span>
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
