import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { artifactApi } from "./api/artifacts";
import { ArtifactCard } from "./components/ArtifactCard";
import { ArtifactDetail } from "./components/ArtifactDetail";
import { FilterBar } from "./components/FilterBar";
import { NicknameCrawler } from "./components/NicknameCrawler";
import { WebtilesShell } from "./components/WebtilesShell";
import type { Artifact, ArtifactFilters, ArtifactType } from "./types/artifact";

const artifactTypes: Array<ArtifactType | "all"> = [
  "all",
  "weapon",
  "armour",
  "jewellery",
  "talisman",
  "staff",
  "misc",
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
const luxuryMinimumEnchantment = 8;
const luxuryWeaponMinimumScore = 45;
const luxuryArmourMinimumScore = 55;

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

const luxuryWeaponBases = new Set([
  "arbalest",
  "bardiche",
  "battleaxe",
  "broad axe",
  "demon blade",
  "demon trident",
  "demon whip",
  "double sword",
  "eveningstar",
  "eudemon blade",
  "executioner's axe",
  "glaive",
  "great mace",
  "great sword",
  "hand cannon",
  "lajatang",
  "longbow",
  "morningstar",
  "orcbow",
  "partisan",
  "quarterstaff",
  "quick blade",
  "rapier",
  "sacred scourge",
  "scimitar",
  "trident",
  "triple crossbow",
  "triple sword",
  "war axe",
]);

const luxuryBodyArmourBases = new Set([
  "acid dragon scales",
  "chain mail",
  "crystal plate armour",
  "fire dragon scales",
  "gold dragon scales",
  "golden dragon scales",
  "ice dragon scales",
  "pearl dragon scales",
  "plate armour",
  "quicksilver dragon scales",
  "shadow dragon scales",
  "storm dragon scales",
  "swamp dragon scales",
  "troll leather armour",
]);

const luxuryArmourSlots = new Set(["boots", "cloak", "gloves", "helmet"]);
const luxuryShieldBases = new Set([
  "buckler",
  "kite shield",
  "shield",
  "tower shield",
]);

const getInitialFilters = (): ArtifactFilters => {
  const params = new URLSearchParams(window.location.search);
  const type = params.get("type");

  return {
    search: params.get("search") ?? "",
    type: artifactTypes.includes(type as ArtifactType | "all")
      ? (type as ArtifactType | "all")
      : "all",
    slot: params.get("slot") ?? "all",
    luxuryOnly: params.get("luxury") === "1",
    player: params.get("player") ?? "",
    timeRange: params.get("since") === "all" ? "all" : "30d",
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
  const [types, setTypes] = useState<Array<ArtifactType | "all">>(["all"]);
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
      luxuryOnly: false,
      player: filters.player,
      timeRange: filters.timeRange,
    }),
    [filters.player, filters.search, filters.timeRange, filters.type],
  );

  useEffect(() => {
    artifactApi
      .listTypes()
      .then(setTypes)
      .catch(() => setTypes(["all", "weapon", "armour", "jewellery", "misc"]));
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
    () => slotOptionsForArtifacts(artifacts, filters.type, filters.luxuryOnly),
    [artifacts, filters.type, filters.luxuryOnly],
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
    filters.luxuryOnly,
    filters.player,
    filters.search,
    filters.slot,
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
            types={types}
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

function slotOptionsForArtifacts(
  artifacts: Artifact[],
  type: ArtifactFilters["type"],
  luxuryOnly: boolean,
) {
  if (type === "all") return ["all"];
  const slots = new Set<string>();
  artifacts.forEach((artifact) => {
    if (artifact.type !== type) return;
    if (luxuryOnly && !isLuxuryArtifact(artifact)) return;
    const slot = slotForArtifact(artifact);
    if (slot) slots.add(slot);
  });
  const sortedSlots =
    type === "weapon"
      ? Array.from(slots).sort(
          (left, right) =>
            weaponCategoryRank(left) - weaponCategoryRank(right) ||
            left.localeCompare(right),
        )
      : Array.from(slots).sort();
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
  const slotMatched = artifactsMatchingSlot(artifacts, filters.slot);
  if (!filters.luxuryOnly) return slotMatched;
  return slotMatched.filter(isLuxuryArtifact);
}

function slotForArtifact(artifact: Artifact) {
  if (artifact.type === "weapon") return weaponCategoryForArtifact(artifact);
  if (artifact.type === "armour")
    return artifact.armourSlot ?? artifact.subtype;
  if (artifact.type === "jewellery") return jewellerySlotForArtifact(artifact);
  if (artifact.type === "staff") return artifact.subtype;
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
  return artifact.weaponSubtype === "ranged" ? "ranged" : "other weapons";
}

function weaponCategoryRank(category: string) {
  const index = weaponCategoryOrder.indexOf(category);
  return index === -1 ? weaponCategoryOrder.length : index;
}

function isLuxuryArtifact(artifact: Artifact) {
  if (artifact.type === "weapon") return isLuxuryWeapon(artifact);
  if (artifact.type === "armour") return isLuxuryArmour(artifact);
  return false;
}

function isLuxuryWeapon(artifact: Artifact) {
  return (
    artifactEnchantment(artifact) >= luxuryMinimumEnchantment &&
    luxuryWeaponBases.has(normalizedBaseItem(artifact)) &&
    artifact.score.total >= luxuryWeaponMinimumScore
  );
}

function isLuxuryArmour(artifact: Artifact) {
  const baseItem = normalizedBaseItem(artifact);
  const slot = artifact.armourSlot ?? "";
  if (luxuryArmourSlots.has(slot)) {
    return artifact.score.total >= luxuryArmourMinimumScore;
  }
  if (luxuryShieldBases.has(baseItem)) {
    return artifact.score.total >= luxuryArmourMinimumScore;
  }
  return (
    artifactEnchantment(artifact) >= luxuryMinimumEnchantment &&
    luxuryBodyArmourBases.has(baseItem) &&
    artifact.score.total >= luxuryArmourMinimumScore
  );
}

function artifactEnchantment(artifact: Artifact) {
  const match = artifact.name.match(/(?:^|\s)([+-]\d+)(?=\s)/);
  return match ? Number.parseInt(match[1], 10) : 0;
}

function normalizedBaseItem(artifact: Artifact) {
  return artifact.baseItem.trim().toLowerCase();
}
