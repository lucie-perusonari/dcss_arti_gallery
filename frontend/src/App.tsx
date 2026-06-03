import { useEffect, useMemo, useState } from 'react';
import { artifactApi } from './api/artifacts';
import { ArtifactCard } from './components/ArtifactCard';
import { ArtifactDetail } from './components/ArtifactDetail';
import { FilterBar } from './components/FilterBar';
import { NicknameCrawler } from './components/NicknameCrawler';
import { WebtilesShell } from './components/WebtilesShell';
import type { Artifact, ArtifactFilters, ArtifactType } from './types/artifact';

const artifactTypes: Array<ArtifactType | 'all'> = ['all', 'weapon', 'armour', 'jewellery', 'talisman', 'staff', 'misc'];

const getInitialFilters = (): ArtifactFilters => {
  const params = new URLSearchParams(window.location.search);
  const type = params.get('type');

  return {
    search: params.get('search') ?? '',
    type: artifactTypes.includes(type as ArtifactType | 'all') ? (type as ArtifactType | 'all') : 'all',
  };
};

const getInitialSelectedId = () => new URLSearchParams(window.location.search).get('selected');

export function App() {
  const [filters, setFilters] = useState<ArtifactFilters>(() => getInitialFilters());
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [types, setTypes] = useState<Array<ArtifactType | 'all'>>(['all']);
  const [selectedId, setSelectedId] = useState<string | null>(() => getInitialSelectedId());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    artifactApi.listTypes().then(setTypes).catch(() => setTypes(['all', 'weapon', 'armour', 'jewellery', 'misc']));
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    artifactApi
      .listArtifacts(filters)
      .then((items) => {
        if (!active) return;
        setArtifacts(items);
        setSelectedId((current) => {
          if (items.length === 0) return null;
          return current && items.some((item) => item.id === current) ? current : items[0].id;
        });
      })
      .catch((reason: unknown) => {
        if (!active) return;
        setError(reason instanceof Error ? reason.message : 'Failed to load artifacts');
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [filters]);

  const selectedArtifact = useMemo(
    () => artifacts.find((artifact) => artifact.id === selectedId) ?? artifacts[0] ?? null,
    [artifacts, selectedId],
  );

  const applyPlayerArtifacts = (items: Artifact[] | undefined) => {
    const nextItems = items ?? [];
    setArtifacts(nextItems);
    setSelectedId(nextItems[0]?.id ?? null);
  };

  return (
    <WebtilesShell>
      <main id="game" className="gallery-layout">
        <section className="inventory-panel" aria-label="Artifact list">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Inventory</p>
              <h1>Randart Browser</h1>
            </div>
            <span className="count-pill">{artifacts.length}</span>
          </div>

          <NicknameCrawler onArtifactsLoaded={applyPlayerArtifacts} />

          <FilterBar filters={filters} types={types} onChange={setFilters} />

          <div className="list-area">
            {loading && <div className="empty-state">Loading artifacts...</div>}
            {error && <div className="empty-state empty-state--error">{error}</div>}
            {!loading && !error && artifacts.length === 0 && <div className="empty-state">No matching artifacts.</div>}
            {!loading &&
              !error &&
              artifacts.map((artifact) => (
                <ArtifactCard
                  artifact={artifact}
                  key={artifact.id}
                  selected={artifact.id === selectedArtifact?.id}
                  onSelect={(nextArtifact) => setSelectedId(nextArtifact.id)}
                />
              ))}
          </div>
        </section>

        <section id="ui-stack" data-display-mode="tiles" aria-label="DCSS item description">
          {selectedArtifact ? (
            <ArtifactDetail artifact={selectedArtifact} />
          ) : (
            <div className="ui-popup ui-popup--embedded centred">
              <div className="ui-popup-outer">
                <div className="ui-popup-inner">
                  <div className="menu_txt">Select an artifact.</div>
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </WebtilesShell>
  );
}
