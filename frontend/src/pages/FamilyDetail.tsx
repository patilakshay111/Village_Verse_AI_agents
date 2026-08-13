import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { FamilyDetail as FamilyDetailType } from "../types";

export function FamilyDetail() {
  const { id } = useParams<{ id: string }>();
  const [f, setF] = useState<FamilyDetailType | null>(null);

  useEffect(() => {
    if (id) api.family(id).then(setF);
  }, [id]);

  if (!f) return <p className="text-[var(--color-vv-muted)]">Loading…</p>;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link to="/families" className="text-sm text-[var(--color-vv-accent)]">← Families</Link>
      <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">{f.name}</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-lg bg-[var(--color-vv-surface)] p-4 text-center">
          <p className="text-xs text-[var(--color-vv-muted)]">Reputation</p>
          <p className="text-xl font-bold text-[var(--color-vv-accent)]">{f.reputation}</p>
        </div>
        <div className="rounded-lg bg-[var(--color-vv-surface)] p-4 text-center">
          <p className="text-xs text-[var(--color-vv-muted)]">Wealth</p>
          <p className="text-xl font-bold">{f.wealth}</p>
        </div>
        <div className="rounded-lg bg-[var(--color-vv-surface)] p-4 text-center">
          <p className="text-xs text-[var(--color-vv-muted)]">Influence</p>
          <p className="text-xl font-bold">{f.influence}</p>
        </div>
      </div>
      <section>
        <h2 className="font-semibold">Family tree / members</h2>
        <ul className="mt-3 space-y-2">
          {f.members.map((m) => (
            <li key={m.id}>
              <Link to={`/villagers/${m.id}`} className="font-medium hover:text-[var(--color-vv-accent)]">
                {m.name}
              </Link>
              <span className="text-sm text-[var(--color-vv-muted)]">
                {" "}
                — {m.age} yrs, {m.occupation}, {m.current_emotion}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
