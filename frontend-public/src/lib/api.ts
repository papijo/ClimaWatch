const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? res.statusText);
  }

  return res.json();
}

function authHeaders(token: string): HeadersInit {
  return { Authorization: `Bearer ${token}` };
}

export interface StateItem {
  id: string;
  name: string;
  code: string;
  region: string;
  capital: string;
  latitude: number;
  longitude: number;
  current_risk_level: string;
}

export interface Assessment {
  id: string;
  risk_level: string;
  overall_score: number;
  climate_score: number;
  health_score: number;
  vulnerability_score: number;
  advisory_en: string | null;
  advisory_ha: string | null;
  advisory_yo: string | null;
  advisory_ig: string | null;
  assessed_at: string;
}

export interface StateDetail extends StateItem {
  latest_assessment: Assessment | null;
}

export interface LGAScore {
  id: string;
  state_id: string;
  lga_name: string;
  vulnerability_score: number;
  population_density_score: number;
  health_access_score: number;
  climate_exposure_score: number;
  scored_at: string;
}

export interface FacilityRiskScore {
  risk_score: number;
  flood_risk: number;
  heat_stress_risk: number;
  disease_burden_risk: number;
  infrastructure_vulnerability: number;
  scored_at: string;
}

export interface Facility {
  id: string;
  state_id: string;
  lga: string;
  name: string;
  facility_type: string;
  ownership: string;
  category: string | null;
  latitude: number | null;
  longitude: number | null;
  latest_risk_score: FacilityRiskScore | null;
}

export interface ActiveAlert {
  id: string;
  state_id: string;
  title: string;
  description: string;
  risk_level: string;
  is_active: boolean;
  started_at: string;
  ended_at: string | null;
}

export interface AlertHistoryResponse {
  items: ActiveAlert[];
  next_cursor: string | null;
}

export interface DiseaseAlert {
  id: string;
  state_id: string | null;
  disease_name: string;
  alert_level: string;
  source: string;
  description: string;
  affected_lgas: string[] | null;
  is_active: boolean;
  reported_at: string;
}

export interface Forecast {
  id: string;
  state_id: string;
  risk_level: string;
  overall_score: number;
  climate_score: number;
  health_score: number;
  vulnerability_score: number;
  advisory_en: string | null;
  advisory_ha: string | null;
  advisory_yo: string | null;
  advisory_ig: string | null;
  key_drivers: string[] | null;
  recommended_actions: string[] | null;
  assessed_at: string;
}

export interface Subscription {
  id: string;
  user_id: string;
  state_id: string;
  notify_moderate: boolean;
  notify_high: boolean;
  notify_critical: boolean;
  is_active: boolean;
}

export const api = {
  getStates: () => request<StateItem[]>("/api/states"),

  getState: (id: string) => request<StateDetail>(`/api/states/${id}`),

  getStateLGAs: (id: string) => request<LGAScore[]>(`/api/states/${id}/lgas`),

  getFacilities: (stateId?: string) => {
    const params = stateId ? `?state_id=${stateId}` : "";
    return request<Facility[]>(`/api/facilities${params}`);
  },

  getActiveAlerts: () => request<ActiveAlert[]>("/api/alerts/active"),

  getAlertHistory: (cursor?: string, limit = 20) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (cursor) params.set("cursor", cursor);
    return request<AlertHistoryResponse>(`/api/alerts/history?${params}`);
  },

  getDiseaseAlerts: () => request<DiseaseAlert[]>("/api/disease-alerts"),

  getForecast: (stateId: string) => request<Forecast>(`/api/forecasts/${stateId}`),

  register: (email: string, password: string, fullName: string) =>
    request<{ id: string; email: string }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
    }),

  login: (email: string, password: string) =>
    request<{ access_token: string; token_type: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  getSubscriptions: (token: string) =>
    request<Subscription[]>("/api/me/subscriptions", { headers: authHeaders(token) }),

  subscribe: (token: string, stateId: string, prefs: { notify_moderate: boolean; notify_high: boolean; notify_critical: boolean }) =>
    request<Subscription>("/api/me/subscriptions", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ state_id: stateId, ...prefs }),
    }),

  unsubscribe: (token: string, stateId: string) =>
    request<void>(`/api/me/subscriptions/${stateId}`, {
      method: "DELETE",
      headers: authHeaders(token),
    }),

  forgotPassword: (email: string, locale = "en") =>
    request<{ message: string }>("/api/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify({ email, locale }),
    }),

  resetPassword: (token: string, newPassword: string) =>
    request<{ message: string }>("/api/auth/reset-password", {
      method: "POST",
      body: JSON.stringify({ token, new_password: newPassword }),
    }),
};

export { ApiError };
