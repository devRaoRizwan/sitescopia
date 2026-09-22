import { SearchIcon } from './icons'

const TITLE_LIMIT = 60
const DESCRIPTION_LIMIT = 155

const truncate = (value, limit) =>
  value && value.length > limit ? `${value.slice(0, limit - 1).trimEnd()}…` : value

const crumbs = (url) => {
  try {
    const parsed = new URL(url)
    const parts = parsed.pathname.split('/').filter(Boolean)
    return [parsed.hostname.replace(/^www\./, ''), ...parts].join(' › ')
  } catch {
    return url
  }
}

export default function SearchPreview({ page }) {
  const title = page.title || '(no title — Google will invent one)'
  const description = page.meta_description

  const titleNote =
    !page.title
      ? { tone: 'bad', text: 'No title tag. Google will pick text from the page instead.' }
      : page.title.length > TITLE_LIMIT
        ? { tone: 'warn', text: `${page.title.length} characters — Google cuts around ${TITLE_LIMIT}, so the end is hidden.` }
        : { tone: 'good', text: `${page.title.length} characters — fits.` }

  const descriptionNote = !description
    ? { tone: 'warn', text: 'No description. Google will pull a sentence from the page, and it is rarely the one you would choose.' }
    : description.length > DESCRIPTION_LIMIT
      ? { tone: 'warn', text: `${description.length} characters — Google cuts around ${DESCRIPTION_LIMIT}.` }
      : { tone: 'good', text: `${description.length} characters — fits.` }

  return (
    <section className="insight-card search-preview">
      <h3>
        <SearchIcon className="card-icon" />
        How this looks in Google
      </h3>

      <div className="serp">
        <div className="serp-site">
          {page.favicon && <img src={page.favicon} alt="" width={16} height={16} referrerPolicy="no-referrer" />}
          <div>
            <span className="serp-name">{page.site_name}</span>
            <span className="serp-crumbs">{crumbs(page.final_url)}</span>
          </div>
        </div>

        <p className="serp-title">{truncate(title, TITLE_LIMIT)}</p>
        <p className="serp-description">
          {description ? truncate(description, DESCRIPTION_LIMIT) : 'Google will choose a snippet from your page text.'}
        </p>
      </div>

      <dl className="serp-notes">
        <div>
          <dt>Title</dt>
          <dd className={`note note-${titleNote.tone}`}>{titleNote.text}</dd>
        </div>
        <div>
          <dt>Description</dt>
          <dd className={`note note-${descriptionNote.tone}`}>{descriptionNote.text}</dd>
        </div>
        {page.robots && page.robots.toLowerCase().includes('noindex') && (
          <div>
            <dt>Indexing</dt>
            <dd className="note note-bad">This page tells Google not to list it at all.</dd>
          </div>
        )}
      </dl>
    </section>
  )
}
