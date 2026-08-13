import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Location } from "../types";

export function Locations() {
  const [list, setList] = useState<Location[]>([]);

  useEffect(() => {
    api.locations().then(setList);
  }, []);

  return (
    <div className="space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Locations</h1>
      <p className="text-[var(--color-vv-muted)]">Social hubs across Anandgaon</p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {list.map((l) => (
          <div
            key={l.id}
            className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5"
          >
            <h3 className="font-semibold">📍 {l.name}</h3>
            <p className="mt-2 text-sm text-[var(--color-vv-muted)]">{l.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
