<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { getJobs, getStats, triggerScrape, type Job, type Stats } from './api'

const stats = ref<Stats | null>(null)
const jobs = ref<Job[]>([])
const keyword = ref('')
const company = ref('')

const scraping = ref(false)
const loadingJobs = ref(false)
const error = ref('')
const notice = ref('')

// Largest tag count, used to scale the bar-chart widths to 100%.
const maxTagCount = computed(() => stats.value?.top_tags[0]?.count ?? 0)

async function loadStats() {
  stats.value = await getStats()
}

async function loadJobs() {
  loadingJobs.value = true
  try {
    const data = await getJobs(keyword.value.trim(), company.value.trim())
    jobs.value = data.items
  } finally {
    loadingJobs.value = false
  }
}

async function scrape() {
  scraping.value = true
  error.value = ''
  notice.value = ''
  try {
    const result = await triggerScrape()
    notice.value = `Scraped ${result.fetched} jobs — ${result.inserted} new, ${result.skipped} already stored.`
    await Promise.all([loadStats(), loadJobs()])
  } catch (e) {
    error.value = `Scrape failed: ${(e as Error).message}`
  } finally {
    scraping.value = false
  }
}

// Re-filter as the user types, debounced so we don't hit the API per keystroke.
let debounce: ReturnType<typeof setTimeout>
watch([keyword, company], () => {
  clearTimeout(debounce)
  debounce = setTimeout(loadJobs, 300)
})

function formatDate(value: string | null): string {
  if (!value) return '—'
  return new Date(value).toLocaleDateString()
}

onMounted(async () => {
  try {
    await Promise.all([loadStats(), loadJobs()])
  } catch (e) {
    error.value = `Could not reach the API: ${(e as Error).message}`
  }
})
</script>

<template>
  <div class="page">
    <header class="header">
      <div>
        <h1>Job Listings Dashboard</h1>
        <p class="subtitle">Remote jobs scraped from RemoteOK</p>
      </div>
      <button class="btn-primary" :disabled="scraping" @click="scrape">
        {{ scraping ? 'Scraping…' : 'Scrape now' }}
      </button>
    </header>

    <p v-if="notice" class="banner banner-ok">{{ notice }}</p>
    <p v-if="error" class="banner banner-error">{{ error }}</p>

    <section class="cards">
      <div class="card stat">
        <span class="stat-value">{{ stats?.total_jobs ?? '—' }}</span>
        <span class="stat-label">Total jobs stored</span>
      </div>
      <div class="card stat">
        <span class="stat-value">{{ stats?.top_tags.length ?? '—' }}</span>
        <span class="stat-label">Tags in top list</span>
      </div>
      <div class="card stat">
        <span class="stat-value">{{ jobs.length }}</span>
        <span class="stat-label">Jobs shown</span>
      </div>
    </section>

    <section class="card">
      <h2>Top skills</h2>
      <div v-if="stats && stats.top_tags.length" class="chart">
        <div v-for="t in stats.top_tags" :key="t.tag" class="bar-row">
          <span class="bar-label">{{ t.tag }}</span>
          <div class="bar-track">
            <div class="bar-fill" :style="{ width: `${(t.count / maxTagCount) * 100}%` }" />
          </div>
          <span class="bar-value">{{ t.count }}</span>
        </div>
      </div>
      <p v-else class="empty">No data yet.</p>
    </section>

    <section class="card">
      <div class="table-head">
        <h2>Jobs</h2>
        <div class="filters">
          <input v-model="keyword" placeholder="Filter by keyword…" />
          <input v-model="company" placeholder="Filter by company…" />
        </div>
      </div>

      <table v-if="jobs.length">
        <thead>
          <tr>
            <th>Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Tags</th>
            <th>Posted</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id">
            <td>
              <a :href="job.url" target="_blank" rel="noopener">{{ job.title }}</a>
            </td>
            <td>{{ job.company }}</td>
            <td>{{ job.location ?? '—' }}</td>
            <td>
              <span v-for="tag in job.tags.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
              <span v-if="job.tags.length > 3" class="tag-more">+{{ job.tags.length - 3 }}</span>
            </td>
            <td class="nowrap">{{ formatDate(job.date_posted) }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">
        {{ loadingJobs ? 'Loading…' : 'No jobs match. Try scraping or clearing filters.' }}
      </p>
    </section>
  </div>
</template>

<style>
:root {
  --bg: #f6f7f9;
  --card: #ffffff;
  --border: #e5e7eb;
  --text: #111827;
  --muted: #6b7280;
  --accent: #2563eb;
  --accent-soft: #dbeafe;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}
</style>

<style scoped>
.page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.25rem 4rem;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

h1 {
  margin: 0;
  font-size: 1.5rem;
}

.subtitle {
  margin: 0.25rem 0 0;
  color: var(--muted);
  font-size: 0.9rem;
}

h2 {
  margin: 0 0 1rem;
  font-size: 1.05rem;
}

.btn-primary {
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.1rem;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s ease;
  white-space: nowrap;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.9;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: default;
}

.banner {
  margin: 0 0 1rem;
  padding: 0.7rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.banner-ok {
  background: #ecfdf5;
  color: #065f46;
}

.banner-error {
  background: #fef2f2;
  color: #991b1b;
}

.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.25rem;
  margin-bottom: 1.25rem;
}

.cards .card {
  margin-bottom: 0;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
}

.stat-label {
  color: var(--muted);
  font-size: 0.85rem;
}

.chart {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.bar-row {
  display: grid;
  grid-template-columns: 120px 1fr 40px;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.88rem;
}

.bar-label {
  color: var(--muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bar-track {
  background: var(--bg);
  border-radius: 6px;
  height: 18px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.bar-value {
  text-align: right;
  font-variant-numeric: tabular-nums;
  color: var(--muted);
}

.table-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.table-head h2 {
  margin: 0;
}

.filters {
  display: flex;
  gap: 0.5rem;
}

.filters input {
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.45rem 0.7rem;
  font-size: 0.85rem;
  outline: none;
}

.filters input:focus {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-soft);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.88rem;
}

th {
  text-align: left;
  color: var(--muted);
  font-weight: 600;
  padding: 0.5rem 0.6rem;
  border-bottom: 1px solid var(--border);
}

td {
  padding: 0.6rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}

tbody tr:last-child td {
  border-bottom: none;
}

td a {
  color: var(--accent);
  text-decoration: none;
  font-weight: 600;
}

td a:hover {
  text-decoration: underline;
}

.nowrap {
  white-space: nowrap;
  color: var(--muted);
}

.tag {
  display: inline-block;
  background: var(--accent-soft);
  color: #1e40af;
  border-radius: 6px;
  padding: 0.1rem 0.45rem;
  margin: 0 0.25rem 0.25rem 0;
  font-size: 0.75rem;
}

.tag-more {
  color: var(--muted);
  font-size: 0.75rem;
}

.empty {
  color: var(--muted);
  font-size: 0.9rem;
  margin: 0;
}

@media (max-width: 640px) {
  .cards {
    grid-template-columns: 1fr;
  }
  .bar-row {
    grid-template-columns: 90px 1fr 32px;
  }
}
</style>
