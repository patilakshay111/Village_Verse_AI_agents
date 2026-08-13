import type {
  Conversation,
  ConversationListResponse,
  AssetItem,
  BusinessItem,
  CivilizationOverview,
  ConstructionProjectItem,
  EconomyResponse,
  Family,
  FamilyDetail,
  Location,
  MetricsResponse,
  OrganizationItem,
  SimulationStatus,
  Story,
  StoryFilters,
  StoryListResponse,
  Villager,
  VillagerDetail,
} from "../types";

/** In dev, use Vite proxy (/api → backend). Override with VITE_API_URL if needed. */
function apiBase(): string {
  const env = import.meta.env.VITE_API_URL?.trim();
  if (env) return env.replace(/\/$/, "");
  if (import.meta.env.DEV) return "/api";
  return "";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error((err as { detail?: string }).detail || res.statusText);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  seed: () => request<{ families: number; villagers: number; locations: number }>("/admin/seed", { method: "POST" }),

  villagers: (params?: { family_id?: string; location_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.family_id) q.set("family_id", params.family_id);
    if (params?.location_id) q.set("location_id", params.location_id);
    const qs = q.toString();
    return request<Villager[]>(`/villagers${qs ? `?${qs}` : ""}`);
  },
  villager: (id: string) => request<VillagerDetail>(`/villagers/${id}`),

  families: () => request<Family[]>("/families"),
  family: (id: string) => request<FamilyDetail>(`/families/${id}`),

  locations: () => request<Location[]>("/locations"),

  stories: (filters: StoryFilters = {}) => {
    const q = new URLSearchParams();
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== "" && v !== null) q.set(k, String(v));
    });
    const qs = q.toString();
    return request<StoryListResponse>(`/stories${qs ? `?${qs}` : ""}`);
  },
  story: (id: string) => request<Story>(`/stories/${id}`),

  conversations: (params?: { tick_id?: number; villager_id?: string; location_id?: string; q?: string; offset?: number; limit?: number }) => {
    const q = new URLSearchParams();
    Object.entries(params ?? {}).forEach(([k, v]) => {
      if (v !== undefined && v !== "") q.set(k, String(v));
    });
    const qs = q.toString();
    return request<ConversationListResponse>(`/conversations${qs ? `?${qs}` : ""}`);
  },
  conversation: (id: number) => request<Conversation>(`/conversations/${id}`),
  conversationByTick: (tickId: number) => request<Conversation>(`/conversations/by-tick/${tickId}`),

  simulationStatus: () => request<SimulationStatus>("/simulation/status"),
  simulationTick: () => request<{ tick_id: number; events: number; stories: number; error: string | null }>("/simulation/tick", { method: "POST" }),
  simulationRun: (ticks: number) => request<{ ticks_completed: number }>("/simulation/run", { method: "POST", body: JSON.stringify({ ticks }) }),
  simulationStart: () => request<{ status: string }>("/simulation/start", { method: "POST" }),
  simulationPause: () => request<{ status: string }>("/simulation/pause", { method: "POST" }),

  metrics: () => request<MetricsResponse>("/metrics"),
  economy: () => request<EconomyResponse>("/economy"),
  assets: (limit = 50) => request<AssetItem[]>(`/assets?limit=${limit}`),
  businesses: (limit = 50) => request<BusinessItem[]>(`/businesses?limit=${limit}`),
  organizations: (limit = 50) => request<OrganizationItem[]>(`/organizations?limit=${limit}`),
  construction: (limit = 50) => request<ConstructionProjectItem[]>(`/construction?limit=${limit}`),
  civilization: () => request<CivilizationOverview>("/civilization"),
};
