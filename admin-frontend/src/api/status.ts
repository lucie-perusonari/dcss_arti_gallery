import type { CrawlStatus } from '../types/status';

const API_BASE_URL = (import.meta.env.VITE_ADMIN_API_URL ?? 'http://127.0.0.1:8000').trim();

const mockStatus: CrawlStatus = {
  artifactCount: 0,
  rawFiles: {
    total: 0,
    fetched: 0,
    fetchFailed: 0,
    processPending: 0,
    processProcessed: 0,
    processFailed: 0,
  },
  crawlFiles: {},
  crawlUsers: {},
  latest: {},
  recentErrors: [],
};

const apiUrl = (path: string) => `${API_BASE_URL.replace(/\/$/, '')}${path}`;

export async function fetchCrawlStatus(): Promise<CrawlStatus> {
  if (!API_BASE_URL) return mockStatus;
  const response = await fetch(apiUrl('/admin/crawl-status'));
  if (!response.ok) {
    throw new Error(`Crawl status API failed with ${response.status}`);
  }
  return (await response.json()) as CrawlStatus;
}
