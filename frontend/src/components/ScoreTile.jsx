import { STATUS_COLORS, scoreBand } from './status'

export default function ScoreTile({ label, score, hero = false }) {
  const band = scoreBand(score)

  return (
    <div className={hero ? 'tile tile-hero' : 'tile'}>
      <span className="tile-label">{label}</span>
      <span className="tile-value">{score}</span>
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
      <span className="tile-band">{band.label}</span>
    </div>
  )
}
