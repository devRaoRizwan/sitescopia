import { createContext, useContext, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { getAnalysis, startAnalysis } from './api'

const POLL_INTERVAL_MS = 1500
const SETTLED = ['done', 'failed', 'blocked']

const ScanContext = createContext(null)

export function ScanProvider({ children }) {
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

  const analyze = (url) => {
    setJobId(null)
    setJobToken(null)
    submit.mutate(url)
  }

  const value = {
    jobId,
    data,
    busy,
    analyze,
    hasSession: Boolean(jobId) || submit.isPending || submit.isError,
    submitError: submit.isError ? submit.error : null,
  }

  return <ScanContext.Provider value={value}>{children}</ScanContext.Provider>
}

export function useScan() {
  const value = useContext(ScanContext)
  if (!value) throw new Error('useScan must be used inside a ScanProvider')
  return value
}
