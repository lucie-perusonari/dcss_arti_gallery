import type { CrawlStatus, GalleryApiMetrics } from '../types/status';

const API_BASE_URL = (import.meta.env.VITE_ADMIN_API_URL ?? 'http://127.0.0.1:8001').trim();

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

const mockGalleryApiMetrics: GalleryApiMetrics = {
  status: 'unavailable',
  windowSeconds: 300,
  requestRatePerSecond: null,
  errorRatePerSecond: null,
  p95LatencySeconds: null,
  inFlightRequests: null,
  error: 'Admin API URL is not configured.',
};

const apiUrl = (path: string) => `${API_BASE_URL.replace(/\/$/, '')}${path}`;

export async function fetchCrawlStatus(signal?: AbortSignal): Promise<CrawlStatus> {
  if (!API_BASE_URL) return mockStatus;
  const response = await fetch(apiUrl('/admin/crawl-status'), { signal });
  if (!response.ok) {
    throw new Error(`Crawl status API failed with ${response.status}`);
  }
  return (await response.json()) as CrawlStatus;
}

export async function fetchGalleryApiMetrics(signal?: AbortSignal): Promise<GalleryApiMetrics> {
  if (!API_BASE_URL) return mockGalleryApiMetrics;
  const response = await fetch(apiUrl('/admin/metrics/gallery-api'), { signal });
  if (!response.ok) {
    throw new Error(`Gallery API metrics failed with ${response.status}`);
  }
  return (await response.json()) as GalleryApiMetrics;
}
