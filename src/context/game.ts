import { createContext, useContext } from 'react'
import type { GameAction, GameState } from '../api/client'

export interface Session {
  loggedIn: boolean
  loading: boolean
  error: string
  notice: string
  login: (username: string, password: string) => Promise<void>
  register: (username: string, password: string) => Promise<boolean>
  logout: () => void
  clearMessages: () => void
}

export interface GameData {
  game: GameState | null
  busy: boolean
  offlineEarnings: string | null
  dismissOffline: () => void
  runAction: (action: GameAction) => Promise<void>
}

export const SessionContext = createContext<Session | null>(null)
export const GameContext = createContext<GameData | null>(null)

export function useSession() {
  const session = useContext(SessionContext)
  if (!session) throw new Error('Session provider is missing.')
  return session
}

export function useGame() {
  const data = useContext(GameContext)
  if (!data?.game) throw new Error('Game is not loaded.')
  return { ...data, game: data.game }
}
