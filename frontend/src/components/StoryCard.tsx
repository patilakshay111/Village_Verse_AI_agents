import type { Story } from "../types";

export function StoryCard({
  story,
  onReadMore,
}: {
  story: Story;
  onReadMore: (s: Story) => void;
}) {
  const importancePct = Math.round(story.importance * 100);

  return (
    <article className="rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-5 shadow-sm transition hover:border-[var(--color-vv-accent)]/40">
      <div className="mb-3 flex flex-wrap gap-3 text-xs text-[var(--color-vv-muted)]">
        {story.date && <span>📅 {story.date}</span>}
        {story.time && <span>🕒 {story.time}</span>}
        {story.location && <span>📍 {story.location}</span>}
        {story.category && (
          <span className="rounded-full bg-[var(--color-vv-surface-2)] px-2 py-0.5">
            {story.category}
          </span>
        )}
      </div>
      <h3 className="font-[family-name:var(--font-display)] text-lg font-semibold leading-snug">
        {story.title}
      </h3>
      {story.participants.length > 0 && (
        <p className="mt-2 text-sm text-[var(--color-vv-muted)]">
          <span className="font-medium text-[var(--color-vv-text)]">Participants: </span>
          {story.participants.join(" · ")}
        </p>
      )}
      <p className="mt-3 text-sm leading-relaxed text-[var(--color-vv-text)]/90">
        {story.summary}
      </p>
      {story.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {story.tags.map((t) => (
            <span
              key={t}
              className="text-xs text-[var(--color-vv-accent)]"
            >
              #{t.replace(/\s+/g, "")}
            </span>
          ))}
        </div>
      )}
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--color-vv-muted)]">Importance</span>
          <div className="h-2 w-24 overflow-hidden rounded-full bg-[var(--color-vv-surface-2)]">
            <div
              className="h-full rounded-full bg-[var(--color-vv-accent)]"
              style={{ width: `${importancePct}%` }}
            />
          </div>
          <span className="text-xs font-medium">{story.importance.toFixed(2)}</span>
        </div>
        <button
          type="button"
          onClick={() => onReadMore(story)}
          className="rounded-lg bg-[var(--color-vv-accent)]/15 px-4 py-2 text-sm font-medium text-[var(--color-vv-accent)] hover:bg-[var(--color-vv-accent)]/25"
        >
          Read Full Story
        </button>
      </div>
    </article>
  );
}
