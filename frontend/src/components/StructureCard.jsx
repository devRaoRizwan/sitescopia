import { FileIcon, HashIcon, LinkIcon, ServerIcon } from './icons'

const formatNumber = (value) => value.toLocaleString()

export default function StructureCard({ structure }) {
  if (!structure) return null

  const stats = [
    { label: 'Words', value: formatNumber(structure.word_count), Icon: FileIcon },
    {
      label: 'Links',
      value: `${structure.links_internal} internal · ${structure.links_external} external`,
      Icon: LinkIcon,
    },
    {
      label: 'Images',
      value: structure.images_without_alt
        ? `${structure.images} · ${structure.images_without_alt} missing alt`
        : formatNumber(structure.images),
      Icon: HashIcon,
    },
    {
      label: 'Assets',
      value: `${structure.scripts} scripts · ${structure.stylesheets} styles`,
      Icon: ServerIcon,
    },
  ]

  const skipped = structure.headings.some(
    (heading, index) => index > 0 && heading.level > structure.headings[index - 1].level + 1,
  )

  return (
    <section className="insight-card">
      <h3>
        <FileIcon className="card-icon" />
        Page structure
      </h3>

      <div className="structure-stats">
        {stats.map(({ label, value, Icon }) => (
          <div key={label} className="structure-stat">
            <Icon className="fact-icon" />
            <span className="structure-stat-label">{label}</span>
            <span className="structure-stat-value">{value}</span>
          </div>
        ))}
      </div>

      {structure.headings.length > 0 ? (
        <div className="outline">
          <span className="fact-group-title">
            Heading outline
            <em>
              {structure.heading_total} total
              {skipped && ' · levels skip'}
            </em>
          </span>
          <ul>
            {structure.headings.map((heading, index) => (
              <li key={`${heading.level}-${index}`}>
                <span className="outline-level" data-level={heading.level}>
                  h{heading.level}
                </span>
                <span className="outline-text" style={{ paddingLeft: (heading.level - 1) * 10 }}>
                  {heading.text}
                </span>
              </li>
            ))}
          </ul>
          {structure.heading_total > structure.headings.length && (
            <p className="outline-more">
              + {structure.heading_total - structure.headings.length} more
            </p>
          )}
        </div>
      ) : (
        <p className="insight-note">This page has no headings at all.</p>
      )}
    </section>
  )
}
