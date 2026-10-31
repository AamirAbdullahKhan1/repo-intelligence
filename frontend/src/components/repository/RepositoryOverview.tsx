import type { RepositoryOverview as Overview } from "../../../../shared/contracts/analysis";
export function RepositoryOverview({ value }: { value: Overview }) {
  return (
    <section className="repository-overview" aria-label="Repository summary">
      <div className="stack-line">
        <strong>
          {Object.keys(value.languages)
            .filter((n) => !n.includes("inventory"))
            .join(" · ") || "No supported source detected"}
        </strong>
        <span>
          {value.frameworks.join(" · ") ||
            "No framework identified in package manifests"}
        </span>
        <small>
          Frameworks are detected from manifests; adapter coverage varies.
        </small>
        {Object.keys(value.languages).some((n) => n.includes("inventory")) && (
          <small>
            {Object.keys(value.languages)
              .filter((n) => n.includes("inventory"))
              .join(" · ")}
          </small>
        )}
      </div>
      <div className="summary-metrics">
        <div>
          <strong>{value.package_count}</strong>
          <span>packages / source roots</span>
        </div>
        <div>
          <strong>{value.module_count}</strong>
          <span>logical modules</span>
        </div>
        <div>
          <strong>{value.entry_point_count}</strong>
          <span>route entry points</span>
        </div>
        <div>
          <strong>{value.infrastructure_count}</strong>
          <span>infrastructure identities</span>
        </div>
      </div>
      <details className="summary-details">
        <summary>What was detected, and what remains uncertain</summary>
        <div className="summary-columns">
          <div>
            <h3>Applications / packages</h3>
            <p>
              {value.packages.map((p) => p.label).join(", ")}
              {value.packages_truncated
                ? " (first 20; browse all in the explorer)"
                : ""}
            </p>
            <h3>External integrations</h3>
            <p>
              {value.integrations.map((p) => p.label).join(", ") ||
                "None established"}
            </p>
            <small>
              SDK means a client library; its remote destination may be unknown.
              Lists show up to 30 identities; browse all in the explorer.
            </small>
            <h3>Storage declarations</h3>
            <p>
              {value.storage
                .map((p) => `${p.label} (${p.technology})`)
                .join(", ") || "No storage declaration established"}
            </p>
          </div>
          <div>
            <h3>Coverage and confidence</h3>
            <p>
              {value.coverage.parsed_files} source files analyzed from{" "}
              {value.coverage.inventoried_files} inventoried files.{" "}
              {value.coverage.skipped_files} files or directories excluded by
              scope/limits.
            </p>
            <p>
              {value.supported_relationships.toLocaleString()} source-supported
              relationships; {value.unresolved_references.toLocaleString()}{" "}
              references need more context. These include unavailable dependency
              implementations and generated files, rather than only missing
              application connections.
            </p>
            <ul>
              {value.limitations.map((l) => (
                <li key={l}>{l}</li>
              ))}
            </ul>
          </div>
        </div>
      </details>
    </section>
  );
}
