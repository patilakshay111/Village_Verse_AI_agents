import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { MetricsResponse } from "../types";

const card = (label: string, value: string | number) => (
  <div className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
    <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">{label}</p>
    <p className="mt-1 text-2xl font-semibold text-[var(--color-vv-accent)]">{value}</p>
  </div>
);

export function CivilizationDashboard() {
  const [m, setM] = useState<MetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .metrics()
      .then((r) => {
        setM(r);
        setError(null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load metrics"));
  }, []);

  if (error) return <p className="text-sm text-[var(--color-vv-danger)]">{error}</p>;
  if (!m) return <p className="text-[var(--color-vv-muted)]">Loading…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Civilization</h1>
        <p className="mt-1 text-[var(--color-vv-muted)]">Economic and institutional evolution metrics.</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {card("Simulation mode", m.simulation_mode)}
        {card("Civilization stage", m.civilization_stage)}
        {card("Technology level", m.technology_level.toFixed(2))}
        {card("Unemployment", `${Math.round(m.unemployment_rate * 100)}%`)}
        {card("GDP", Math.round(m.gdp))}
        {card("Total wealth", Math.round(m.total_wealth))}
        {card("Businesses", m.active_businesses)}
        {card("Organizations", m.active_organizations)}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
          <h2 className="font-semibold">Top families (wealth)</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {m.top_families.length === 0 && <li className="text-[var(--color-vv-muted)]">No families</li>}
            {m.top_families.map((f) => (
              <li key={f.family_id} className="flex items-center justify-between gap-4">
                <span>{f.name}</span>
                <span className="text-[var(--color-vv-muted)]">{Math.round(f.wealth)}</span>
              </li>
            ))}
          </ul>
        </section>
        <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
          <h2 className="font-semibold">Top businesses (revenue)</h2>
          <ul className="mt-3 space-y-2 text-sm">
            {m.top_businesses.length === 0 && <li className="text-[var(--color-vv-muted)]">No businesses</li>}
            {m.top_businesses.map((b) => (
              <li key={b.business_id} className="flex items-center justify-between gap-4">
                <span>
                  {b.name} <span className="text-[var(--color-vv-muted)]">({b.business_type})</span>
                </span>
                <span className="text-[var(--color-vv-muted)]">{Math.round(b.revenue_monthly)}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

