import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { Story, StoryFilters } from "../types";

const PAGE_SIZE = 10;

export function useInfiniteStories(filters: StoryFilters) {
  const [items, setItems] = useState<Story[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const offsetRef = useRef(0);
  const filtersKey = JSON.stringify(filters);

  const loadMore = useCallback(async () => {
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.stories({
        ...filters,
        offset: offsetRef.current,
        limit: PAGE_SIZE,
      });
      setTotal(res.total);
      setItems((prev) => {
        if (offsetRef.current === 0) return res.items;
        const ids = new Set(prev.map((s) => s.story_id));
        const fresh = res.items.filter((s) => !ids.has(s.story_id));
        return [...prev, ...fresh];
      });
      offsetRef.current += res.items.length;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load stories");
    } finally {
      setLoading(false);
    }
  }, [filters, loading]);

  useEffect(() => {
    offsetRef.current = 0;
    setItems([]);
    setTotal(0);
    setLoading(true);
    setError(null);
    api
      .stories({ ...filters, offset: 0, limit: PAGE_SIZE })
      .then((res) => {
        setItems(res.items);
        setTotal(res.total);
        offsetRef.current = res.items.length;
      })
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [filtersKey]);

  const hasMore = items.length < total;

  return { items, total, loading, error, hasMore, loadMore };
}
