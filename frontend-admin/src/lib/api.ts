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

// ── Types ──────────────────────────────────────────────────────────────────────

export interface StateItem {
  id: string
  name: string
  code: string
  region: string
  capital: string
  latitude: number
  longitude: number
  current_risk_level: string
  last_assessed_at: string | null
}

export interface Assessment {
  id: string
  state_id: string
  state_name: string
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
  state_name: string
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

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  limit: number
  total_pages: number
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

export interface ActiveAlert {
  id: string
  state_id: string
  title: string
  description: string
  risk_level: string
  is_active: boolean
  started_at: string
  ended_at: string | null
}

export interface PipelineSource {
  source: string
  label: string
  type: 'api' | 'dataset'
  description: string
  can_trigger: boolean
  last_run: string | null
  records_stored: number
  status: 'ok' | 'error' | 'never'
}

// ── Auth ───────────────────────────────────────────────────────────────────────

export async function login(email: string, password: string): Promise<LoginResponse> {
  return request<LoginResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

// ── States ─────────────────────────────────────────────────────────────────────

export async function getStates(token: string): Promise<StateItem[]> {
  return request<StateItem[]>('/api/states', {}, token)
}

// ── Assessments ────────────────────────────────────────────────────────────────

export interface AssessmentParams {
  stateId?: string
  search?: string
  sortDir?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export async function getAssessments(
  token: string,
  params: AssessmentParams = {},
): Promise<PaginatedResponse<Assessment>> {
  const qs = new URLSearchParams()
  if (params.stateId) qs.set('state_id', params.stateId)
  if (params.search) qs.set('search', params.search)
  if (params.sortDir) qs.set('sort_dir', params.sortDir)
  if (params.page) qs.set('page', String(params.page))
  if (params.limit) qs.set('limit', String(params.limit))
  const q = qs.toString() ? `?${qs.toString()}` : ''
  return request<PaginatedResponse<Assessment>>(`/api/admin/assessments${q}`, {}, token)
}

export async function triggerAssessment(token: string, stateId: string): Promise<{ message: string }> {
  return request<{ message: string }>(`/api/admin/trigger/${stateId}`, { method: 'POST' }, token)
}

// ── Contacts ───────────────────────────────────────────────────────────────────

export interface ContactsParams {
  search?: string
  sortBy?: string
  sortDir?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export async function getContacts(
  token: string,
  params: ContactsParams = {},
): Promise<PaginatedResponse<GovernmentContact>> {
  const qs = new URLSearchParams()
  if (params.search) qs.set('search', params.search)
  if (params.sortBy) qs.set('sort_by', params.sortBy)
  if (params.sortDir) qs.set('sort_dir', params.sortDir)
  if (params.page) qs.set('page', String(params.page))
  if (params.limit) qs.set('limit', String(params.limit))
  const q = qs.toString() ? `?${qs.toString()}` : ''
  return request<PaginatedResponse<GovernmentContact>>(`/api/admin/contacts${q}`, {}, token)
}

export async function createContact(
  token: string,
  data: Omit<GovernmentContact, 'id' | 'state_name'>,
): Promise<GovernmentContact> {
  return request<GovernmentContact>('/api/admin/contacts', {
    method: 'POST',
    body: JSON.stringify(data),
  }, token)
}

export async function updateContact(
  token: string,
  id: string,
  data: Partial<Omit<GovernmentContact, 'id' | 'state_name'>>,
): Promise<GovernmentContact> {
  return request<GovernmentContact>(`/api/admin/contacts/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }, token)
}

export async function deleteContact(token: string, id: string): Promise<void> {
  await request<void>(`/api/admin/contacts/${id}`, { method: 'DELETE' }, token)
}

// ── Risk change logs ───────────────────────────────────────────────────────────

export interface LogsParams {
  search?: string
  sortDir?: 'asc' | 'desc'
  page?: number
  limit?: number
}

export async function getLogs(
  token: string,
  params: LogsParams = {},
): Promise<PaginatedResponse<RiskStateChange>> {
  const qs = new URLSearchParams()
  if (params.search) qs.set('search', params.search)
  if (params.sortDir) qs.set('sort_dir', params.sortDir)
  if (params.page) qs.set('page', String(params.page))
  if (params.limit) qs.set('limit', String(params.limit))
  const q = qs.toString() ? `?${qs.toString()}` : ''
  return request<PaginatedResponse<RiskStateChange>>(`/api/admin/logs${q}`, {}, token)
}

// ── Alerts (public) ────────────────────────────────────────────────────────────

export async function getActiveAlerts(): Promise<ActiveAlert[]> {
  return request<ActiveAlert[]>('/api/alerts/active')
}

// ── Pipeline ───────────────────────────────────────────────────────────────────

export async function getPipelineStatus(token: string): Promise<PipelineSource[]> {
  return request<PipelineSource[]>('/api/admin/pipeline/status', {}, token)
}

export async function triggerPipeline(
  token: string,
  sourceKey: string,
): Promise<{ message: string; source: string }> {
  return request<{ message: string; source: string }>(
    `/api/admin/pipeline/trigger/${sourceKey}`,
    { method: 'POST' },
    token,
  )
}

// ── Password reset ─────────────────────────────────────────────────────────────

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

// ── Scheduler ──────────────────────────────────────────────────────────────────

export async function getSchedulerStatus(token: string): Promise<SchedulerStatus[]> {
  return request<SchedulerStatus[]>('/api/admin/scheduler/status', {}, token)
}
