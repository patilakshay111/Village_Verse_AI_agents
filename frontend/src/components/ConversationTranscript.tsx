import type { Conversation, ConversationLine } from "../types";

const emotionColor: Record<string, string> = {
  Angry: "text-red-400",
  Happy: "text-emerald-400",
  Hopeful: "text-sky-400",
  Frustrated: "text-orange-400",
  Calm: "text-[var(--color-vv-muted)]",
  Sad: "text-violet-400",
};

function Line({ line }: { line: ConversationLine }) {
  const emotionClass = line.emotion ? emotionColor[line.emotion] ?? "text-[var(--color-vv-muted)]" : "";
  return (
    <div className="rounded-lg bg-[var(--color-vv-surface-2)] px-4 py-3">
      <div className="flex flex-wrap items-baseline gap-2">
        <span className="font-semibold text-[var(--color-vv-accent)]">{line.speaker}</span>
        {line.emotion && (
          <span className={`text-xs ${emotionClass}`}>({line.emotion})</span>
        )}
      </div>
      <p className="mt-1 text-sm leading-relaxed">{line.message}</p>
    </div>
  );
}

export function ConversationTranscript({
  conversation,
  compact = false,
}: {
  conversation: Conversation;
  compact?: boolean;
}) {
  if (conversation.lines.length === 0) {
    return <p className="text-sm text-[var(--color-vv-muted)]">No dialogue recorded.</p>;
  }

  return (
    <div className="space-y-3">
      {!compact && (
        <p className="text-sm text-[var(--color-vv-muted)]">
          Tick {conversation.tick_id}
          {conversation.location_name ? ` · ${conversation.location_name}` : ""}
          {conversation.participants.length > 0 && (
            <> · {conversation.participants.join(", ")}</>
          )}
        </p>
      )}
      {conversation.lines.map((line, i) => (
        <Line key={`${line.speaker}-${i}`} line={line} />
      ))}
      {conversation.important_moments.length > 0 && (
        <div className="rounded-lg border border-[var(--color-vv-border)] p-3">
          <h4 className="text-xs font-semibold uppercase tracking-wide text-[var(--color-vv-muted)]">
            Key moments
          </h4>
          <ul className="mt-2 list-inside list-disc text-sm text-[var(--color-vv-muted)]">
            {conversation.important_moments.map((m) => (
              <li key={m}>{m}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
