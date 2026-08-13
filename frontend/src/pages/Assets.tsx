import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AssetItem } from "../types";

export function Assets() {
  const [items, setItems] = useState<AssetItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .assets(100)
      .then((r) => {
        setItems(r);
        setError(null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load assets"));
  }, []);

  if (error) return <p className="text-sm text-[var(--color-vv-danger)]">{error}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Assets</h1>
        <p className="mt-1 text-[var(--color-vv-muted)]">Top active assets by value.</p>
      </div>

      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[var(--color-vv-muted)]">
              <tr>
                <th className="py-2 pr-3 font-medium">Name</th>
                <th className="py-2 pr-3 font-medium">Type</th>
                <th className="py-2 pr-3 font-medium">Owner</th>
                <th className="py-2 pr-3 font-medium">Value</th>
                <th className="py-2 pr-3 font-medium">Monthly P/L</th>
              </tr>
            </thead>
            <tbody>
              {items.map((a) => (
                <tr key={a.id} className="border-t border-[var(--color-vv-border)]">
                  <td className="py-2 pr-3">{a.name}</td>
                  <td className="py-2 pr-3">{a.asset_type}</td>
                  <td className="py-2 pr-3">
                    {a.owner_type}:{a.owner_id}
                  </td>
                  <td className="py-2 pr-3">{Math.round(a.value)}</td>
                  <td className="py-2 pr-3">{Math.round(a.monthly_revenue - a.monthly_cost)}</td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="py-3 text-[var(--color-vv-muted)]" colSpan={5}>
                    No assets yet.
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

