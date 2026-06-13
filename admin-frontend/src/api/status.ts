import type { CrawlStatus, GalleryApiMetrics } from '../types/status';

const API_BASE_URL = (import.meta.env.VITE_ADMIN_API_URL ?? 'http://127.0.0.1:8001').trim();

const apiUrl = (path: string) => `${API_BASE_URL.replace(/\/$/, '')}${path}`;

export async function fetchCrawlStatus(signal?: AbortSignal): Promise<CrawlStatus> {
  const response = await fetch(apiUrl('/admin/crawl-status'), { signal });
  if (!response.ok) {
    throw new Error(`Crawl status API failed with ${response.status}`);
  }
  return (await response.json()) as CrawlStatus;
}

export async function fetchGalleryApiMetrics(signal?: AbortSignal): Promise<GalleryApiMetrics> {
  const response = await fetch(apiUrl('/admin/metrics/gallery-api'), { signal });
  if (!response.ok) {
    throw new Error(`Gallery API metrics failed with ${response.status}`);
  }
  return (await response.json()) as GalleryApiMetrics;
}
