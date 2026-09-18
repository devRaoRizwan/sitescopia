export default function PageHeader({ eyebrow, title, lead }) {
  return (
    <section className="page-header">
      <div className="shell">
        {eyebrow && <span className="eyebrow">{eyebrow}</span>}
        <h1>{title}</h1>
        {lead && <p className="lead">{lead}</p>}
      </div>
    </section>
  )
}
