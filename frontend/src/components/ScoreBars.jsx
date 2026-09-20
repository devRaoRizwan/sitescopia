import { CATEGORY_LABELS } from './status'

export default function ScoreBars({ byCategory, active, onSelect }) {
  const rows = Object.entries(byCategory).sort(([, a], [, b]) => a - b)

  return (
    <figure className="chart chart-bars chart-scores">
      <figcaption>
        <span>Category health</span>
        <strong>Tap to filter</strong>
      </figcaption>

      <ul className="bars">
        {rows.map(([key, score]) => {
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
                    style={{ width: `${Math.max(score, 2)}%` }}
                  />
                </span>
                <span className="bar-value">{score}</span>
              </button>
            </li>
          )
        })}
      </ul>
    </figure>
  )
}
