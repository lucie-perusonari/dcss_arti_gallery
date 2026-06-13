import { memo } from 'react';
import type { Artifact } from '../types/artifact';

type ArtifactCardProps = {
  artifact: Artifact;
  selected: boolean;
  onSelect: (artifact: Artifact) => void;
};

export const ArtifactCard = memo(function ArtifactCard({ artifact, selected, onSelect }: ArtifactCardProps) {
  return (
    <button
      className={`artifact-card ${selected ? 'is-selected' : ''}`}
      type="button"
      onClick={() => onSelect(artifact)}
      aria-pressed={selected}
    >
      <span className="tile-frame">
        <img src={artifact.tile} alt="" />
      </span>
      <span className="artifact-card__body">
        <span className="artifact-card__title">{artifact.name}</span>
        <span className="artifact-card__meta">
          {artifact.type} / {artifact.subtype}
        </span>
        <span className="token-row">
          {artifact.randomAttributes.slice(0, 4).map((token) => (
            <span className="token" key={token}>
              {token}
            </span>
          ))}
        </span>
      </span>
      <span className="score-badge">{artifact.score.total}</span>
    </button>
  );
});
