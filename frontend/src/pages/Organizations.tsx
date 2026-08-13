import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { OrganizationItem } from "../types";

export function Organizations() {
  const [items, setItems] = useState<OrganizationItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .organizations(100)
      .then((r) => {
        setItems(r);
        setError(null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load organizations"));
  }, []);

  if (error) return <p className="text-sm text-[var(--color-vv-danger)]">{error}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Organizations</h1>
        <p className="mt-1 text-[var(--color-vv-muted)]">Active organizations sorted by reputation.</p>
      </div>

      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[var(--color-vv-muted)]">
              <tr>
                <th className="py-2 pr-3 font-medium">Name</th>
                <th className="py-2 pr-3 font-medium">Type</th>
                <th className="py-2 pr-3 font-medium">Owner</th>
                <th className="py-2 pr-3 font-medium">Cash</th>
                <th className="py-2 pr-3 font-medium">Budget</th>
                <th className="py-2 pr-3 font-medium">Tech</th>
                <th className="py-2 pr-3 font-medium">Employees</th>
              </tr>
            </thead>
            <tbody>
              {items.map((o) => (
                <tr key={o.id} className="border-t border-[var(--color-vv-border)]">
                  <td className="py-2 pr-3">{o.name}</td>
                  <td className="py-2 pr-3">{o.org_type}</td>
                  <td className="py-2 pr-3">{o.owner_name ?? o.owner_id ?? "—"}</td>
                  <td className="py-2 pr-3">{Math.round(o.cash)}</td>
                  <td className="py-2 pr-3">{Math.round(o.budget)}</td>
                  <td className="py-2 pr-3">{o.technology_level.toFixed(2)}</td>
                  <td className="py-2 pr-3">{o.employee_count}</td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="py-3 text-[var(--color-vv-muted)]" colSpan={7}>
                    No organizations yet.
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

