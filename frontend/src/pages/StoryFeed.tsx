import { useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import { FeedSidebar } from "../components/FeedSidebar";
import { FilterBar } from "../components/FilterBar";
import { StoryCard } from "../components/StoryCard";
import { StoryModal } from "../components/StoryModal";
import { useInfiniteStories } from "../hooks/useInfiniteStories";
import type { Family, Location, SimulationStatus, Story, StoryFilters, Villager } from "../types";

export function StoryFeed() {
  const [filters, setFilters] = useState<StoryFilters>({});
  const [selected, setSelected] = useState<Story | null>(null);
  const [villagers, setVillagers] = useState<Villager[]>([]);
  const [families, setFamilies] = useState<Family[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [status, setStatus] = useState<SimulationStatus | null>(null);
  const sentinel = useRef<HTMLDivElement>(null);

  const { items, loading, error, hasMore, loadMore } = useInfiniteStories(filters);

  useEffect(() => {
    Promise.all([
      api.villagers(),
      api.families(),
      api.locations(),
      api.simulationStatus(),
    ]).then(([v, f, l, s]) => {
      setVillagers(v);
      setFamilies(f);
      setLocations(l);
      setStatus(s);
    });
  }, []);

  useEffect(() => {
    const el = sentinel.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting && hasMore && !loading) loadMore();
      },
      { rootMargin: "200px" }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [hasMore, loading, loadMore]);

  return (
    <div className="space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Story Feed</h1>
      <FilterBar
        filters={filters}
        onChange={setFilters}
        villagers={villagers}
        families={families}
        locations={locations}
      />
      <div className="grid gap-6 xl:grid-cols-[1fr_280px]">
        <div className="space-y-4">
          {error && <p className="text-sm text-[var(--color-vv-danger)]">{error}</p>}
          {items.length === 0 && !loading && (
            <p className="rounded-xl border border-dashed border-[var(--color-vv-border)] p-8 text-center text-[var(--color-vv-muted)]">
              No stories yet. Run a simulation tick from the dashboard.
            </p>
          )}
          {items.map((s) => (
            <StoryCard key={s.story_id} story={s} onReadMore={setSelected} />
          ))}
          <div ref={sentinel} className="h-4" />
          {loading && <p className="text-center text-sm text-[var(--color-vv-muted)]">Loading…</p>}
        </div>
        <FeedSidebar stories={items} villagers={villagers} status={status} />
      </div>
      {selected && <StoryModal story={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
