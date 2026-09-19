import { useState } from 'react'
import { useSeo } from '../seo'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getAnalysis, getChecks, startAnalysis } from '../api'
import Hero from '../components/Hero'
import Report from '../components/Report'
import Progress from '../components/Progress'
import Blocked from '../components/Blocked'
import Sidebar from '../components/Sidebar'
import AdSlot from '../components/AdSlot'
import { CATEGORY_LABELS } from '../components/status'

const POLL_INTERVAL_MS = 1500
const SETTLED = ['done', 'failed', 'blocked']

const STEPS = [
  { step: '01', title: 'We fetch it once', body: 'A single request, with strict limits on time, size and redirects. Private and internal addresses are refused outright.' },
  { step: '02', title: 'We pull out the facts', body: 'Headings, links, images, metadata, and headers, plus a registry and DNS lookup for the domain itself.' },
  { step: '03', title: 'Then 34 checks run', body: 'Each one tells you what it found, why it matters and exactly what to change.' },
]

const CHECK_CATEGORIES = [
  ['seo', 'Search visibility', 'Titles, descriptions, headings, canonicals and sharing metadata.'],
  ['accessibility', 'Accessibility', 'Language, image alternatives, viewport settings and heading structure.'],
  ['security', 'Security', 'HTTPS, protective headers, mixed content and version disclosure.'],
  ['performance', 'Performance', 'Response time, document size, compression, caching and images.'],
  ['content', 'Content quality', 'Status codes, redirects, thin content and link structure.'],
  ['domain', 'Domain signals', 'Registration, expiry, DNS and the domain behind the page.'],
  ['contact', 'Contact signals', 'Email, phone and social profiles that visitors can use.'],
]

export default function Home() {
  useSeo({
    title: 'Free Website Analyzer: SEO, Speed and Security',
    description:
      "Check any page for SEO, accessibility, security, speed and domain problems in seconds. Free, no signup, and every finding shows the evidence behind it.",
    path: '/',
  })

  const [jobId, setJobId] = useState(null)
  const [jobToken, setJobToken] = useState(null)

  const submit = useMutation({
    mutationFn: startAnalysis,
    onSuccess: (job) => {
      setJobId(job.id)
      setJobToken(job.access_token)
    },
  })
  const checks = useQuery({ queryKey: ['checks'], queryFn: getChecks, staleTime: Infinity })

  const job = useQuery({
    queryKey: ['analysis', jobId, jobToken],
    queryFn: () => getAnalysis(jobId, jobToken),
    enabled: Boolean(jobId && jobToken),
    refetchInterval: (query) =>
      SETTLED.includes(query.state.data?.status) ? false : POLL_INTERVAL_MS,
  })

  const data = job.data
  const busy = submit.isPending || (data && !SETTLED.includes(data.status))
  const hasSession = Boolean(jobId) || submit.isPending || submit.isError

  const analyze = (url) => {
    setJobId(null)
    setJobToken(null)
    submit.mutate(url)
  }

  return (
    <>
      <Hero onSubmit={analyze} busy={busy} compact={hasSession} checkCount={checks.data?.total} />

      {hasSession && (
        <div className={busy ? 'shell results results-loading' : 'shell results'}>
          <div className="results-main">
            {submit.isError && (
              <div className="alert">
                <strong>That URL was rejected</strong>
                <span>{submit.error.message}</span>
              </div>
            )}

            {busy && <Progress />}

            {data?.status === 'failed' && (
              <div className="alert">
                <strong>Could not analyze {data.url}</strong>
                <span>{data.error}</span>
              </div>
            )}

            {data?.status === 'blocked' && <Blocked url={data.url} reason={data.error} />}

            {data?.status === 'done' && <Report result={data.result} />}
          </div>

          <Sidebar />
        </div>
      )}

      {!hasSession && (
        <>
          <section className="section">
            <div className="shell">
              <h2 className="section-title">How it works</h2>
              <div className="steps">
                {STEPS.map(({ step, title, body }) => (
                  <article key={step} className="step">
                    <span className="step-number">{step}</span>
                    <h3>{title}</h3>
                    <p>{body}</p>
                  </article>
                ))}
              </div>
              <p className="section-more">
                <Link to="/how-it-works">Read the full walkthrough →</Link>
              </p>
            </div>
          </section>

          <section className="section section-alt">
            <div className="shell">
              <h2 className="section-title">What we check</h2>
              <div className="category-grid">
                {CHECK_CATEGORIES.map(([category, title, description]) => {
                  const count = checks.data?.by_category?.[category]?.length
                  return (
                    <article key={category} className="category-card">
                      <div className="category-card-head">
                        <span className={`dot dot-${category}`} aria-hidden="true" />
                        <h3>{title}</h3>
                        {count != null && <span className="category-card-count">{count}</span>}
                      </div>
                      <p>{description}</p>
                    </article>
                  )
                })}
              </div>
              <p className="section-more">
                <Link to="/checks">See all {checks.data?.total ?? ''} checks →</Link>
              </p>
            </div>
          </section>
        </>
      )}

      <div className="shell ad-footer-wrap">
        <AdSlot format="leaderboard" />
      </div>
    </>
  )
}
