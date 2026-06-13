import type { ReactNode } from 'react';

type WebtilesShellProps = {
  children: ReactNode;
};

export function WebtilesShell({ children }: WebtilesShellProps) {
  return (
    <div className="webtiles-shell">
      <header className="topbar">
        <div>
          <span className="brand-mark">DCSS</span>
          <span className="topbar__title">Artifact Gallery</span>
        </div>
        <nav aria-label="Gallery status">
          <span className="topbar__status">archive api</span>
          <span className="topbar__status">webtiles style</span>
          <a className="topbar__github" href="https://github.com/lucie-perusonari/dcss_arti_gallery" target="_blank" rel="noreferrer">
            GitHub
          </a>
        </nav>
      </header>
      {children}
    </div>
  );
}
