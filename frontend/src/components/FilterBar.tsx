import type { Family, Location, Villager } from "../types";
import type { StoryFilters } from "../types";

export function FilterBar({
  filters,
  onChange,
  villagers,
  families,
  locations,
}: {
  filters: StoryFilters;
  onChange: (f: StoryFilters) => void;
  villagers: Villager[];
  families: Family[];
  locations: Location[];
}) {
  const set = (key: keyof StoryFilters, value: string | number | undefined) => {
    onChange({ ...filters, [key]: value === "" ? undefined : value });
  };

  const inputClass =
    "w-full rounded-lg border border-[var(--color-vv-border)] bg-[var(--color-vv-surface-2)] px-3 py-2 text-sm";

  return (
    <div className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
      <h3 className="mb-3 text-sm font-semibold text-[var(--color-vv-muted)]">Filter stories</h3>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-5">
        <input
          className={inputClass}
          placeholder="Keyword search"
          value={filters.q ?? ""}
          onChange={(e) => set("q", e.target.value)}
        />
        <input
          className={inputClass}
          placeholder="Date (e.g. Day 1)"
          value={filters.date ?? ""}
          onChange={(e) => set("date", e.target.value)}
        />
        <input
          className={inputClass}
          placeholder="Time from"
          value={filters.time_from ?? ""}
          onChange={(e) => set("time_from", e.target.value)}
        />
        <input
          className={inputClass}
          placeholder="Time to"
          value={filters.time_to ?? ""}
          onChange={(e) => set("time_to", e.target.value)}
        />
        <select
          className={inputClass}
          value={filters.location ?? ""}
          onChange={(e) => set("location", e.target.value)}
        >
          <option value="">All locations</option>
          {locations.map((l) => (
            <option key={l.id} value={l.name}>
              {l.name}
            </option>
          ))}
        </select>
        <select
          className={inputClass}
          value={filters.family_id ?? ""}
          onChange={(e) => set("family_id", e.target.value)}
        >
          <option value="">All families</option>
          {families.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name}
            </option>
          ))}
        </select>
        <select
          className={inputClass}
          value={filters.villager_id ?? ""}
          onChange={(e) => set("villager_id", e.target.value)}
        >
          <option value="">All characters</option>
          {villagers.map((v) => (
            <option key={v.id} value={v.id}>
              {v.name}
            </option>
          ))}
        </select>
        <input
          className={inputClass}
          placeholder="Category"
          value={filters.category ?? ""}
          onChange={(e) => set("category", e.target.value)}
        />
        <div className="flex items-center gap-2">
          <label className="text-xs text-[var(--color-vv-muted)]">Min importance</label>
          <input
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={filters.importance_min ?? 0}
            onChange={(e) => set("importance_min", parseFloat(e.target.value) || undefined)}
            className="flex-1"
          />
          <span className="w-8 text-xs">{(filters.importance_min ?? 0).toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}
