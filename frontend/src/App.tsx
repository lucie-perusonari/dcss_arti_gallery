import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { artifactApi } from "./api/artifacts";
import { ArtifactCard } from "./components/ArtifactCard";
import { ArtifactDetail } from "./components/ArtifactDetail";
import { FilterBar } from "./components/FilterBar";
import { NicknameCrawler } from "./components/NicknameCrawler";
import { WebtilesShell } from "./components/WebtilesShell";
import type {
  Artifact,
  ArtifactFilters,
  ArtifactFiltersMetadata,
  ArtifactType,
} from "./types/artifact";

const artifactTypes: ArtifactType[] = [
  "weapon",
  "armour",
  "jewellery",
  "staff",
  "talisman",
];
const weaponCategoryOrder = [
  "short blades",
  "long blades",
  "axes",
  "maces & flails",
  "polearms",
  "staves",
  "ranged",
  "other weapons",
];
const weaponCategories: Record<string, string> = {
  arbalest: "ranged",
  athame: "short blades",
  bardiche: "polearms",
  battleaxe: "axes",
  "broad axe": "axes",
  club: "maces & flails",
  dagger: "short blades",
  "demon blade": "long blades",
  "demon trident": "polearms",
  "demon whip": "maces & flails",
  "dire flail": "maces & flails",
  "double sword": "long blades",
  "eudemon blade": "long blades",
  eveningstar: "maces & flails",
  "executioner's axe": "axes",
  falchion: "long blades",
  flail: "maces & flails",
  "giant club": "maces & flails",
  "giant spiked club": "maces & flails",
  glaive: "polearms",
  "great mace": "maces & flails",
  "great sword": "long blades",
  halberd: "polearms",
  hammer: "maces & flails",
  "hand axe": "axes",
  "hand cannon": "ranged",
  lajatang: "staves",
  "long sword": "long blades",
  longbow: "ranged",
  mace: "maces & flails",
  morningstar: "maces & flails",
  orcbow: "ranged",
  partisan: "polearms",
  quarterstaff: "staves",
  "quick blade": "short blades",
  rapier: "short blades",
  "sacred scourge": "maces & flails",
  scimitar: "long blades",
  scythe: "polearms",
  "short sword": "short blades",
  shortbow: "ranged",
  sling: "ranged",
  spear: "polearms",
  staff: "staves",
  trident: "polearms",
  "triple crossbow": "ranged",
  "triple sword": "long blades",
  trishula: "polearms",
  "war axe": "axes",
  whip: "maces & flails",
};

const talismanTierOrder = [
  "tier 1 talismans",
  "tier 2 talismans",
  "tier 3 talismans",
  "tier 4 talismans",
  "tier 5 talismans",
  "other talismans",
];

const talismanTiers: Record<string, string> = {
  "beast talisman": "tier 1 talismans",
  "inkwell talisman": "tier 1 talismans",
  "quill talisman": "tier 1 talismans",
  "flux talisman": "tier 2 talismans",
  "maw talisman": "tier 2 talismans",
  "medusa talisman": "tier 2 talismans",
  "protean talisman": "tier 2 talismans",
  "rimehorn talisman": "tier 2 talismans",
  "scarab talisman": "tier 2 talismans",
  "serpent talisman": "tier 2 talismans",
  "spore talisman": "tier 2 talismans",
  "blade talisman": "tier 3 talismans",
  "eel talisman": "tier 3 talismans",
  "fortress talisman": "tier 3 talismans",
  "lupine talisman": "tier 3 talismans",
  "spider talisman": "tier 3 talismans",
  "wellspring talisman": "tier 3 talismans",
  "dragon-blood talisman": "tier 4 talismans",
  "dragon-coil talisman": "tier 4 talismans",
  "granite talisman": "tier 4 talismans",
  "hive talisman": "tier 4 talismans",
  "riddle talisman": "tier 4 talismans",
  "sanguine talisman": "tier 4 talismans",
  "sphinx talisman": "tier 4 talismans",
  "statue talisman": "tier 4 talismans",
  "vampire talisman": "tier 4 talismans",
  "storm talisman": "tier 5 talismans",
  "talisman of death": "tier 5 talismans",
};

const fallbackFiltersMetadata: ArtifactFiltersMetadata = {
  types: artifactTypes,
  displayCategories: {},
};

const getInitialFilters = (): ArtifactFilters => {
  const params = new URLSearchParams(window.location.search);
  const type = params.get("type");

  return {
    search: params.get("search") ?? "",
    type: artifactTypes.includes(type as ArtifactType)
      ? (type as ArtifactType)
      : "weapon",
    slot: params.get("slot") ?? "all",
    player: params.get("player") ?? "",
    timeRange: params.get("since") === "all" ? "all" : "30d",
    sort: params.get("sort") === "score" ? "score" : "recent",
  };
};

const getInitialSelectedId = () =>
  new URLSearchParams(window.location.search).get("selected");

export function App() {
  const listRef = useRef<HTMLDivElement>(null);
  const [filters, setFilters] = useState<ArtifactFilters>(() =>
    getInitialFilters(),
  );
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [filtersMetadata, setFiltersMetadata] = useState<ArtifactFiltersMetadata>(
    fallbackFiltersMetadata,
  );
  const [selectedId, setSelectedId] = useState<string | null>(() =>
    getInitialSelectedId(),
  );
  const [mobileDetailOpen, setMobileDetailOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const apiFilters = useMemo<ArtifactFilters>(
    () => ({
      search: filters.search,
      type: filters.type,
      slot: "all",
      player: filters.player,
      timeRange: filters.timeRange,
      sort: filters.sort,
    }),
    [
      filters.player,
      filters.search,
      filters.sort,
      filters.timeRange,
      filters.type,
    ],
  );

  useEffect(() => {
    artifactApi
      .listFilters()
      .then((metadata) =>
        setFiltersMetadata({
          ...metadata,
          types: artifactTypes,
        }),
      )
      .catch(() => setFiltersMetadata(fallbackFiltersMetadata));
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);

    artifactApi
      .listArtifacts(apiFilters)
      .then((items) => {
        if (!active) return;
        setArtifacts(items);
      })
      .catch((reason: unknown) => {
        if (!active) return;
        setError(
          reason instanceof Error ? reason.message : "Failed to load artifacts",
        );
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [apiFilters]);

  const slotOptions = useMemo(
    () => slotOptionsForMetadata(filtersMetadata, filters.type),
    [filters.type, filtersMetadata],
  );
  const displayedArtifacts = useMemo(
    () => artifactsMatchingFilters(artifacts, filters),
    [artifacts, filters],
  );

  useEffect(() => {
    setSelectedId((current) => {
      if (displayedArtifacts.length === 0) return null;
      return current && displayedArtifacts.some((item) => item.id === current)
        ? current
        : displayedArtifacts[0].id;
    });
  }, [displayedArtifacts]);

  const selectedArtifact = useMemo(
    () =>
      displayedArtifacts.find((artifact) => artifact.id === selectedId) ??
      displayedArtifacts[0] ??
      null,
    [displayedArtifacts, selectedId],
  );
  const rowVirtualizer = useVirtualizer({
    count: displayedArtifacts.length,
    estimateSize: () => 42,
    getItemKey: (index) => displayedArtifacts[index]?.id ?? index,
    getScrollElement: () => listRef.current,
    overscan: 8,
  });

  useEffect(() => {
    rowVirtualizer.scrollToOffset(0);
  }, [
    filters.player,
    filters.search,
    filters.slot,
    filters.sort,
    filters.timeRange,
    filters.type,
    rowVirtualizer,
  ]);

  const applyPlayerFilter = (player: string) => {
    setFilters((current) => ({ ...current, player }));
  };

  const clearPlayerFilter = () => {
    setFilters((current) => ({ ...current, player: "" }));
  };

  const handleSelectArtifact = useCallback((artifact: Artifact) => {
    setSelectedId(artifact.id);
    setMobileDetailOpen(true);
  }, []);

  const closeMobileDetail = useCallback(() => {
    setMobileDetailOpen(false);
  }, []);

  useEffect(() => {
    if (!selectedArtifact) setMobileDetailOpen(false);
  }, [selectedArtifact]);

  useEffect(() => {
    if (!mobileDetailOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMobileDetailOpen(false);
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mobileDetailOpen]);

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

          <NicknameCrawler
            activePlayer={filters.player}
            artifactCount={artifacts.length}
            loading={loading}
            onPlayerChange={applyPlayerFilter}
            onClearPlayer={clearPlayerFilter}
          />

          <FilterBar
            filters={filters}
            types={artifactTypes}
            slots={slotOptions}
            onChange={setFilters}
          />

          <div className="list-area" ref={listRef}>
            {loading && <div className="empty-state">Loading artifacts...</div>}
            {error && (
              <div className="empty-state empty-state--error">{error}</div>
            )}
            {!loading && !error && displayedArtifacts.length === 0 && (
              <div className="empty-state">No matching artifacts.</div>
            )}
            {!loading && !error && displayedArtifacts.length > 0 && (
              <div
                className="virtual-list"
                style={{ height: `${rowVirtualizer.getTotalSize()}px` }}
              >
                {rowVirtualizer.getVirtualItems().map((virtualRow) => {
                  const artifact = displayedArtifacts[virtualRow.index];

                  return (
                    <div
                      className="virtual-list__row"
                      data-index={virtualRow.index}
                      key={virtualRow.key}
                      ref={rowVirtualizer.measureElement}
                      style={{ transform: `translateY(${virtualRow.start}px)` }}
                    >
                      <ArtifactCard
                        artifact={artifact}
                        selected={artifact.id === selectedArtifact?.id}
                        onSelect={handleSelectArtifact}
                      />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </section>

        <section
          id="ui-stack"
          data-display-mode="tiles"
          aria-label="DCSS item description"
        >
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
        {selectedArtifact && mobileDetailOpen ? (
          <ArtifactDetail
            artifact={selectedArtifact}
            modal
            onClose={closeMobileDetail}
          />
        ) : null}
      </main>
    </WebtilesShell>
  );
}

function slotOptionsForMetadata(
  filtersMetadata: ArtifactFiltersMetadata,
  type: ArtifactFilters["type"],
) {
  if (type === "all") return ["all"];
  const slots = filtersMetadata.displayCategories[type] ?? [];
  if (type === "talisman") return talismanTierOptionsForMetadata(slots);
  const sortedSlots =
    type === "weapon"
      ? [...slots].sort(
          (left, right) =>
            weaponCategoryRank(left) - weaponCategoryRank(right) ||
            left.localeCompare(right),
        )
      : [...slots].sort();
  return ["all", ...sortedSlots];
}

function artifactsMatchingSlot(artifacts: Artifact[], slot: string) {
  if (slot === "all") return artifacts;
  return artifacts.filter((artifact) => slotForArtifact(artifact) === slot);
}

function artifactsMatchingFilters(
  artifacts: Artifact[],
  filters: ArtifactFilters,
) {
  return artifactsMatchingSlot(artifacts, filters.slot);
}

function slotForArtifact(artifact: Artifact) {
  if (artifact.type === "weapon") return weaponCategoryForArtifact(artifact);
  if (artifact.type === "armour")
    return artifact.armourSlot ?? artifact.subtype;
  if (artifact.type === "jewellery") return jewellerySlotForArtifact(artifact);
  if (artifact.type === "staff") return artifact.subtype;
  if (artifact.type === "talisman") return talismanTierForArtifact(artifact);
  return artifact.subtype;
}

function jewellerySlotForArtifact(artifact: Artifact) {
  const jewellerySlot = artifact.jewellerySlot?.trim().toLowerCase();
  const baseItem = artifact.baseItem.trim().toLowerCase();
  const subtype = artifact.subtype.trim().toLowerCase();
  if (
    jewellerySlot === "amulet" ||
    baseItem === "amulet" ||
    subtype.startsWith("amulet of ")
  )
    return "amulet";
  return "ring";
}

function weaponCategoryForArtifact(artifact: Artifact) {
  const subtype = artifact.subtype.trim().toLowerCase();
  const baseItem = artifact.baseItem.trim().toLowerCase();
  if (weaponCategories[subtype]) return weaponCategories[subtype];
  if (weaponCategories[baseItem]) return weaponCategories[baseItem];
  if (subtype.endsWith(" sword") || baseItem.endsWith(" sword"))
    return "long blades";
  return artifact.weaponSubtype === "ranged" ? "ranged" : "other weapons";
}

function weaponCategoryRank(category: string) {
  const index = weaponCategoryOrder.indexOf(category);
  return index === -1 ? weaponCategoryOrder.length : index;
}

function talismanTierOptionsForMetadata(slots: string[]) {
  const tiers = new Set(
    slots
      .filter((slot) => slot !== "all")
      .map((slot) => talismanTierForName(slot) ?? "other talismans"),
  );
  const sortedTiers = talismanTierOrder.filter((tier) => tiers.has(tier));
  return ["all", ...(sortedTiers.length > 0 ? sortedTiers : talismanTierOrder)];
}

function talismanTierForArtifact(artifact: Artifact) {
  return (
    talismanTierForName(artifact.subtype) ??
    talismanTierForName(artifact.baseItem) ??
    "other talismans"
  );
}

function talismanTierForName(name: string) {
  const normalized = name.trim().toLowerCase();
  if (talismanTierOrder.includes(normalized)) return normalized;
  return talismanTiers[normalized];
}
