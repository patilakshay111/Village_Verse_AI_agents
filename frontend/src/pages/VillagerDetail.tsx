import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { VillagerDetail as VillagerDetailType } from "../types";

export function VillagerDetail() {
  const { id } = useParams<{ id: string }>();
  const [v, setV] = useState<VillagerDetailType | null>(null);

  useEffect(() => {
    if (id) api.villager(id).then(setV);
  }, [id]);

  if (!v) return <p className="text-[var(--color-vv-muted)]">Loading…</p>;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <Link to="/villagers" className="text-sm text-[var(--color-vv-accent)]">← Villagers</Link>
      <header>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">{v.name}</h1>
        <p className="text-[var(--color-vv-muted)]">
          {v.age} · {v.gender} · {v.occupation} · Family {v.family_id}
        </p>
        <p className="mt-2">
          Current emotion: <strong className="text-[var(--color-vv-accent)]">{v.current_emotion}</strong> (
          {v.emotion_intensity.toFixed(2)})
        </p>
      </header>
      <section className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-4">
        <h2 className="font-semibold">Economics</h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Role</p>
            <p className="mt-1 font-semibold">{v.agent_role ?? "villager"}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Employment</p>
            <p className="mt-1 font-semibold">{v.employment_status}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Cash</p>
            <p className="mt-1 font-semibold">{Math.round(v.cash)}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Bank</p>
            <p className="mt-1 font-semibold">{Math.round(v.bank_balance)}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Monthly income</p>
            <p className="mt-1 font-semibold">{Math.round(v.monthly_income)}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Monthly expenses</p>
            <p className="mt-1 font-semibold">{Math.round(v.monthly_expenses)}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Net worth</p>
            <p className="mt-1 font-semibold">{Math.round(v.net_worth)}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Reputation</p>
            <p className="mt-1 font-semibold">{Math.round(v.reputation)}</p>
          </div>
        </div>
        {v.skills.length > 0 && (
          <div className="mt-4">
            <p className="text-xs uppercase tracking-wide text-[var(--color-vv-muted)]">Skills</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {v.skills.map((s) => (
                <span key={s} className="rounded-full bg-[var(--color-vv-surface-2)] px-3 py-1 text-sm">
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </section>
      {v.personality.length > 0 && (
        <section>
          <h2 className="font-semibold">Personality</h2>
          <div className="mt-2 flex flex-wrap gap-2">
            {v.personality.map((t) => (
              <span key={t} className="rounded-full bg-[var(--color-vv-surface-2)] px-3 py-1 text-sm">
                {t}
              </span>
            ))}
          </div>
        </section>
      )}
      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-xl border border-[var(--color-vv-border)] p-4">
          <h2 className="font-semibold">Friends</h2>
          <ul className="mt-2 space-y-1 text-sm">
            {v.friends.length === 0 && <li className="text-[var(--color-vv-muted)]">None listed</li>}
            {v.friends.map((f) => (
              <li key={f.agent_id}>
                <Link to={`/villagers/${f.agent_id}`}>{f.name}</Link> (friendship {f.friendship})
              </li>
            ))}
          </ul>
        </section>
        <section className="rounded-xl border border-[var(--color-vv-border)] p-4">
          <h2 className="font-semibold">Rivals</h2>
          <ul className="mt-2 space-y-1 text-sm">
            {v.rivals.length === 0 && <li className="text-[var(--color-vv-muted)]">None listed</li>}
            {v.rivals.map((r) => (
              <li key={r.agent_id}>
                <Link to={`/villagers/${r.agent_id}`}>{r.name}</Link> (rivalry {r.rivalry})
              </li>
            ))}
          </ul>
        </section>
      </div>
      <section className="rounded-xl border border-[var(--color-vv-border)] p-4">
        <h2 className="font-semibold">Memories</h2>
        <ul className="mt-3 space-y-3">
          {v.memories.length === 0 && <li className="text-sm text-[var(--color-vv-muted)]">No memories yet</li>}
          {v.memories.map((m) => (
            <li key={m.id} className="border-b border-[var(--color-vv-border)] pb-3 text-sm last:border-0">
              <p>{m.content}</p>
              <p className="mt-1 text-[var(--color-vv-muted)]">
                {m.emotion} · importance {m.importance} · {m.sim_timestamp}
              </p>
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2 className="font-semibold">Recent stories</h2>
        <ul className="mt-2 space-y-1">
          {v.recent_stories.map((s) => (
            <li key={s.story_id}>
              <Link to="/feed" className="text-[var(--color-vv-accent)]">
                {s.title}
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
