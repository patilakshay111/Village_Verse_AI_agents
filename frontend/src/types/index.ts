export interface Villager {
  id: string;
  name: string;
  age: number;
  gender: string;
  occupation: string;
  family_id: string;
  location_id: string | null;
  current_emotion: string;
  emotion_intensity: number;
}

export interface VillagerDetail extends Villager {
  education: string | null;
  personality: string[];
  friends: { agent_id: string; name: string; friendship: number; rivalry: number }[];
  rivals: { agent_id: string; name: string; friendship: number; rivalry: number }[];
  memories: { id: number; content: string; emotion: string | null; importance: number; sim_timestamp: string | null }[];
  recent_stories: { story_id: string; title: string; importance: number }[];
  agent_role: string | null;
  cash: number;
  bank_balance: number;
  monthly_income: number;
  monthly_expenses: number;
  net_worth: number;
  reputation: number;
  skills: string[];
  intelligence: number;
  employment_status: string;
}

export interface Family {
  id: string;
  name: string;
  surname: string;
  reputation: number;
  wealth: number;
  influence: number;
}

export interface FamilyDetail extends Family {
  members: { id: string; name: string; age: number; occupation: string; current_emotion: string }[];
  traditions: string[];
}

export interface Location {
  id: string;
  name: string;
  description: string | null;
}

export interface ConversationLine {
  speaker: string;
  message: string;
  emotion: string | null;
}

export interface Conversation {
  id: number;
  tick_id: number;
  location_id: string | null;
  location_name: string | null;
  event_id: string | null;
  participants: string[];
  lines: ConversationLine[];
  important_moments: string[];
}

export interface ConversationListResponse {
  items: Conversation[];
  total: number;
  offset: number;
  limit: number;
}

export interface Story {
  id: number;
  story_id: string;
  tick_id: number | null;
  title: string;
  summary: string;
  full_story: string | null;
  date: string | null;
  time: string | null;
  location: string | null;
  category: string | null;
  importance: number;
  participants: string[];
  families: string[];
  tags: string[];
  keywords: string[];
  future_hooks: string[];
}

export interface StoryListResponse {
  items: Story[];
  total: number;
  offset: number;
  limit: number;
}

export interface SimulationStatus {
  current_day: number;
  current_time: string;
  tick_count: number;
  status: string;
  weather: string;
  population: number;
  fast_mode: boolean;
  agents_per_tick: number;
  simulation_mode: string;
  active_conversations: number;
  latest_events: { title: string; category: string; importance: number }[];
  latest_stories: { title: string; importance: number; category: string | null }[];
  last_error: string | null;
  civilization_stage: string;
  technology_level: number;
  gdp: number;
  total_wealth: number;
  unemployment_rate: number;
  active_businesses: number;
  active_organizations: number;
}

export interface TopFamilyItem {
  family_id: string;
  name: string;
  wealth: number;
  reputation: number;
  member_count: number;
}

export interface TopBusinessItem {
  business_id: string;
  name: string;
  business_type: string;
  revenue_monthly: number;
  owner_name: string | null;
}

export interface MetricsResponse {
  total_wealth: number;
  gdp: number;
  active_businesses: number;
  active_organizations: number;
  population: number;
  unemployment_rate: number;
  technology_level: number;
  civilization_stage: string;
  simulation_mode: string;
  top_families: TopFamilyItem[];
  top_businesses: TopBusinessItem[];
}

export interface MarketPrice {
  market_id: string;
  commodity: string;
  price: number;
  supply: number;
  demand: number;
}

export interface EconomyResponse {
  gdp: number;
  total_wealth: number;
  unemployment_rate: number;
  inflation_rate: number;
  active_businesses: number;
  active_organizations: number;
  market_prices: MarketPrice[];
}

export interface AssetItem {
  id: string;
  owner_type: string;
  owner_id: string;
  asset_type: string;
  name: string;
  value: number;
  monthly_revenue: number;
  monthly_cost: number;
  status: string;
  location_id: string | null;
}

export interface BusinessItem {
  id: string;
  name: string;
  business_type: string;
  owner_id: string;
  owner_name: string | null;
  cash: number;
  revenue_monthly: number;
  expenses_monthly: number;
  employee_count: number;
  status: string;
}

export interface OrganizationItem {
  id: string;
  name: string;
  org_type: string;
  owner_id: string | null;
  owner_name: string | null;
  cash: number;
  budget: number;
  reputation: number;
  technology_level: number;
  employee_count: number;
  status: string;
}

export interface ConstructionProjectItem {
  id: string;
  owner_type: string;
  owner_id: string;
  project_type: string;
  total_cost: number;
  spent: number;
  progress_pct: number;
  status: string;
  location_id: string | null;
}

export interface CivilizationOverview {
  civilization_stage: string;
  technology_level: number;
  next_stage: string | null;
  requirements: string[];
}

export interface StoryFilters {
  date?: string;
  time_from?: string;
  time_to?: string;
  category?: string;
  villager_id?: string;
  family_id?: string;
  location?: string;
  importance_min?: number;
  q?: string;
  offset?: number;
  limit?: number;
}
