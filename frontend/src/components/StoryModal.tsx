import { useEffect, useState } from "react";
import { api } from "../api/client";
import { ConversationTranscript } from "./ConversationTranscript";
import type { Conversation, Story } from "../types";

export function StoryModal({ story, onClose }: { story: Story; onClose: () => void }) {
  const [conversation, setConversation] = useState<Conversation | null>(null);

  useEffect(() => {
    if (story.tick_id == null) {
      setConversation(null);
      return;
    }
    api
      .conversationByTick(story.tick_id)
      .then(setConversation)
      .catch(() => setConversation(null));
  }, [story.tick_id]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      <div
        className="max-h-[85vh] w-full max-w-2xl overflow-y-auto rounded-xl border border-[var(--color-vv-border)] bg-[var(--color-vv-surface)] p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex justify-between gap-4">
          <h2 className="font-[family-name:var(--font-display)] text-2xl font-bold">
            {story.title}
          </h2>
          <button type="button" onClick={onClose} className="text-[var(--color-vv-muted)] hover:text-[var(--color-vv-text)]">
            ✕
          </button>
        </div>
        <p className="text-sm text-[var(--color-vv-muted)]">
          {[story.date, story.time, story.location].filter(Boolean).join(" · ")}
        </p>
        <p className="mt-4 leading-relaxed">{story.full_story || story.summary}</p>
        {conversation && conversation.lines.length > 0 && (
          <div className="mt-6">
            <h4 className="text-sm font-semibold text-[var(--color-vv-accent)]">What they actually said</h4>
            <div className="mt-3">
              <ConversationTranscript conversation={conversation} compact />
            </div>
          </div>
        )}
        {story.future_hooks.length > 0 && (
          <div className="mt-6 rounded-lg bg-[var(--color-vv-surface-2)] p-4">
            <h4 className="text-sm font-semibold text-[var(--color-vv-accent)]">Future hooks</h4>
            <ul className="mt-2 list-inside list-disc text-sm text-[var(--color-vv-muted)]">
              {story.future_hooks.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
