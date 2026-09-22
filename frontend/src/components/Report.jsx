import { useState } from 'react'
import ScoreTile from './ScoreTile'
import SeverityDonut from './SeverityDonut'
import CategoryBreakdown from './CategoryBreakdown'
import DomainCard from './DomainCard'
import ContactsCard from './ContactsCard'
import StructureCard from './StructureCard'
import ElementInspector from './ElementInspector'
import SiteIdentity from './SiteIdentity'
import FindingsBrowser from './FindingsBrowser'
import PrintAppendix from './PrintAppendix'

const hostOf = (url) => {
  try {
    return new URL(url).hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

const countBySeverity = (findings) =>
  findings.reduce((counts, finding) => {
    counts[finding.severity] = (counts[finding.severity] || 0) + 1
    return counts
  }, {})

const printReport = () => {
  const originalTitle = document.title
  document.title = 'sitescopia_report'

  window.addEventListener(
    'afterprint',
    () => {
      document.title = originalTitle
    },
    { once: true },
  )

  window.print()
}

export default function Report({ result }) {
  const [category, setCategory] = useState('all')

  const { page, scores, findings, insights, diagnostics } = result
  const counts = countBySeverity(findings)

  return (
    <section className="report">
      <div className="print-header">
        <span className="print-brand">SiteScopia report</span>
        <span>
          {page.final_url}
          {' · '}
          {new Date().toLocaleDateString(undefined, {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </span>
      </div>

      <div className="report-head">
        <div className="page-meta">
          <SiteIdentity page={page} />
          <h2>{page.title || hostOf(page.final_url)}</h2>
          <span className="muted">
            HTTP {page.status} · {page.elapsed_ms} ms · {(page.bytes / 1024).toFixed(0)} KB
            {page.redirects.length > 0 &&
              ` · ${page.redirects.length} redirect${page.redirects.length === 1 ? '' : 's'}`}
          </span>
        </div>

        <div className="report-actions">
          <a
            className="ghost-button"
            href={page.final_url}
            target="_blank"
            rel="noopener noreferrer nofollow"
            title={page.final_url}
          >
            Visit site ↗
          </a>
          <button type="button" className="ghost-button" onClick={printReport}>
            Download PDF
          </button>
        </div>

        <div className="summary">
          {counts.error > 0 && <span className="pill pill-error">{counts.error} errors</span>}
          {counts.warning > 0 && <span className="pill pill-warning">{counts.warning} warnings</span>}
          {counts.info > 0 && <span className="pill pill-info">{counts.info} notes</span>}
          {counts.pass > 0 && <span className="pill pill-pass">{counts.pass} passed</span>}
        </div>
      </div>

      <div className="report-grid">
        <ScoreTile
          label="Overall health"
          score={scores.overall}
          hero
          errors={counts.error || 0}
          warnings={counts.warning || 0}
          notes={counts.info || 0}
        />
        <SeverityDonut counts={counts} total={findings.length} />
        <CategoryBreakdown
          byCategory={scores.by_category}
          findings={findings}
          active={category}
          onSelect={setCategory}
        />
      </div>

      <div className="insights">
        <DomainCard domain={insights.domain} />
        <ContactsCard contacts={insights.contacts} />
        <StructureCard structure={insights.structure} />
      </div>

      <div id="findings">
        <ElementInspector groups={insights.elements} />

      <FindingsBrowser findings={findings} category={category} onCategory={setCategory} />
      </div>

      <PrintAppendix findings={findings} diagnostics={diagnostics} />
    </section>
  )
}
