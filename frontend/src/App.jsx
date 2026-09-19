import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { getAnalysis, startAnalysis } from './api'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Hero from './components/Hero'
import HowItWorks from './components/HowItWorks'
import Report from './components/Report'
import Progress from './components/Progress'
import AdSlot from './components/AdSlot'
import Sidebar from './components/Sidebar'

const POLL_INTERVAL_MS = 1500
const SETTLED = ['done', 'failed', 'blocked']

export default function App() {
  const [jobId, setJobId] = useState(null)
  const [jobToken, setJobToken] = useState(null)

  const submit = useMutation({
    mutationFn: startAnalysis,
    onSuccess: (job) => {
      setJobId(job.id)
      setJobToken(job.access_token)
    },
  })

  const job = useQuery({
    queryKey: ['analysis', jobId, jobToken],
    queryFn: () => getAnalysis(jobId, jobToken),
    enabled: Boolean(jobId && jobToken),
    refetchInterval: (query) =>
      SETTLED.includes(query.state.data?.status) ? false : POLL_INTERVAL_MS,
  })

  const data = job.data
  const busy = submit.isPending || Boolean(jobId && (!data || !SETTLED.includes(data.status)))
  const hasSession = Boolean(jobId) || submit.isPending || submit.isError

  const analyze = (url) => {
    setJobId(null)
    setJobToken(null)
    submit.mutate(url)
  }

  return (
    <>
      <Navbar />

      <main>
        <Hero onSubmit={analyze} busy={busy} compact={hasSession} />

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

              {data?.status === 'done' && <Report result={data.result} />}
            </div>

            <Sidebar />
          </div>
        )}

        {!hasSession && <HowItWorks />}

        <div className="shell ad-footer-wrap">
          <AdSlot format="leaderboard" />
        </div>
      </main>

      <Footer />
    </>
  )
}
