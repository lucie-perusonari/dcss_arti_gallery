import { useEffect, useRef } from 'react';
import type { Artifact } from '../types/artifact';
import { displayTileForArtifact } from '../tiles';

type DcssItemDescriptionProps = {
  artifact: Artifact;
};

export function DcssItemDescription({ artifact }: DcssItemDescriptionProps) {
  const title = `${artifact.name.replace(/\.$/, '')}.`;
  const description = itemDescriptionBody(artifact);
  const stashPrefixes = stashSearchPrefixes(artifact);
  const menuPrefixes = menuColouringPrefixes(artifact);
  const tile = displayTileForArtifact(artifact);

  return (
    <div className="describe-item" role="dialog" aria-label={`${artifact.name} description`}>
      <div className="header">
        <TileCanvas src={tile} />
        <span className="describe-item__title">{title}</span>
      </div>

      <div className="body fg7" tabIndex={0}>
        {description}
        <div className="describe-item__prefixes">
          <div>
            <span className="fg7">Stash search prefixes: </span>
            <span>{stashPrefixes}</span>
          </div>
          <div>
            <span className="fg7">Menu/colouring prefixes: </span>
            <span>{menuPrefixes}</span>
          </div>
        </div>
      </div>

      {artifact.source.url ? (
        <div className="actions fg11">
          <a
            href={artifact.source.url}
            target="_blank"
            rel="noreferrer"
            data-source-link
            aria-label={`Open original morgue for ${artifact.name}`}
          >
            View original morgue
          </a>
          .
        </div>
      ) : null}
      <div className="describe-item__discovery fg7">
        {discoveryText(artifact)}
      </div>
    </div>
  );
}

function itemDescriptionBody(artifact: Artifact) {
  const description = artifact.dcssDescription;
  const lines = description.split('\n');
  const firstContentIndex = lines.findIndex((line) => line.trim());
  if (firstContentIndex === -1) return '';

  const firstLine = lines[firstContentIndex].trim().replace(/\.$/, '');
  const title = artifact.name.trim().replace(/\.$/, '');
  if (firstLine === title || firstLine.startsWith(`${title} `)) {
    return lines.slice(firstContentIndex + 1).join('\n').trim();
  }

  return description.trim();
}

function stashSearchPrefixes(artifact: Artifact) {
  const prefixes = ['{inventory}', '{artefact}', '{artifact}'];
  if (artifact.type === 'armour') {
    prefixes.push('{armour}');
    if (artifact.armourSubtype) prefixes.push(`{${artifact.armourSubtype}}`);
    if (artifact.subtype) prefixes.push(`{${artifact.subtype}}`);
  } else if (artifact.type === 'weapon') {
    prefixes.push('{weapon}');
    if (artifact.subtype) prefixes.push(`{${artifact.subtype}}`);
  } else if (artifact.type === 'jewellery') {
    prefixes.push('{jewellery}');
    if (artifact.subtype) prefixes.push(`{${artifact.subtype}}`);
  } else if (artifact.subtype) {
    prefixes.push(`{${artifact.subtype}}`);
  }
  return Array.from(new Set(prefixes)).join(' ');
}

function menuColouringPrefixes(artifact: Artifact) {
  const typeName = artifact.type === 'jewellery' ? 'jewellery' : artifact.type;
  return `identified artefact ${typeName}`;
}

function discoveryText(artifact: Artifact) {
  const parts = [];
  if (artifact.discovery.version) {
    parts.push(`Version ${artifact.discovery.version}`);
  }
  const datetime = formattedDiscoveryDatetime(artifact.discovery.datetime);
  if (datetime) {
    parts.push(`Found ${datetime}`);
  }
  return parts.join(' / ');
}

function formattedDiscoveryDatetime(value?: string | null) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toISOString().replace('.000Z', 'Z');
}

function TileCanvas({ src }: { src: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const context = canvas.getContext('2d');
    if (!context) return;

    const image = new Image();
    image.onload = () => {
      context.imageSmoothingEnabled = false;
      context.clearRect(0, 0, canvas.width, canvas.height);
      context.drawImage(image, 0, 0, 64, 64);
    };
    image.src = src;
  }, [src]);

  return <canvas className="glyph-mode-hidden" ref={canvasRef} width={64} height={64} aria-hidden="true" />;
}
