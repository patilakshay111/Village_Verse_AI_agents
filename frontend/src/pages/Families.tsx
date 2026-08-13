import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Family } from "../types";

export function Families() {
  const [list, setList] = useState<Family[]>([]);

  useEffect(() => {
    api.families().then(setList);
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Families</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((f) => (
          <Link
            key={f.id}
            to={`/families/${f.id}`}
            className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5 hover:border-[var(--color-vv-accent)]/50"
          >
            <h3 className="text-lg font-semibold">{f.name}</h3>
            <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
              <div>
                <p className="text-[var(--color-vv-muted)]">Reputation</p>
                <p className="font-semibold text-[var(--color-vv-accent)]">{Math.round(f.reputation)}</p>
              </div>
              <div>
                <p className="text-[var(--color-vv-muted)]">Wealth</p>
                <p className="font-semibold">{Math.round(f.wealth)}</p>
              </div>
              <div>
                <p className="text-[var(--color-vv-muted)]">Influence</p>
                <p className="font-semibold">{Math.round(f.influence)}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
