import { useRef, useState } from 'react'

const EXAMPLES = ['example.com', 'wikipedia.org', 'stripe.com']

export default function UrlForm({ onSubmit, busy, showExamples = false }) {
  const [url, setUrl] = useState('')
  const inputRef = useRef(null)

  const handleSubmit = (event) => {
    event.preventDefault()
    if (url.trim()) onSubmit(url.trim())
  }

  const handleExampleClick = (example) => {
    setUrl(example)
    if (window.matchMedia('(max-width: 680px)').matches) {
      onSubmit(example)
      return
    }
    inputRef.current?.focus()
  }

  return (
    <div className="url-block">
      <form className="url-form" onSubmit={handleSubmit}>
        <div className="url-field">
          <span className="url-prefix" aria-hidden="true">
            https://
          </span>
          <input
            ref={inputRef}
            type="text"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="example.com/pricing"
            aria-label="URL to analyze"
            spellCheck="false"
            autoComplete="url"
          />
        </div>
        <button type="submit" disabled={busy || !url.trim()}>
          {busy ? 'Analyzing…' : 'Analyze page'}
        </button>
      </form>

      {showExamples && (
        <p className="url-examples">
          <span>Or try</span>
          {EXAMPLES.map((example) => (
            <button
              key={example}
              type="button"
              disabled={busy}
              onClick={() => handleExampleClick(example)}
            >
              {example}
            </button>
          ))}
        </p>
      )}
    </div>
  )
}
