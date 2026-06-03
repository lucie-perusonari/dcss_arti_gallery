import type { ArtifactFilters, ArtifactType } from '../types/artifact';

type FilterBarProps = {
  filters: ArtifactFilters;
  types: Array<ArtifactType | 'all'>;
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

export function FilterBar({ filters, types, onChange }: FilterBarProps) {
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
            onClick={() => onChange({ ...filters, type })}
          >
            {typeLabels[type]}
          </button>
        ))}
      </div>
    </div>
  );
}
