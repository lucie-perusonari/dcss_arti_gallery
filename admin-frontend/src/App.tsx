import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { fetchCrawlStatus, fetchGalleryApiMetrics } from './api/status';
import type { CrawlStatus, GalleryApiMetrics } from './types/status';

const REFRESH_MS = 15_000;
const GRAFANA_URL = (import.meta.env.VITE_GRAFANA_URL ?? '').trim();

export function App() {
  const [status, setStatus] = useState<CrawlStatus | null>(null);
  const [galleryApiMetrics, setGalleryApiMetrics] = useState<GalleryApiMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metricsError, setMetricsError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const crawlController = new AbortController();
    const metricsController = new AbortController();
    let crawlTimer: number | undefined;
    let metricsTimer: number | undefined;

    const scheduleCrawlStatus = () => {
      crawlTimer = window.setTimeout(loadCrawlStatus, REFRESH_MS);
    };
    const scheduleGalleryMetrics = () => {
      metricsTimer = window.setTimeout(loadGalleryMetrics, REFRESH_MS);
    };

    const loadCrawlStatus = () => {
      fetchCrawlStatus(crawlController.signal)
        .then((nextStatus) => {
          if (!active) return;
          setStatus(nextStatus);
          setError(null);
          setLastUpdated(new Date().toLocaleString());
        })
        .catch((reason: unknown) => {
          if (!active || isAbortError(reason)) return;
          setError(errorMessage(reason, 'Failed to load crawl status'));
        })
        .finally(() => {
          if (!active) return;
          setLoading(false);
          scheduleCrawlStatus();
        });
    };

    const loadGalleryMetrics = () => {
      fetchGalleryApiMetrics(metricsController.signal)
        .then((nextMetrics) => {
          if (!active) return;
          setGalleryApiMetrics(nextMetrics);
          setMetricsError(null);
        })
        .catch((reason: unknown) => {
          if (!active || isAbortError(reason)) return;
          setMetricsError(errorMessage(reason, 'Failed to load Gallery API metrics'));
        })
        .finally(() => {
          if (!active) return;
          scheduleGalleryMetrics();
        });
    };

    loadCrawlStatus();
    loadGalleryMetrics();

    return () => {
      active = false;
      crawlController.abort();
      metricsController.abort();
      if (crawlTimer) window.clearTimeout(crawlTimer);
      if (metricsTimer) window.clearTimeout(metricsTimer);
    };
  }, []);

  const health = useMemo(() => statusHealth(status), [status]);

  return (
    <main className="admin-shell">
      <header className="admin-header">
        <div>
          <p className="eyebrow">DCSS operations</p>
          <h1>Crawl Admin</h1>
        </div>
        <div className={`health health--${health.tone}`}>{health.label}</div>
      </header>

      <section className="toolbar">
        <span>{loading ? 'Loading status...' : `Updated ${lastUpdated ?? '-'}`}</span>
        {(error || metricsError) && <strong>{[error, metricsError].filter(Boolean).join(' / ')}</strong>}
      </section>

      <section className="metric-grid" aria-label="Crawl metrics">
        <Metric label="Artifacts" value={status?.artifactCount ?? 0} />
        <Metric label="Raw files" value={status?.rawFiles.total ?? 0} />
        <Metric label="Fetched raw" value={status?.rawFiles.fetched ?? 0} />
        <Metric label="Pending process" value={status?.rawFiles.processPending ?? 0} tone="warn" />
        <Metric label="Fetch failed" value={status?.rawFiles.fetchFailed ?? 0} tone="bad" />
        <Metric label="Process failed" value={status?.rawFiles.processFailed ?? 0} tone="bad" />
      </section>

      <section className="metric-grid" aria-label="Gallery API metrics">
        <Metric label="API req/s" value={formatRate(galleryApiMetrics?.requestRatePerSecond)} />
        <Metric
          label="API 5xx/s"
          value={formatRate(galleryApiMetrics?.errorRatePerSecond)}
          tone={(galleryApiMetrics?.errorRatePerSecond ?? 0) > 0 ? 'bad' : 'neutral'}
        />
        <Metric label="API p95" value={formatDuration(galleryApiMetrics?.p95LatencySeconds)} />
        <Metric label="In-flight" value={formatNumber(galleryApiMetrics?.inFlightRequests)} />
      </section>

      <section className="content-grid">
        <Panel title="Gallery API">
          <KeyValue label="Status" value={galleryApiMetrics?.status ?? 'unknown'} />
          <KeyValue label="Window" value={galleryApiMetrics ? `${galleryApiMetrics.windowSeconds}s` : '-'} />
          <KeyValue label="Prometheus" value={galleryApiMetrics?.error ?? 'ok'} />
          {GRAFANA_URL && (
            <a className="panel-link" href={GRAFANA_URL} rel="noreferrer" target="_blank">
              Open Grafana
            </a>
          )}
        </Panel>

        <Panel title="Latest Activity">
          <KeyValue label="Fetched" value={status?.latest.fetchedAt} />
          <KeyValue label="Processed" value={status?.latest.processedAt} />
        </Panel>

        <Panel title="Worker State">
          <KeyValue label="Crawl active" value={status?.crawlActive ? 'yes' : 'no'} />
        </Panel>

        <Panel title="Recent Errors" wide>
          {status && status.recentErrors.length > 0 ? (
            <div className="error-list">
              {status.recentErrors.map((item, index) => (
                <article className="error-row" key={`${item.kind}-${item.player}-${item.name ?? ''}-${index}`}>
                  <div>
                    <span className="error-kind">{item.kind}</span>
                    <strong>{item.player || 'unknown'}</strong>
                    {item.name && <span>{item.name}</span>}
                  </div>
                  <p>{item.message}</p>
                  <time>{item.at ?? '-'}</time>
                </article>
              ))}
            </div>
          ) : (
            <p className="empty">No recorded errors.</p>
          )}
        </Panel>
      </section>
    </main>
  );
}

function Metric({ label, value, tone = 'neutral' }: { label: string; value: number | string; tone?: 'neutral' | 'warn' | 'bad' }) {
  return (
    <div className={`metric metric--${tone}`}>
      <span>{label}</span>
      <strong>{typeof value === 'number' ? value.toLocaleString() : value}</strong>
    </div>
  );
}

function Panel({ title, children, wide = false }: { title: string; children: ReactNode; wide?: boolean }) {
  return (
    <section className={wide ? 'panel panel--wide' : 'panel'}>
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function KeyValue({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="key-value">
      <span>{label}</span>
      <strong>{value ?? '-'}</strong>
    </div>
  );
}

function statusHealth(status: CrawlStatus | null): { label: string; tone: 'ok' | 'warn' | 'bad' } {
  if (!status) return { label: 'Unknown', tone: 'warn' };
  if (status.rawFiles.fetchFailed > 0 || status.rawFiles.processFailed > 0) {
    return { label: 'Needs attention', tone: 'bad' };
  }
  if (status.crawlActive) return { label: 'Crawling', tone: 'ok' };
  if (status.rawFiles.processPending > 0) {
    return { label: 'Processing backlog', tone: 'warn' };
  }
  return { label: 'Healthy', tone: 'ok' };
}

function errorMessage(reason: unknown, fallback: string) {
  return reason instanceof Error ? reason.message : fallback;
}

function isAbortError(reason: unknown) {
  return reason instanceof DOMException && reason.name === 'AbortError';
}

function formatNumber(value?: number | null) {
  return value == null ? '-' : value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function formatRate(value?: number | null) {
  return value == null ? '-' : value.toLocaleString(undefined, { maximumFractionDigits: 3 });
}

function formatDuration(value?: number | null) {
  if (value == null) return '-';
  if (value < 1) return `${Math.round(value * 1000)}ms`;
  return `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}s`;
}
