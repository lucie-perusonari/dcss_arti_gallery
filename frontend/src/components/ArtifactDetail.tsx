import { DcssItemDescription } from "./DcssItemDescription";
import type { Artifact } from "../types/artifact";

type ArtifactDetailProps = {
  artifact: Artifact;
  modal?: boolean;
  onClose?: () => void;
};

export function ArtifactDetail({
  artifact,
  modal = false,
  onClose,
}: ArtifactDetailProps) {
  return (
    <div
      className={`ui-popup ${modal ? "ui-popup--modal artifact-detail-modal" : "ui-popup--embedded"} artifact-detail-popup`}
    >
      {modal ? (
        <button
          className="ui-popup-overlay"
          type="button"
          aria-label="Close item description"
          onClick={onClose}
        />
      ) : null}
      <div className="ui-popup-outer">
        {modal ? (
          <button
            className="artifact-detail-popup__close"
            type="button"
            aria-label="Close item description"
            onClick={onClose}
          >
            Close
          </button>
        ) : null}
        <div className="ui-popup-inner">
          <DcssItemDescription artifact={artifact} />
        </div>
      </div>
    </div>
  );
}
