import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { SimulationControls } from "../components/SimulationControls";
import type { SimulationStatus } from "../types";

export function Dashboard() {
  const [status, setStatus] = useState<SimulationStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setStatus(await api.simulationStatus());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Cannot reach API");
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 15000);
    return () => clearInterval(id);
  }, [load]);

  const stat = (label: string, value: string | number) => (
    <div className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
      <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-[var(--color-vv-accent)]">{value}</p>
    </div>
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Village Overview</h1>
        <p className="mt-1 text-[var(--color-vv-muted)]">Anandgaon — emergent stories from autonomous villagers</p>
      </div>
      {error && (
        <div className="rounded-lg border border-[var(--color-vv-danger)]/50 bg-[var(--color-vv-danger)]/10 p-4 text-sm">
          <p>{error}</p>
          <p className="mt-2 text-[var(--color-vv-muted)]">
            Check: (1) &quot;VillageVerse API&quot; terminal is open, (2){" "}
            <a href="http://127.0.0.1:8000/health" className="text-[var(--color-vv-accent)] underline" target="_blank" rel="noreferrer">
              http://127.0.0.1:8000/health
            </a>{" "}
            opens in browser, (3) restart via Run-VillageVerse.bat
          </p>
        </div>
      )}
      <SimulationControls status={status} onUpdate={load} />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stat("Current day", status?.current_day ?? "—")}
        {stat("Time", status?.current_time ?? "—")}
        {stat("Population", status?.population ?? "—")}
        {stat("Ticks", status?.tick_count ?? 0)}
        {stat("Weather", status?.weather ?? "—")}
        {stat("Active conversations", status?.active_conversations ?? 0)}
        {stat("Status", status?.status ?? "idle")}
        {stat("Mode", status?.fast_mode !== false ? "Fast" : "Full")}
      </div>

      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="font-semibold">Civilization snapshot</h2>
          <Link to="/civilization" className="text-sm font-medium text-[var(--color-vv-accent)]">
            Open dashboards →
          </Link>
        </div>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stat("Simulation mode", status?.simulation_mode ?? "—")}
          {stat("Stage", status?.civilization_stage ?? "—")}
          {stat("Tech level", status ? status.technology_level.toFixed(2) : "—")}
          {stat("GDP", status ? Math.round(status.gdp) : "—")}
          {stat("Total wealth", status ? Math.round(status.total_wealth) : "—")}
          {stat("Unemployment", status ? `${Math.round(status.unemployment_rate * 100)}%` : "—")}
          {stat("Businesses", status?.active_businesses ?? 0)}
          {stat("Organizations", status?.active_organizations ?? 0)}
        </div>
      </section>
      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
          <h2 className="font-semibold">Latest events</h2>
          <ul className="mt-3 space-y-2">
            {(status?.latest_events ?? []).length === 0 && (
              <li className="text-sm text-[var(--color-vv-muted)]">Run a tick to generate events</li>
            )}
            {status?.latest_events.map((e, i) => (
              <li key={i} className="flex justify-between text-sm">
                <span>{e.title}</span>
                <span className="text-[var(--color-vv-muted)]">{e.category}</span>
              </li>
            ))}
          </ul>
        </section>
        <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
          <h2 className="font-semibold">Latest stories</h2>
          <ul className="mt-3 space-y-2">
            {(status?.latest_stories ?? []).length === 0 && (
              <li className="text-sm text-[var(--color-vv-muted)]">No stories yet</li>
            )}
            {status?.latest_stories.map((s, i) => (
              <li key={i} className="text-sm">
                <Link to="/feed" className="hover:text-[var(--color-vv-accent)]">
                  {s.title}
                </Link>
              </li>
            ))}
          </ul>
          <Link
            to="/feed"
            className="mt-4 inline-block text-sm font-medium text-[var(--color-vv-accent)]"
          >
            View story feed →
          </Link>
        </section>
      </div>
    </div>
  );
}
