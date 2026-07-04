const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message)
  }
}

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((init.headers as Record<string, string>) ?? {}),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers })
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }))
    throw new ApiError(res.status, (body as { detail?: string }).detail ?? res.statusText)
  }
  return res.json() as Promise<T>
}

// --- Types ---

export interface StateItem {
  id: string
  name: string
  code: string
  current_risk_level: string
  last_assessed_at: string | null
}

export interface Assessment {
  id: string
  state_id: string
  risk_level: string
  overall_score: number
  climate_score: number
  health_score: number
  vulnerability_score: number
  advisory_en: string
  advisory_ha: string
  advisory_yo: string
  advisory_ig: string
  assessed_at: string
}

export interface GovernmentContact {
  id: string
  state_id: string
  name: string
  title: string
  ministry: string
  phone: string | null
  email: string
}

export interface RiskStateChange {
  id: string
  state_id: string
  state_name: string
  from_level: string
  to_level: string
  reason: string | null
  changed_at: string
}

export interface AssessmentHistoryResponse {
  items: Assessment[]
  next_cursor: string | null
}

export interface LogsResponse {
  items: RiskStateChange[]
  next_cursor: string | null
}

export interface SchedulerStatus {
  state_id: string
  state_name: string
  interval_hours: number
  next_run_time: string | null
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

// --- Auth ---

export async function login(email: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

// --- States ---

export async function getStates(token: string): Promise<StateItem[]> {
  return request<StateItem[]>('/api/states', {}, token)
}

// --- Admin: Assessments ---

export async function getAssessments(
  token: string,
  stateId?: string,
  cursor?: string,
): Promise<AssessmentHistoryResponse> {
  const params = new URLSearchParams()
  if (stateId) params.set('state_id', stateId)
  if (cursor) params.set('cursor', cursor)
  const qs = params.toString() ? `?${params.toString()}` : ''
  return request<AssessmentHistoryResponse>(`/api/admin/assessments${qs}`, {}, token)
}

export async function triggerAssessment(token: string, stateId: string): Promise<{ message: string }> {
  return request<{ message: string }>(`/api/admin/trigger/${stateId}`, { method: 'POST' }, token)
}

// --- Admin: Contacts ---

export async function getContacts(token: string): Promise<GovernmentContact[]> {
  return request<GovernmentContact[]>('/api/admin/contacts', {}, token)
}

export async function createContact(
  token: string,
  data: Omit<GovernmentContact, 'id'>,
): Promise<GovernmentContact> {
  return request<GovernmentContact>('/api/admin/contacts', {
    method: 'POST',
    body: JSON.stringify(data),
  }, token)
}

export async function updateContact(
  token: string,
  id: string,
  data: Partial<Omit<GovernmentContact, 'id'>>,
): Promise<GovernmentContact> {
  return request<GovernmentContact>(`/api/admin/contacts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }, token)
}

export async function deleteContact(token: string, id: string): Promise<void> {
  await request<void>(`/api/admin/contacts/${id}`, { method: 'DELETE' }, token)
}

// --- Admin: Logs ---

export async function getLogs(token: string, cursor?: string): Promise<LogsResponse> {
  const qs = cursor ? `?cursor=${cursor}` : ''
  return request<LogsResponse>(`/api/admin/logs${qs}`, {}, token)
}

// --- Password reset ---

export async function forgotPassword(email: string): Promise<{ message: string }> {
  return request<{ message: string }>('/api/auth/forgot-password', {
    method: 'POST',
    body: JSON.stringify({ email, target: 'admin' }),
  })
}

export async function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  return request<{ message: string }>('/api/auth/reset-password', {
    method: 'POST',
    body: JSON.stringify({ token, new_password: newPassword }),
  })
}

// --- Admin: Scheduler ---

export async function getSchedulerStatus(token: string): Promise<SchedulerStatus[]> {
  return request<SchedulerStatus[]>('/api/admin/scheduler/status', {}, token)
}
