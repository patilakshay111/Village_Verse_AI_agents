import { useState } from "react";
import { api } from "../api/client";
import type { SimulationStatus } from "../types";

export function SimulationControls({
  status,
  onUpdate,
}: {
  status: SimulationStatus | null;
  onUpdate: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const run = async (fn: () => Promise<unknown>, label: string) => {
    setBusy(true);
    setMsg(null);
    try {
      await fn();
      setMsg(`${label} — done`);
      onUpdate();
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Failed");
    } finally {
      setBusy(false);
    }
  };

  const btn =
    "rounded-lg border border-[var(--color-vv-border)] bg-[var(--color-vv-surface-2)] px-4 py-2 text-sm font-medium hover:border-[var(--color-vv-accent)] disabled:opacity-50";

  return (
    <div className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
      <h2 className="font-[family-name:var(--font-display)] text-lg font-semibold">
        Simulation controls
      </h2>
      <p className="mt-1 text-sm text-[var(--color-vv-muted)]">
        Status:{" "}
        <span className="font-medium text-[var(--color-vv-accent)]">
          {status?.status === "pausing" ? "pausing (finishing current step…)" : status?.status ?? "—"}
        </span>
        {status?.last_error && (
          <span className="ml-2 text-[var(--color-vv-danger)]">{status.last_error}</span>
        )}
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" disabled={busy} className={btn} onClick={() => run(() => api.simulationTick(), "1 tick")}>
          Run 1 Tick
        </button>
        <button type="button" disabled={busy} className={btn} onClick={() => run(() => api.simulationRun(10), "10 ticks")}>
          Run 10 Ticks
        </button>
        <button type="button" disabled={busy} className={btn} onClick={() => run(() => api.simulationRun(100), "100 ticks")}>
          Run 100 Ticks
        </button>
        <button type="button" disabled={busy} className={`${btn} border-[var(--color-vv-accent)]/50`} onClick={() => run(() => api.simulationStart(), "Continuous")}>
          Start Continuous
        </button>
        <button type="button" disabled={busy} className={btn} onClick={() => run(() => api.simulationPause(), "Pause")}>
          Pause
        </button>
        <button type="button" disabled={busy} className={btn} onClick={() => run(() => api.seed(), "Seed world")}>
          Reset & Seed
        </button>
      </div>
      {msg && <p className="mt-3 text-sm text-[var(--color-vv-muted)]">{msg}</p>}
      {busy && (
        <p className="mt-2 text-sm text-[var(--color-vv-accent)]">
          Running tick… {status?.fast_mode !== false
            ? "Fast mode: usually 2–5 min on llama3.2:1b (3 LLM steps). Do not click again."
            : "Full mode: may take 10–20 min. Do not click again."}
        </p>
      )}
      {status?.fast_mode !== false && !busy && (
        <p className="mt-2 text-xs text-[var(--color-vv-muted)]">
          Fast mode on ({status?.agents_per_tick ?? 3} villagers/tick). For richer simulation set SIMULATION_FAST_MODE=false in .env and restart.
        </p>
      )}
    </div>
  );
}
