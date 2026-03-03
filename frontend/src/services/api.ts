/**
 * API client for Ordinus backend.
 * Uses /api prefix when served via Vite proxy.
 */
const BASE = '/api'

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })
  if (res.status === 204) return undefined as T
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.detail || res.statusText || 'Request failed')
  return data as T
}

// Types (mirror backend schemas)
export interface Faculty {
  id: number
  name: string
  email?: string
}

export interface FacultyAvailabilitySlot {
  id: number
  faculty_id: number
  day: number
  slot: number
  is_available: boolean
}

export interface FacultyWithAvailability extends Faculty {
  availability: FacultyAvailabilitySlot[]
}

export interface Class {
  id: number
  name: string
  working_days: number
  slots_per_day: number
}

export interface Subject {
  id: number
  name: string
  faculty_id?: number
  faculty_name?: string
}

export interface ClassSubject {
  id: number
  class_id: number
  subject_id: number
  hours_per_week: number
  subject_name?: string
  faculty_name?: string
}

export interface TimetableCell {
  subject_name: string
  faculty_name: string
}

export interface TimetableGrid {
  class_id: number
  class_name: string
  working_days: number
  slots_per_day: number
  grid: (TimetableCell | null)[][]
}

// Faculty
export const facultyApi = {
  list: () => request<Faculty[]>('/faculties'),
  get: (id: number) => request<FacultyWithAvailability>(`/faculties/${id}`),
  create: (body: { name: string; email?: string }) =>
    request<Faculty>('/faculties', { method: 'POST', body: JSON.stringify(body) }),
  update: (id: number, body: { name?: string; email?: string }) =>
    request<Faculty>(`/faculties/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (id: number) =>
    request<void>(`/faculties/${id}`, { method: 'DELETE' }),
  setAvailability: (id: number, slots: { day: number; slot: number; is_available: boolean }[]) =>
    request<FacultyAvailabilitySlot[]>(`/faculties/${id}/availability`, {
      method: 'PUT',
      body: JSON.stringify(slots),
    }),
}

// Classes
export const classApi = {
  list: () => request<Class[]>('/classes'),
  get: (id: number) => request<Class>(`/classes/${id}`),
  create: (body: { name: string; working_days: number; slots_per_day: number }) =>
    request<Class>('/classes', { method: 'POST', body: JSON.stringify(body) }),
  update: (id: number, body: { name?: string; working_days?: number; slots_per_day?: number }) =>
    request<Class>(`/classes/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (id: number) =>
    request<void>(`/classes/${id}`, { method: 'DELETE' }),
}

// Subjects
export const subjectApi = {
  list: () => request<Subject[]>('/subjects'),
  get: (id: number) => request<Subject>(`/subjects/${id}`),
  create: (body: { name: string; faculty_id?: number }) =>
    request<Subject>('/subjects', { method: 'POST', body: JSON.stringify(body) }),
  update: (id: number, body: { name?: string; faculty_id?: number }) =>
    request<Subject>(`/subjects/${id}`, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: (id: number) =>
    request<void>(`/subjects/${id}`, { method: 'DELETE' }),
  listByClass: (classId: number) =>
    request<ClassSubject[]>(`/subjects/classes/${classId}`),
  addToClass: (classId: number, body: { subject_id: number; hours_per_week: number }) =>
    request<ClassSubject>(`/subjects/classes/${classId}/subjects`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),
  updateClassSubject: (classId: number, subjectId: number, body: { hours_per_week?: number }) =>
    request<ClassSubject>(`/subjects/classes/${classId}/subjects/${subjectId}`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    }),
  removeFromClass: (classId: number, subjectId: number) =>
    request<void>(`/subjects/classes/${classId}/subjects/${subjectId}`, { method: 'DELETE' }),
}

// Timetable
export const timetableApi = {
  generate: (classId: number) =>
    request<{ success: boolean; message: string; class_id: number }>('/timetable/generate', {
      method: 'POST',
      body: JSON.stringify({ class_id: classId }),
    }),
  get: (classId: number) => request<TimetableGrid>(`/timetable/${classId}`),
}
