import AdSlot from './AdSlot'

const TIPS = [
  'Start with errors. Those are the ones blocking indexing or locking people out.',
  'A pass is not praise. We check that something exists, not that it is any good.',
  'If the page builds itself with JavaScript, we only see the shell. Treat those findings as provisional.',
]

export default function Sidebar() {
  return (
    <aside className="results-side">
      <AdSlot format="rectangle" sticky />

      <section className="side-card">
        <h3>Reading this report</h3>
        <ul>
          {TIPS.map((tip) => (
            <li key={tip}>{tip}</li>
          ))}
        </ul>
      </section>
    </aside>
  )
}
