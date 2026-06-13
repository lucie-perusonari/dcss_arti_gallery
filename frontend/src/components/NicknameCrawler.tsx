import { useEffect, useState, type FormEvent } from 'react';

type NicknameCrawlerProps = {
  activePlayer: string;
  artifactCount: number;
  loading: boolean;
  onPlayerChange: (player: string) => void;
  onClearPlayer: () => void;
};

export function NicknameCrawler({ activePlayer, artifactCount, loading, onPlayerChange, onClearPlayer }: NicknameCrawlerProps) {
  const [nickname, setNickname] = useState(activePlayer);
  const [message, setMessage] = useState('Load stored artifacts for a player.');
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [playerModalOpen, setPlayerModalOpen] = useState(false);

  useEffect(() => {
    if (!activePlayer) {
      setStatus('idle');
      setMessage(`Load stored artifacts for ${nickname.trim() || 'a player'}.`);
      return;
    }

    setNickname(activePlayer);
    setStatus('success');
    setMessage(`Showing ${artifactCount} stored artifacts for ${activePlayer}.`);
  }, [activePlayer, artifactCount]);

  const submitNickname = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextNickname = nickname.trim();

    if (!nextNickname) {
      setStatus('error');
      setMessage('Nickname is required.');
      return;
    }

    setMessage(`Loading stored artifacts for ${nextNickname}...`);
    setPlayerModalOpen(false);
    onPlayerChange(nextNickname);
  };

  const openPlayerModalOnMobile = () => {
    if (!window.matchMedia('(max-width: 900px)').matches) return false;
    setPlayerModalOpen(true);
    return true;
  };

  return (
    <div className="nickname-crawl">
      <form onSubmit={submitNickname}>
        <label className="search-field nickname-crawl__field">
          <span>Player</span>
          <input
            value={nickname}
            onChange={(event) => setNickname(event.target.value)}
            onPointerDown={(event) => {
              if (!openPlayerModalOnMobile()) return;
              event.preventDefault();
            }}
            onFocus={(event) => {
              if (!openPlayerModalOnMobile()) return;
              event.currentTarget.blur();
            }}
            placeholder="player"
            autoComplete="nickname"
            disabled={loading}
          />
        </label>

        <div className="nickname-crawl__row">
          <button type="submit" disabled={loading}>
            {loading && activePlayer ? 'Loading' : 'Load'}
          </button>
          {activePlayer && (
            <button type="button" className="nickname-crawl__clear" disabled={loading} onClick={onClearPlayer}>
              All
            </button>
          )}
          <span className={`nickname-crawl__status nickname-crawl__status--${loading ? 'submitting' : status}`}>{message}</span>
        </div>
      </form>

      {playerModalOpen && (
        <div className="ui-popup ui-popup--modal nickname-crawl-modal" role="presentation">
          <button
            type="button"
            className="ui-popup-overlay"
            aria-label="Close player input"
            onClick={() => setPlayerModalOpen(false)}
          />
          <div className="ui-popup-outer">
            <div className="ui-popup-inner">
              <form className="nickname-crawl-modal__form" role="dialog" aria-modal="true" aria-label="Player input" onSubmit={submitNickname}>
                <label className="search-field nickname-crawl__field">
                  <span>Player</span>
                  <input
                    autoFocus
                    value={nickname}
                    onChange={(event) => setNickname(event.target.value)}
                    placeholder="player"
                    autoComplete="nickname"
                    disabled={loading}
                  />
                </label>
                <div className="nickname-crawl__row">
                  <button type="submit" disabled={loading}>
                    {loading && activePlayer ? 'Loading' : 'Load'}
                  </button>
                  <button type="button" disabled={loading} onClick={() => setPlayerModalOpen(false)}>
                    Cancel
                  </button>
                  {activePlayer && (
                    <button
                      type="button"
                      className="nickname-crawl__clear"
                      disabled={loading}
                      onClick={() => {
                        setPlayerModalOpen(false);
                        onClearPlayer();
                      }}
                    >
                      All
                    </button>
                  )}
                </div>
                <span className={`nickname-crawl__status nickname-crawl__status--${loading ? 'submitting' : status}`}>{message}</span>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
