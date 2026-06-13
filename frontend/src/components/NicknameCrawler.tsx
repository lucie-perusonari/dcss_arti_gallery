import { useEffect, useState, type FormEvent } from 'react';

type NicknameCrawlerProps = {
  activePlayer: string;
  artifactCount: number;
  loading: boolean;
  onPlayerChange: (player: string) => void;
  onClearPlayer: () => void;
};

export function NicknameCrawler({ activePlayer, artifactCount, loading, onPlayerChange, onClearPlayer }: NicknameCrawlerProps) {
  const [nickname, setNickname] = useState(activePlayer || 'wiiwiwi');
  const [message, setMessage] = useState(`Load stored artifacts for wiiwiwi.`);
  const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

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
    onPlayerChange(nextNickname);
  };

  return (
    <form className="nickname-crawl" onSubmit={submitNickname}>
      <label className="search-field nickname-crawl__field">
        <span>Player</span>
        <input
          value={nickname}
          onChange={(event) => setNickname(event.target.value)}
          placeholder="nickname"
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
  );
}
