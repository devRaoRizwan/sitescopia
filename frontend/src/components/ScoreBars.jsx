import { CATEGORY_LABELS, STATUS_COLORS, scoreBand } from './status'

export default function ScoreBars({ byCategory, active, onSelect }) {
  const rows = Object.entries(byCategory).sort(([, a], [, b]) => a - b)

  return (
    <figure className="chart chart-bars">
      <figcaption>Score by category</figcaption>

      <ul className="bars">
        {rows.map(([key, score]) => {
          const band = scoreBand(score)
          const isActive = active === key
          return (
            <li key={key}>
              <button
                type="button"
                className={isActive ? 'bar-row active' : 'bar-row'}
                onClick={() => onSelect(isActive ? 'all' : key)}
                aria-pressed={isActive}
                title={`Show only ${CATEGORY_LABELS[key]} findings`}
              >
                <span className="bar-label">{CATEGORY_LABELS[key]}</span>
                <span className="bar-track">
                  <span
                    className="bar-fill"
                    style={{ width: `${Math.max(score, 2)}%`, background: STATUS_COLORS[band.role] }}
                  />
                </span>
                <span className="bar-value">{score}</span>
              </button>
            </li>
          )
        })}
      </ul>

      <p className="chart-note">Click a category to filter the findings below.</p>
    </figure>
  )
}
