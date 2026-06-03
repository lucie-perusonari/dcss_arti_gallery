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
          <span>archive api</span>
          <span>webtiles style</span>
        </nav>
      </header>
      {children}
    </div>
  );
}
