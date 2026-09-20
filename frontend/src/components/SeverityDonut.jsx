import { useState } from 'react'
import { STATUS_COLORS } from './status'

const SEGMENTS = [
  { key: 'error', label: 'Errors', color: STATUS_COLORS.critical },
  { key: 'warning', label: 'Warnings', color: STATUS_COLORS.warning },
  { key: 'info', label: 'Notes', color: STATUS_COLORS.serious },
  { key: 'pass', label: 'Passed', color: STATUS_COLORS.good },
]

const SIZE = 132
const STROKE = 18
const RADIUS = (SIZE - STROKE) / 2
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const GAP = 3

export default function SeverityDonut({ counts, total }) {
  const [active, setActive] = useState(null)
  const present = SEGMENTS.filter((segment) => counts[segment.key] > 0)
  let offset = 0
  const arcs = present.map((segment) => {
    const value = counts[segment.key]
    const length = total ? (value / total) * CIRCUMFERENCE : 0
    const arc = { ...segment, value, length, offset }
    offset += length
    return arc
  })
  const focused = arcs.find((arc) => arc.key === active)

  return (
    <figure className="chart chart-severity">
      <figcaption>
        <span>Findings overview</span>
        <strong>{total} checked</strong>
      </figcaption>

      <div className="donut-wrap">
        <svg
          width={SIZE}
          height={SIZE}
          viewBox={`0 0 ${SIZE} ${SIZE}`}
          role="img"
          aria-label={`${total} findings: ${arcs.map((arc) => `${arc.value} ${arc.label}`).join(', ')}`}
        >
          <circle
            cx={SIZE / 2}
            cy={SIZE / 2}
            r={RADIUS}
            fill="none"
            stroke="var(--brand-100)"
            strokeWidth={STROKE}
          />
          <g transform={`rotate(-90 ${SIZE / 2} ${SIZE / 2})`}>
            {arcs.map((arc) => (
              <circle
                key={arc.key}
                cx={SIZE / 2}
                cy={SIZE / 2}
                r={RADIUS}
                fill="none"
                stroke={arc.color}
                strokeWidth={active && active !== arc.key ? STROKE - 5 : STROKE}
                strokeDasharray={`${Math.max(arc.length - GAP, 0.5)} ${CIRCUMFERENCE}`}
                strokeDashoffset={-arc.offset}
                onMouseEnter={() => setActive(arc.key)}
                onMouseLeave={() => setActive(null)}
              />
            ))}
          </g>
        </svg>
        <div className="donut-center">
          <strong>{focused ? focused.value : total}</strong>
          <span>{focused ? focused.label : 'findings'}</span>
        </div>
      </div>

      <ul className="severity-list" aria-label={`${total} findings by severity`}>
        {arcs.map((arc) => {
          const percentage = total ? Math.round((arc.value / total) * 100) : 0
          return (
            <li
              key={arc.key}
              className={active === arc.key ? 'active' : ''}
              onMouseEnter={() => setActive(arc.key)}
              onMouseLeave={() => setActive(null)}
            >
              <span className="severity-marker" style={{ background: arc.color }} aria-hidden="true" />
              <span className="severity-label">{arc.label}</span>
              <span className="severity-percent">{percentage}%</span>
              <strong>{arc.value}</strong>
            </li>
          )
        })}
      </ul>
    </figure>
  )
}
