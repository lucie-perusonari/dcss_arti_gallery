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
  rawFiles: RawFileStatus;
  crawlFiles: Record<string, number>;
  crawlUsers: Record<string, number>;
  latest: LatestActivity;
  recentErrors: CrawlError[];
};
