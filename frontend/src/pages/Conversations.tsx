import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { ConversationTranscript } from "../components/ConversationTranscript";
import type { Conversation } from "../types";

export function Conversations() {
  const [items, setItems] = useState<Conversation[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    setLoading(true);
    api
      .conversations({ limit: 50 })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
        if (res.items[0]) setExpanded(res.items[0].id);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="font-[family-name:var(--font-display)] text-3xl font-bold">Conversations</h1>
        <p className="mt-1 text-sm text-[var(--color-vv-muted)]">
          Raw village dialogue from each simulation tick — who said what, and how they felt.
        </p>
      </div>

      {error && <p className="text-sm text-[var(--color-vv-danger)]">{error}</p>}
      {loading && <p className="text-sm text-[var(--color-vv-muted)]">Loading…</p>}

      {!loading && items.length === 0 && (
        <p className="rounded-xl border border-dashed border-[var(--color-vv-border)] p-8 text-center text-[var(--color-vv-muted)]">
          No conversations yet. Run a tick from the{" "}
          <Link to="/" className="text-[var(--color-vv-accent)]">
            dashboard
          </Link>
          .
        </p>
      )}

      <p className="text-sm text-[var(--color-vv-muted)]">{total} conversation{total === 1 ? "" : "s"}</p>

      <div className="space-y-4">
        {items.map((c) => {
          const open = expanded === c.id;
          const preview = c.lines[0];
          return (
            <article
              key={c.id}
              className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] overflow-hidden"
            >
              <button
                type="button"
                className="flex w-full items-start justify-between gap-4 p-4 text-left hover:bg-[var(--color-vv-surface-2)]"
                onClick={() => setExpanded(open ? null : c.id)}
              >
                <div>
                  <p className="font-semibold">
                    Tick {c.tick_id}
                    {c.location_name ? ` at ${c.location_name}` : ""}
                  </p>
                  <p className="mt-1 text-sm text-[var(--color-vv-muted)]">
                    {c.participants.join(", ") || "Villagers"} · {c.lines.length} lines
                  </p>
                  {!open && preview && (
                    <p className="mt-2 text-sm italic text-[var(--color-vv-muted)]">
                      {preview.speaker}: “{preview.message.slice(0, 120)}
                      {preview.message.length > 120 ? "…" : ""}”
                    </p>
                  )}
                </div>
                <span className="text-[var(--color-vv-muted)]">{open ? "▲" : "▼"}</span>
              </button>
              {open && (
                <div className="border-t border-[var(--color-vv-border)] p-4">
                  <ConversationTranscript conversation={c} />
                </div>
              )}
            </article>
          );
        })}
      </div>
    </div>
  );
}
