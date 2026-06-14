import { memo } from 'react';
import type { Artifact } from '../types/artifact';
import { displayTileForArtifact } from '../tiles';

type ArtifactCardProps = {
  artifact: Artifact;
  selected: boolean;
  onSelect: (artifact: Artifact) => void;
};

export const ArtifactCard = memo(function ArtifactCard({ artifact, selected, onSelect }: ArtifactCardProps) {
  const tile = displayTileForArtifact(artifact);

  return (
    <button
      className={`artifact-card ${selected ? 'is-selected' : ''}`}
      type="button"
      onClick={() => onSelect(artifact)}
      aria-pressed={selected}
    >
      <span className="tile-frame">
        <img src={tile} alt="" />
      </span>
      <span className="artifact-card__body">
        <span className="artifact-card__title">{artifact.name}</span>
        <span className="artifact-card__meta">
          {artifact.type} / {artifact.armourSubtype ?? artifact.subtype}
        </span>
        <span className="token-row">
          {artifact.allAttributes.map((token) => (
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
