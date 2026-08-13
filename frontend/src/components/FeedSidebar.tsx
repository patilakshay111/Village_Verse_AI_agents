import { Link } from "react-router-dom";
import type { SimulationStatus, Story, Villager } from "../types";

export function FeedSidebar({
  stories,
  villagers,
  status,
}: {
  stories: Story[];
  villagers: Villager[];
  status: SimulationStatus | null;
}) {
  const trending = [...stories].sort((a, b) => b.importance - a.importance).slice(0, 5);

  const mentionCount: Record<string, number> = {};
  stories.forEach((s) => {
    s.participants.forEach((p) => {
      mentionCount[p] = (mentionCount[p] || 0) + 1;
    });
  });
  const discussed = Object.entries(mentionCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  const conflicts = villagers
    .filter((v) => ["Angry", "Frustrated", "Jealous"].includes(v.current_emotion))
    .slice(0, 5);

  return (
    <aside className="space-y-4">
      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
        <h3 className="text-sm font-semibold text-[var(--color-vv-accent)]">Trending stories</h3>
        <ul className="mt-3 space-y-2">
          {trending.length === 0 && <li className="text-sm text-[var(--color-vv-muted)]">No stories yet</li>}
          {trending.map((s) => (
            <li key={s.story_id}>
              <Link to="/feed" className="text-sm hover:text-[var(--color-vv-accent)]">
                {s.title}
              </Link>
              <span className="ml-1 text-xs text-[var(--color-vv-muted)]">({s.importance.toFixed(2)})</span>
            </li>
          ))}
        </ul>
      </section>
      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
        <h3 className="text-sm font-semibold">Most discussed</h3>
        <ul className="mt-3 space-y-1 text-sm text-[var(--color-vv-muted)]">
          {discussed.map(([name, n]) => (
            <li key={name}>
              {name} <span className="text-[var(--color-vv-accent)]">×{n}</span>
            </li>
          ))}
        </ul>
      </section>
      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
        <h3 className="text-sm font-semibold">Recent tensions</h3>
        <ul className="mt-3 space-y-1 text-sm">
          {conflicts.length === 0 && <li className="text-[var(--color-vv-muted)]">Village is calm</li>}
          {conflicts.map((v) => (
            <li key={v.id}>
              <Link to={`/villagers/${v.id}`} className="hover:text-[var(--color-vv-accent)]">
                {v.name}
              </Link>
              <span className="text-[var(--color-vv-danger)]"> — {v.current_emotion}</span>
            </li>
          ))}
        </ul>
      </section>
      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
        <h3 className="text-sm font-semibold">Upcoming</h3>
        <p className="mt-2 text-sm text-[var(--color-vv-muted)]">
          Day {status?.current_day ?? 1} · {status?.weather ?? "Clear"}
          <br />
          Holi, Diwali & village fair — emergent from simulation
        </p>
      </section>
    </aside>
  );
}
