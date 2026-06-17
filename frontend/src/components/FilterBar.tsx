import type { ArtifactFilters, ArtifactType } from '../types/artifact';

type FilterBarProps = {
  filters: ArtifactFilters;
  types: ArtifactType[];
  slots: string[];
  onChange: (filters: ArtifactFilters) => void;
};

const typeLabels: Record<ArtifactType, string> = {
  weapon: 'Weapon',
  armour: 'Armour',
  jewellery: 'Jewellery',
  talisman: 'Talisman',
  staff: 'Staff',
  misc: 'Misc',
};

export function FilterBar({ filters, types, slots, onChange }: FilterBarProps) {
  const subtypeFilterLabel =
    filters.type === 'weapon'
      ? 'Weapon type filter'
      : filters.type === 'talisman'
        ? 'Talisman tier filter'
        : 'Artifact slot filter';

  return (
    <div className="filter-bar">
      <label className="search-field">
        <span>Search</span>
        <input
          value={filters.search}
          onChange={(event) => onChange({ ...filters, search: event.target.value })}
          placeholder="name, item, property"
        />
      </label>

      <div className="segmented" aria-label="Artifact type filter">
        {types.map((type) => (
          <button
            className={filters.type === type ? 'is-active' : ''}
            key={type}
            type="button"
            onClick={() => onChange({ ...filters, type, slot: 'all' })}
          >
            {typeLabels[type]}
          </button>
        ))}
      </div>

      {filters.type !== 'all' && slots.length > 1 && (
        <div className="segmented segmented--secondary" aria-label={subtypeFilterLabel}>
          {slots.map((slot) => (
            <button
              className={filters.slot === slot ? 'is-active' : ''}
              key={slot}
              type="button"
              onClick={() => onChange({ ...filters, slot })}
            >
              {slotLabel(slot, filters.type)}
            </button>
          ))}
        </div>
      )}

      <div
        className="segmented segmented--secondary filter-bar__date-filter"
        aria-label="Game date filter"
      >
        <button
          className={filters.timeRange === '30d' ? 'is-active' : ''}
          type="button"
          onClick={() => onChange({ ...filters, timeRange: '30d' })}
        >
          Recent 30d
        </button>
        <button
          className={filters.timeRange === 'all' ? 'is-active' : ''}
          type="button"
          onClick={() => onChange({ ...filters, timeRange: 'all' })}
        >
          All time
        </button>
      </div>
    </div>
  );
}

function slotLabel(slot: string, type: ArtifactFilters['type']) {
  if (slot === 'all') {
    if (type === 'weapon') return 'All weapons';
    if (type === 'armour') return 'All armour';
    if (type === 'jewellery') return 'All jewellery';
    if (type === 'talisman') return 'All talismans';
    return 'All';
  }
  if (type === 'weapon') return weaponCategoryLabel(slot);
  if (type === 'jewellery') return jewellerySlotLabel(slot);
  if (type === 'talisman') return talismanTierLabel(slot);
  return slot;
}

function jewellerySlotLabel(slot: string) {
  const labels: Record<string, string> = {
    ring: 'Ring',
    amulet: 'Amulet',
  };
  return labels[slot] ?? slot;
}

function weaponCategoryLabel(slot: string) {
  const labels: Record<string, string> = {
    'short blades': 'Short blades',
    'long blades': 'Long blades',
    axes: 'Axes',
    'maces & flails': 'Maces & flails',
    polearms: 'Polearms',
    staves: 'Staves',
    ranged: 'Ranged',
    'other weapons': 'Other weapons',
  };
  return labels[slot] ?? slot;
}

function talismanTierLabel(slot: string) {
  const labels: Record<string, string> = {
    'tier 1 talismans': 'Tier 1',
    'tier 2 talismans': 'Tier 2',
    'tier 3 talismans': 'Tier 3',
    'tier 4 talismans': 'Tier 4',
    'tier 5 talismans': 'Tier 5',
    'other talismans': 'Other',
  };
  return labels[slot] ?? slot;
}
