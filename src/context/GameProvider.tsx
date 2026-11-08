import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import * as api from '../api/client'
import { GameContext, SessionContext } from './game'

function message(error: unknown): string {
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.'
}

export function GameProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState('')
  const [game, setGame] = useState<api.GameState | null>(null)
  const [loading, setLoading] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [connectionError, setConnectionError] = useState('')
  const [notice, setNotice] = useState('')
  const [offlineEarnings, setOfflineEarnings] = useState<string | null>(null)
  const session = useRef(0)
  const revision = useRef(0)
  const actionRunning = useRef(false)

  const clearMessages = useCallback(() => {
    setError('')
    setNotice('')
  }, [])

  const logout = useCallback((reason = '') => {
    session.current += 1
    revision.current += 1
    actionRunning.current = false
    setToken('')
    setGame(null)
    setBusy(false)
    setOfflineEarnings(null)
    setError(reason)
    setConnectionError('')
    setNotice('')
  }, [])

  const updateGame = useCallback((next: api.GameState) => {
    setGame(previous => {
      if (!previous) return next
      const businesses = next.businesses.map(business => {
        const old = previous.businesses.find(item => item.id === business.id)
        return old && JSON.stringify(old) === JSON.stringify(business) ? old : business
      })
      const oldAchievements = new Map(previous.achievements.map(item => [item.code, item]))
      const achievements = next.achievements.map(achievement => {
        const old = oldAchievements.get(achievement.code)
        return old && JSON.stringify(old) === JSON.stringify(achievement) ? old : achievement
      })
      return { ...next, businesses, achievements }
    })
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    clearMessages()
    setLoading(true)
    try {
      const accessToken = await api.login(username, password)
      const progress = await api.getGameState(accessToken)
      session.current += 1
      setGame(progress)
      setToken(accessToken)
      setConnectionError('')
      if (Number(progress.income_earned ?? 0) > 0) setOfflineEarnings(progress.income_earned ?? null)
    } catch (error) {
      setError(message(error))
    } finally {
      setLoading(false)
    }
  }, [clearMessages])

  const register = useCallback(async (username: string, password: string) => {
    clearMessages()
    setLoading(true)
    try {
      await api.register(username, password)
      setNotice('Account created! Log in with your new username and password.')
      return true
    } catch (error) {
      setError(message(error))
      return false
    } finally {
      setLoading(false)
    }
  }, [clearMessages])

  const runAction = useCallback(async (action: api.GameAction) => {
    if (!token || actionRunning.current) return
    const currentSession = session.current
    actionRunning.current = true
    revision.current += 1
    setBusy(true)
    setError('')
    try {
      const next = await api.performAction(token, action)
      if (currentSession === session.current) updateGame(next)
    } catch (error) {
      if (currentSession !== session.current) return
      if (error instanceof api.ApiError && error.status === 401) logout('Your session expired. Please log in again.')
      else setError(message(error))
    } finally {
      if (currentSession === session.current) {
        actionRunning.current = false
        setBusy(false)
      }
    }
  }, [token, logout, updateGame])

  useEffect(() => {
    if (!token) return
    const controller = new AbortController()
    const poll = { running: false, away: false }
    const timer = window.setInterval(async () => {
      if (document.hidden) { poll.away = true; return }
      if (poll.running || actionRunning.current) return
      poll.running = true
      const startedAt = revision.current
      try {
        const next = await api.getGameState(token, controller.signal)
        if (controller.signal.aborted || startedAt !== revision.current) return
        updateGame(next)
        setConnectionError('')
        if (poll.away && Number(next.income_earned ?? 0) > 0) setOfflineEarnings(next.income_earned ?? null)
        poll.away = false
      } catch (error) {
        if (controller.signal.aborted || startedAt !== revision.current) return
        if (error instanceof api.ApiError && error.status === 401) logout('Your session expired. Please log in again.')
        else setConnectionError(message(error))
      } finally {
        poll.running = false
      }
    }, 1000)
    return () => {
      controller.abort()
      window.clearInterval(timer)
    }
  }, [token, logout, updateGame])

  const dismissOffline = useCallback(() => setOfflineEarnings(null), [])
  const loggedIn = Boolean(token && game)
  const sessionValue = useMemo(() => ({
    loggedIn, loading, error: error || connectionError, notice, login, register, logout, clearMessages,
  }), [loggedIn, loading, error, connectionError, notice, login, register, logout, clearMessages])
  const gameValue = useMemo(() => ({ game, busy, offlineEarnings, dismissOffline, runAction }),
    [game, busy, offlineEarnings, dismissOffline, runAction])

  return (
    <SessionContext.Provider value={sessionValue}>
      <GameContext.Provider value={gameValue}>{children}</GameContext.Provider>
    </SessionContext.Provider>
  )
}
