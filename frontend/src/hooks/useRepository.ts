import { useEffect, useState } from "react";
import type { Analysis, Job } from "../../../shared/contracts/analysis";
import { api } from "../services/analysis";
export function useRepository() {
  const [history, setHistory] = useState<Analysis[]>([]);
  const [selected, setSelected] = useState(
    localStorage.getItem("analysis-id") || "",
  );
  const [summary, setSummary] = useState<Analysis | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [viewRevision, setViewRevision] = useState(0);
  const busy =
    submitting || job?.status === "queued" || job?.status === "running";
  const refresh = () =>
    api
      .history()
      .then(setHistory)
      .catch((e) => setError(e.message));
  useEffect(() => {
    refresh();
    const id = localStorage.getItem("analysis-job");
    if (id)
      api
        .job(id)
        .then(setJob)
        .catch(() => localStorage.removeItem("analysis-job"));
  }, []);
  useEffect(() => {
    if (!job || !["queued", "running"].includes(job.status)) {
      localStorage.removeItem("analysis-job");
      return;
    }
    localStorage.setItem("analysis-job", job.id);
    let active = true;
    const timer = setTimeout(
      () =>
        api
          .job(job.id)
          .then((value) => {
            if (!active) return;
            setJob(value);
            if (value.status === "complete" && value.snapshot_id) {
              setSelected(value.snapshot_id);
              setViewRevision((v) => v + 1);
              refresh();
            }
            if (value.status === "failed")
              setError(value.error || "Analysis failed");
          })
          .catch((e) => {
            if (active) {
              setError(e.message);
              setJob({ ...job });
            }
          }),
      1000,
    );
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [job]);
  useEffect(() => {
    let active = true;
    setSummary(null);
    if (selected) {
      localStorage.setItem("analysis-id", selected);
      api
        .analysis(selected)
        .then((s) => {
          if (active) setSummary(s);
        })
        .catch((e) => {
          if (active) setError(e.message);
        });
    }
    return () => {
      active = false;
    };
  }, [selected]);
  async function submit(action: () => Promise<Job>) {
    setSubmitting(true);
    setError("");
    try {
      setJob(await action());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSubmitting(false);
    }
  }
  const select = (id: string) => {
    setError("");
    setSelected(id);
    setViewRevision((v) => v + 1);
  };
  const cancel = () => {
    if (job)
      api
        .cancel(job.id)
        .then(setJob)
        .catch((e) => setError(e.message));
  };
  return {
    history,
    selected,
    viewRevision,
    summary,
    job,
    busy,
    error,
    setError,
    select,
    cancel,
    github: (url: string) => submit(() => api.github(url)),
    zip: (file: File) => submit(() => api.zip(file)),
  };
}
