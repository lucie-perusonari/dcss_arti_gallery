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
    slot: params.get('slot') ?? 'all',
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
        const visibleItems = artifactsMatchingSlot(items, filters.slot);
        setSelectedId((current) => {
          if (visibleItems.length === 0) return null;
          return current && visibleItems.some((item) => item.id === current) ? current : visibleItems[0].id;
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

  const slotOptions = useMemo(() => slotOptionsForArtifacts(artifacts, filters.type), [artifacts, filters.type]);
  const displayedArtifacts = useMemo(() => artifactsMatchingSlot(artifacts, filters.slot), [artifacts, filters.slot]);
  const selectedArtifact = useMemo(
    () => displayedArtifacts.find((artifact) => artifact.id === selectedId) ?? displayedArtifacts[0] ?? null,
    [displayedArtifacts, selectedId],
  );

  const applyPlayerArtifacts = (items: Artifact[] | undefined) => {
    const nextItems = items ?? [];
    setArtifacts(nextItems);
    const visibleItems = artifactsMatchingSlot(nextItems, filters.slot);
    setSelectedId(visibleItems[0]?.id ?? null);
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
            <span className="count-pill">{displayedArtifacts.length}</span>
          </div>

          <NicknameCrawler onArtifactsLoaded={applyPlayerArtifacts} />

          <FilterBar filters={filters} types={types} slots={slotOptions} onChange={setFilters} />

          <div className="list-area">
            {loading && <div className="empty-state">Loading artifacts...</div>}
            {error && <div className="empty-state empty-state--error">{error}</div>}
            {!loading && !error && displayedArtifacts.length === 0 && <div className="empty-state">No matching artifacts.</div>}
            {!loading &&
              !error &&
              displayedArtifacts.map((artifact) => (
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

function slotOptionsForArtifacts(artifacts: Artifact[], type: ArtifactFilters['type']) {
  if (type === 'all') return ['all'];
  const slots = new Set<string>();
  artifacts.forEach((artifact) => {
    if (artifact.type !== type) return;
    const slot = slotForArtifact(artifact);
    if (slot) slots.add(slot);
  });
  return ['all', ...Array.from(slots).sort()];
}

function artifactsMatchingSlot(artifacts: Artifact[], slot: string) {
  if (slot === 'all') return artifacts;
  return artifacts.filter((artifact) => slotForArtifact(artifact) === slot);
}

function slotForArtifact(artifact: Artifact) {
  if (artifact.type === 'weapon') return artifact.weaponSubtype ?? artifact.subtype;
  if (artifact.type === 'armour') return artifact.armourSlot ?? artifact.subtype;
  if (artifact.type === 'jewellery') return artifact.jewellerySlot ?? artifact.subtype;
  if (artifact.type === 'staff') return artifact.subtype;
  return artifact.subtype;
}
