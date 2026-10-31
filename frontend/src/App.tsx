import { RepositoryPanel } from "./components/repository/RepositoryPanel";
import { Architecture } from "./pages/Architecture";
import { useRepository } from "./hooks/useRepository";
export default function App() {
  const repository = useRepository();
  return (
    <div className="workspace">
      <RepositoryPanel
        history={repository.history}
        selected={repository.selected}
        job={repository.job}
        busy={repository.busy}
        onGithub={repository.github}
        onZip={repository.zip}
        onCancel={repository.cancel}
        onSelect={repository.select}
      />
      <Architecture
        key={repository.selected + ":" + repository.viewRevision}
        selected={repository.selected}
        summary={repository.summary}
        error={repository.error}
        onDismiss={() => repository.setError("")}
        onError={repository.setError}
      />
    </div>
  );
}
