const FORMATS = {
  leaderboard: { width: 728, height: 90, className: 'ad-leaderboard' },
  rectangle: { width: 300, height: 250, className: 'ad-rectangle' },
  inline: { width: null, height: 120, className: 'ad-inline' },
}

export default function AdSlot({ format = 'rectangle', sticky = false }) {
  const { width, height, className } = FORMATS[format]

  return (
    <aside
      className={`ad ${className} ${sticky ? 'ad-sticky' : ''}`}
      style={{ minHeight: height, maxWidth: width ?? '100%' }}
      aria-label="Advertisement"
    >
      <span className="ad-label">Advertisement</span>
      <div className="ad-body">
        <span className="ad-size">{width ? `${width}×${height}` : `responsive · ${height}px`}</span>
      </div>
    </aside>
  )
}
