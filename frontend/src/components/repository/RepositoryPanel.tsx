import { useState } from "react";
import type { Analysis, Job } from "../../../../shared/contracts/analysis";
type Props = {
  history: Analysis[];
  selected: string;
  job: Job | null;
  busy: boolean;
  onGithub: (url: string) => void;
  onZip: (file: File) => void;
  onCancel: () => void;
  onSelect: (id: string) => void;
  onDelete: (id: string) => Promise<void>;
};
export function RepositoryPanel({
  history,
  selected,
  job,
  busy,
  onGithub,
  onZip,
  onCancel,
  onSelect,
  onDelete,
}: Props) {
  const [url, setUrl] = useState("");
  const [confirmDelete, setConfirmDelete] = useState("");
  const [deleting, setDeleting] = useState(false);
  return (
    <aside className="navigation">
      <div className="brand">
        RI<span>REPO INTELLIGENCE</span>
      </div>
      <h1>Architecture from evidence.</h1>
      <p>TypeScript & JavaScript · static analysis</p>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          onGithub(url);
        }}
      >
        <label htmlFor="github-url">Public GitHub repository</label>
        <input
          id="github-url"
          required
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://github.com/owner/repo"
        />
        <button disabled={busy} type="submit">
          Analyze repository
        </button>
      </form>
      <label className="upload">
        Or upload a ZIP
        <input
          aria-label="Repository ZIP"
          type="file"
          accept=".zip"
          disabled={busy}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) onZip(file);
            e.target.value = "";
          }}
        />
      </label>
      {job && (
        <div className="job" aria-live="polite">
          <strong>{job.phase}</strong>
          <progress max="100" value={job.progress} />
          <small>
            {job.status} · {job.progress}%
          </small>
          {busy && <button onClick={() => onCancel()}>Cancel</button>}
        </div>
      )}
      <h3>Saved analyses</h3>
      <div className="history">
        {!history.length && <p>No saved snapshots yet.</p>}
        {history.map((s) => (
          <div key={s.snapshot_id} className="history-item">
            <button
              className={s.snapshot_id === selected ? "active" : ""}
              onClick={() => {
                onSelect(s.snapshot_id);
              }}
            >
              <strong>{s.repository}</strong>
              <small>
                {new Date(s.created_at).toLocaleString()}
                <br />
                {s.snapshot_id.slice(0, 12)}
              </small>
            </button>
            {confirmDelete === s.snapshot_id ? (
              <div className="scan-delete-confirm">
                <p>
                  Delete this saved scan? This cannot be undone. Your repository
                  is not affected.
                </p>
                <button
                  disabled={deleting || busy}
                  onClick={async () => {
                    setDeleting(true);
                    try {
                      await onDelete(s.snapshot_id);
                      setConfirmDelete("");
                    } catch {
                      /* Error shown by parent. */
                    } finally {
                      setDeleting(false);
                    }
                  }}
                >
                  {deleting ? "Deleting…" : "Confirm delete"}
                </button>
                <button
                  disabled={deleting}
                  onClick={() => setConfirmDelete("")}
                >
                  Keep scan
                </button>
              </div>
            ) : (
              <button
                className="delete-scan"
                aria-label={`Delete scan ${s.snapshot_id.slice(0, 12)}`}
                disabled={busy || deleting}
                onClick={() => setConfirmDelete(s.snapshot_id)}
              >
                Delete scan
              </button>
            )}
          </div>
        ))}
      </div>
      <footer>
        Source is parsed locally. Target scripts and builds are never run.
      </footer>
    </aside>
  );
}
