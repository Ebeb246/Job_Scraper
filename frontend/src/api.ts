// Thin API client for the backend. Base URL is /api in both Docker (nginx
// proxy) and dev (vite proxy); overridable via VITE_API_BASE_URL.
const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

export interface Job {
  id: number
  title: string
  company: string
  location: string | null
  tags: string[]
  date_posted: string | null
  url: string
}

export interface JobList {
  count: number
  items: Job[]
}

export interface Stats {
  total_jobs: number
  top_tags: { tag: string; count: number }[]
  jobs_per_day: { day: string; count: number }[]
}

export interface ScrapeResult {
  fetched: number
  inserted: number
  skipped: number
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

export function getStats(): Promise<Stats> {
  return request<Stats>('/stats')
}

export function getJobs(keyword: string, company: string): Promise<JobList> {
  const params = new URLSearchParams()
  if (keyword) params.set('keyword', keyword)
  if (company) params.set('company', company)
  const query = params.toString()
  return request<JobList>(`/jobs${query ? `?${query}` : ''}`)
}

export function triggerScrape(): Promise<ScrapeResult> {
  return request<ScrapeResult>('/scrape', { method: 'POST' })
}
