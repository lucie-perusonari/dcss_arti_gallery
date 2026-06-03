import { DcssItemDescription } from './DcssItemDescription';
import type { Artifact } from '../types/artifact';

type ArtifactDetailProps = {
  artifact: Artifact;
};

export function ArtifactDetail({ artifact }: ArtifactDetailProps) {
  return (
    <div className="ui-popup ui-popup--embedded artifact-detail-popup">
      <div className="ui-popup-outer">
        <div className="ui-popup-inner">
          <DcssItemDescription artifact={artifact} />
        </div>
      </div>
    </div>
  );
}
