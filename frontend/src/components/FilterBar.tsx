import type { ArtifactFilters, ArtifactType } from '../types/artifact';

type FilterBarProps = {
  filters: ArtifactFilters;
  types: Array<ArtifactType | 'all'>;
  slots: string[];
  onChange: (filters: ArtifactFilters) => void;
};

const typeLabels: Record<ArtifactType | 'all', string> = {
  all: 'All',
  weapon: 'Weapon',
  armour: 'Armour',
  jewellery: 'Jewellery',
  talisman: 'Talisman',
  staff: 'Staff',
  misc: 'Misc',
};

export function FilterBar({ filters, types, slots, onChange }: FilterBarProps) {
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
        <div className="segmented segmented--secondary" aria-label="Artifact slot filter">
          {slots.map((slot) => (
            <button
              className={filters.slot === slot ? 'is-active' : ''}
              key={slot}
              type="button"
              onClick={() => onChange({ ...filters, slot })}
            >
              {slotLabel(slot)}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function slotLabel(slot: string) {
  if (slot === 'all') return 'All slots';
  return slot;
}
