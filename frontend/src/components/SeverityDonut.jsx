import { STATUS_COLORS } from './status'

const SEGMENTS = [
  { key: 'error', label: 'Errors', color: STATUS_COLORS.critical },
  { key: 'warning', label: 'Warnings', color: STATUS_COLORS.warning },
  { key: 'info', label: 'Notes', color: STATUS_COLORS.serious },
  { key: 'pass', label: 'Passed', color: STATUS_COLORS.good },
]

export default function SeverityDonut({ counts, total }) {
  const present = SEGMENTS.filter((segment) => counts[segment.key] > 0)

  return (
    <figure className="chart chart-severity">
      <figcaption>
        <span>Findings overview</span>
        <strong>{total} checked</strong>
      </figcaption>

      <ul className="severity-list" aria-label={`${total} findings by severity`}>
        {present.map((segment) => {
          const value = counts[segment.key]
          const percentage = total ? Math.round((value / total) * 100) : 0
          return (
            <li key={segment.key}>
              <span className="severity-marker" style={{ background: segment.color }} aria-hidden="true" />
              <span className="severity-label">{segment.label}</span>
              <span className="severity-percent">{percentage}%</span>
              <strong>{value}</strong>
            </li>
          )
        })}
      </ul>
    </figure>
  )
}
