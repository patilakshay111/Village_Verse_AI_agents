import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Villager } from "../types";

export function Villagers() {
  const [list, setList] = useState<Villager[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    api.villagers().then(setList);
  }, []);

  const filtered = list.filter(
    (v) =>
      v.name.toLowerCase().includes(q.toLowerCase()) ||
      v.occupation.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div className="space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Villagers</h1>
      <input
        className="w-full max-w-md rounded-lg border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] px-4 py-2"
        placeholder="Search by name or occupation"
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((v) => (
          <Link
            key={v.id}
            to={`/villagers/${v.id}`}
            className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4 transition hover:border-[var(--color-vv-accent)]/50"
          >
            <h3 className="font-semibold">{v.name}</h3>
            <p className="text-sm text-[var(--color-vv-muted)]">
              {v.age} · {v.occupation}
            </p>
            <p className="mt-2 text-sm">
              Emotion: <span className="text-[var(--color-vv-accent)]">{v.current_emotion}</span>
            </p>
          </Link>
        ))}
      </div>
    </div>
  );
}
