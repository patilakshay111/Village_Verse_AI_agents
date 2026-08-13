import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { EconomyResponse } from "../types";

export function Economy() {
  const [e, setE] = useState<EconomyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .economy()
      .then((r) => {
        setE(r);
        setError(null);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load economy"));
  }, []);

  if (error) return <p className="text-sm text-[var(--color-vv-danger)]">{error}</p>;
  if (!e) return <p className="text-[var(--color-vv-muted)]">Loading…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Economy</h1>
        <p className="mt-1 text-[var(--color-vv-muted)]">Macro metrics and market prices (latest snapshots).</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
          <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">GDP</p>
          <p className="mt-1 text-2xl font-semibold text-[var(--color-vv-accent)]">{Math.round(e.gdp)}</p>
        </div>
        <div className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
          <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Total wealth</p>
          <p className="mt-1 text-2xl font-semibold text-[var(--color-vv-accent)]">{Math.round(e.total_wealth)}</p>
        </div>
        <div className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
          <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Unemployment</p>
          <p className="mt-1 text-2xl font-semibold text-[var(--color-vv-accent)]">
            {Math.round(e.unemployment_rate * 100)}%
          </p>
        </div>
        <div className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
          <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Inflation</p>
          <p className="mt-1 text-2xl font-semibold text-[var(--color-vv-accent)]">
            {Math.round(e.inflation_rate * 100)}%
          </p>
        </div>
      </div>

      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
        <h2 className="font-semibold">Market prices</h2>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[var(--color-vv-muted)]">
              <tr>
                <th className="py-2 pr-3 font-medium">Commodity</th>
                <th className="py-2 pr-3 font-medium">Price</th>
                <th className="py-2 pr-3 font-medium">Supply</th>
                <th className="py-2 pr-3 font-medium">Demand</th>
              </tr>
            </thead>
            <tbody>
              {e.market_prices.map((p) => (
                <tr key={`${p.market_id}:${p.commodity}`} className="border-t border-[var(--color-vv-border)]">
                  <td className="py-2 pr-3">{p.commodity}</td>
                  <td className="py-2 pr-3">{p.price.toFixed(2)}</td>
                  <td className="py-2 pr-3">{p.supply.toFixed(0)}</td>
                  <td className="py-2 pr-3">{p.demand.toFixed(0)}</td>
                </tr>
              ))}
              {e.market_prices.length === 0 && (
                <tr>
                  <td className="py-3 text-[var(--color-vv-muted)]" colSpan={4}>
                    No market prices yet. Run a civilization tick (or seed + tick).
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

