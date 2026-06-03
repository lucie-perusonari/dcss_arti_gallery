import { useState, type FormEvent } from 'react';
import { artifactApi, type PlayerArtifactsResponse } from '../api/artifacts';

type NicknameCrawlerProps = {
  onArtifactsLoaded?: (artifacts: PlayerArtifactsResponse['artifacts']) => void;
};

const playerArtifactMessage = (result: PlayerArtifactsResponse) => {
  if (result.message) return result.message;
  return `Loaded ${result.artifactCount ?? result.artifacts?.length ?? 0} stored artifacts for ${result.nickname}.`;
};

export function NicknameCrawler({ onArtifactsLoaded }: NicknameCrawlerProps) {
  const [nickname, setNickname] = useState('wiiwiwi');
  const [message, setMessage] = useState(`Load stored artifacts for wiiwiwi.`);
  const [status, setStatus] = useState<'idle' | 'submitting' | 'success' | 'error'>('idle');

  const submitNickname = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextNickname = nickname.trim();

    if (!nextNickname) {
      setStatus('error');
      setMessage('Nickname is required.');
      return;
    }

    setStatus('submitting');
    setMessage(`Loading stored artifacts for ${nextNickname}...`);

    try {
      const result = await artifactApi.listPlayerArtifacts({
        nickname: nextNickname,
      });
      if (result.status === 'failed') {
        throw new Error(result.error ?? result.message ?? 'Failed to load stored artifacts.');
      }

      setStatus('success');
      setMessage(playerArtifactMessage(result));
      onArtifactsLoaded?.(result.artifacts ?? []);
    } catch (reason) {
      setStatus('error');
      setMessage(reason instanceof Error ? reason.message : 'Failed to load stored artifacts.');
    }
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
          disabled={status === 'submitting'}
        />
      </label>

      <div className="nickname-crawl__row">
        <button type="submit" disabled={status === 'submitting'}>
          {status === 'submitting' ? 'Loading' : 'Load'}
        </button>
        <span className={`nickname-crawl__status nickname-crawl__status--${status}`}>{message}</span>
      </div>
    </form>
  );
}
