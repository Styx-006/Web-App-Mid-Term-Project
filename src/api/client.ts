import type { GameAction, GameState } from './types'
export type * from './types'

const API_URL = import.meta.env?.VITE_API_URL ?? 'http://127.0.0.1:8000/api'

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

async function request<T>(path: string, token = '', body?: object, signal?: AbortSignal): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}/${path}`, {
      method: body ? 'POST' : 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: body ? JSON.stringify(body) : undefined,
      signal,
    })
  } catch (error) {
    if (signal?.aborted) throw error
    throw new Error('Cannot reach the server. Check that Django is running.')
  }

  const data: unknown = await response.json().catch(() => null)
  if (!response.ok) {
    let message = 'The request failed. Please try again.'
    if (response.status >= 500) {
      message = 'The server had a problem. Please try again shortly.'
    } else if (data && typeof data === 'object') {
      message = Object.entries(data).map(([field, value]) => {
        const text = Array.isArray(value) ? value.join(' ') : String(value)
        return field === 'detail' ? text : `${field}: ${text}`
      }).join(' ')
    }
    throw new ApiError(message, response.status)
  }
  if (data === null) throw new Error('The server returned an invalid response.')
  return data as T
}

export async function login(username: string, password: string): Promise<string> {
  const data = await request<{ access: string }>('accounts/login/', '', { username, password })
  return data.access
}

export function register(username: string, password: string): Promise<{ id: number; username: string }> {
  return request('accounts/register/', '', { username, password })
}

export function getGameState(token: string, signal?: AbortSignal): Promise<GameState> {
  return request('game/state/', token, undefined, signal)
}

export function performAction(token: string, action: GameAction): Promise<GameState> {
  switch (action.type) {
    case 'work': return request('game/work/', token, {})
    case 'daily': return request('game/rewards/daily/', token, {})
    case 'achievement': return request(`game/achievements/${encodeURIComponent(action.code)}/claim/`, token, {})
    case 'buy': return request(`game/businesses/${action.id}/buy/`, token, { quantity: action.quantity })
    case 'upgrade': return request(`game/businesses/${action.id}/upgrade/`, token, {})
    case 'global': return request(`game/global-upgrades/${encodeURIComponent(action.code)}/buy/`, token, {})
    case 'prestige': return request('game/prestige/', token, { confirm: true })
  }
}
