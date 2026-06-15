export type RawFileStatus = {
  total: number;
  fetched: number;
  fetchFailed: number;
  processPending: number;
  processProcessed: number;
  processFailed: number;
};

export type LatestActivity = {
  fetchedAt?: string | null;
  processedAt?: string | null;
  scannedAt?: string | null;
};

export type CrawlError = {
  kind: string;
  player: string;
  name?: string | null;
  message: string;
  at?: string | null;
};

export type CrawlStatus = {
  artifactCount: number;
  crawlActive: boolean;
  rawFiles: RawFileStatus;
  crawlFiles: Record<string, number>;
  crawlUsers: Record<string, number>;
  latest: LatestActivity;
  recentErrors: CrawlError[];
};

export type GalleryApiMetrics = {
  status: 'ok' | 'unavailable' | string;
  windowSeconds: number;
  requestRatePerSecond?: number | null;
  errorRatePerSecond?: number | null;
  p95LatencySeconds?: number | null;
  inFlightRequests?: number | null;
  error?: string | null;
};
