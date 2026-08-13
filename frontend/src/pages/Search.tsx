import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { StoryCard } from "../components/StoryCard";
import { StoryModal } from "../components/StoryModal";
import type { Family, Story, Villager } from "../types";

export function Search() {
  const [q, setQ] = useState("");
  const [stories, setStories] = useState<Story[]>([]);
  const [matchVillagers, setMatchVillagers] = useState<Villager[]>([]);
  const [matchFamilies, setMatchFamilies] = useState<Family[]>([]);
  const [selected, setSelected] = useState<Story | null>(null);
  const [loading, setLoading] = useState(false);

  const search = async () => {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const [sRes, vList, fList] = await Promise.all([
        api.stories({ q: q.trim(), limit: 20 }),
        api.villagers(),
        api.families(),
      ]);
      setStories(sRes.items);
      const lower = q.toLowerCase();
      setMatchVillagers(vList.filter((v) => v.name.toLowerCase().includes(lower)));
      setMatchFamilies(
        fList.filter(
          (f) => f.name.toLowerCase().includes(lower) || f.surname.toLowerCase().includes(lower)
        )
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Search</h1>
      <div className="flex gap-2">
        <input
          className="flex-1 rounded-lg border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] px-4 py-3"
          placeholder="Character, family, event, keyword…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && search()}
        />
        <button
          type="button"
          onClick={search}
          disabled={loading}
          className="rounded-lg bg-[var(--color-vv-accent)] px-6 py-3 font-medium text-[#1a1208] hover:opacity-90 disabled:opacity-50"
        >
          Search
        </button>
      </div>
      {loading && <p className="text-sm text-[var(--color-vv-muted)]">Searching…</p>}
      <section>
        <h2 className="font-semibold">Villagers</h2>
        <ul className="mt-2 flex flex-wrap gap-2">
          {matchVillagers.slice(0, 12).map((v) => (
            <li key={v.id}>
              <Link
                to={`/villagers/${v.id}`}
                className="rounded-full bg-[var(--color-vv-surface-2)] px-3 py-1 text-sm hover:text-[var(--color-vv-accent)]"
              >
                {v.name}
              </Link>
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="font-semibold">Families</h2>
        <ul className="mt-2 flex flex-wrap gap-2">
          {matchFamilies.map((f) => (
            <li key={f.id}>
              <Link
                to={`/families/${f.id}`}
                className="rounded-full bg-[var(--color-vv-surface-2)] px-3 py-1 text-sm"
              >
                {f.name}
              </Link>
            </li>
          ))}
        </ul>
      </section>
      <section className="space-y-4">
        <h2 className="font-semibold">Stories</h2>
        {stories.map((s) => (
          <StoryCard key={s.story_id} story={s} onReadMore={setSelected} />
        ))}
      </section>
      {selected && <StoryModal story={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
