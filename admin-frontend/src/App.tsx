import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { fetchCrawlStatus } from './api/status';
import type { CrawlStatus } from './types/status';

const REFRESH_MS = 15_000;

export function App() {
  const [status, setStatus] = useState<CrawlStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    let timer: number | undefined;

    const load = () => {
      fetchCrawlStatus()
        .then((nextStatus) => {
          if (!active) return;
          setStatus(nextStatus);
          setError(null);
          setLastUpdated(new Date().toLocaleString());
        })
        .catch((reason: unknown) => {
          if (!active) return;
          setError(reason instanceof Error ? reason.message : 'Failed to load crawl status');
        })
        .finally(() => {
          if (active) setLoading(false);
        });
    };

    load();
    timer = window.setInterval(load, REFRESH_MS);

    return () => {
      active = false;
      if (timer) window.clearInterval(timer);
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
        {error && <strong>{error}</strong>}
      </section>

      <section className="metric-grid" aria-label="Crawl metrics">
        <Metric label="Artifacts" value={status?.artifactCount ?? 0} />
        <Metric label="Raw files" value={status?.rawFiles.total ?? 0} />
        <Metric label="Fetched raw" value={status?.rawFiles.fetched ?? 0} />
        <Metric label="Pending process" value={status?.rawFiles.processPending ?? 0} tone="warn" />
        <Metric label="Fetch failed" value={status?.rawFiles.fetchFailed ?? 0} tone="bad" />
        <Metric label="Process failed" value={status?.rawFiles.processFailed ?? 0} tone="bad" />
      </section>

      <section className="content-grid">
        <Panel title="Latest Activity">
          <KeyValue label="Fetched" value={status?.latest.fetchedAt} />
          <KeyValue label="Processed" value={status?.latest.processedAt} />
          <KeyValue label="User scanned" value={status?.latest.scannedAt} />
        </Panel>

        <Panel title="Worker State">
          <StatusCounts title="Users" values={status?.crawlUsers ?? {}} />
          <StatusCounts title="Files" values={status?.crawlFiles ?? {}} />
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

function Metric({ label, value, tone = 'neutral' }: { label: string; value: number; tone?: 'neutral' | 'warn' | 'bad' }) {
  return (
    <div className={`metric metric--${tone}`}>
      <span>{label}</span>
      <strong>{value.toLocaleString()}</strong>
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

function StatusCounts({ title, values }: { title: string; values: Record<string, number> }) {
  const entries = Object.entries(values);
  return (
    <div className="status-counts">
      <h3>{title}</h3>
      {entries.length > 0 ? (
        entries.map(([key, value]) => <KeyValue key={key} label={key} value={value.toLocaleString()} />)
      ) : (
        <p className="empty">No records.</p>
      )}
    </div>
  );
}

function statusHealth(status: CrawlStatus | null): { label: string; tone: 'ok' | 'warn' | 'bad' } {
  if (!status) return { label: 'Unknown', tone: 'warn' };
  if (status.rawFiles.fetchFailed > 0 || status.rawFiles.processFailed > 0) {
    return { label: 'Needs attention', tone: 'bad' };
  }
  if (status.rawFiles.processPending > 0) {
    return { label: 'Processing backlog', tone: 'warn' };
  }
  return { label: 'Healthy', tone: 'ok' };
}
