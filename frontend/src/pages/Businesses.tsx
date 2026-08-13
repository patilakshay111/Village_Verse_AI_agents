import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { BusinessItem } from "../types";

export function Businesses() {
  const [items, setItems] = useState<BusinessItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .businesses(100)
      .then((r) => {
        setItems(r);
        setError(null);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load businesses"));
  }, []);

  if (error) return <p className="text-sm text-[var(--color-vv-danger)]">{error}</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Businesses</h1>
        <p className="mt-1 text-[var(--color-vv-muted)]">Active businesses sorted by monthly revenue.</p>
      </div>

      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[var(--color-vv-muted)]">
              <tr>
                <th className="py-2 pr-3 font-medium">Name</th>
                <th className="py-2 pr-3 font-medium">Type</th>
                <th className="py-2 pr-3 font-medium">Owner</th>
                <th className="py-2 pr-3 font-medium">Revenue</th>
                <th className="py-2 pr-3 font-medium">Expenses</th>
                <th className="py-2 pr-3 font-medium">Employees</th>
              </tr>
            </thead>
            <tbody>
              {items.map((b) => (
                <tr key={b.id} className="border-t border-[var(--color-vv-border)]">
                  <td className="py-2 pr-3">{b.name}</td>
                  <td className="py-2 pr-3">{b.business_type}</td>
                  <td className="py-2 pr-3">{b.owner_name ?? b.owner_id}</td>
                  <td className="py-2 pr-3">{Math.round(b.revenue_monthly)}</td>
                  <td className="py-2 pr-3">{Math.round(b.expenses_monthly)}</td>
                  <td className="py-2 pr-3">{b.employee_count}</td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td className="py-3 text-[var(--color-vv-muted)]" colSpan={6}>
                    No businesses yet.
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

