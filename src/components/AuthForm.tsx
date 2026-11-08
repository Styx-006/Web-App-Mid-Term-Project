import { useState, type FormEvent } from 'react'
import { useSession } from '../context/game'

export function AuthForm() {
  const session = useSession()
  const [registering, setRegistering] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    if (registering && password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }
    if (registering) {
      const created = await session.register(username, password)
      if (created) {
        setRegistering(false)
        setPassword('')
        setConfirmPassword('')
      }
    } else {
      await session.login(username, password)
    }
  }

  function toggleMode() {
    setRegistering(!registering)
    setPassword('')
    setConfirmPassword('')
    setError('')
    session.clearMessages()
  }

  return (
    <form className="auth-form" onSubmit={submit}>
      <h2>{registering ? 'Create an account' : 'Log in'}</h2>
      {error && <p role="alert">{error}</p>}
      <label>Username
        <input autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} required />
      </label>
      <label>Password
        <input type="password" autoComplete={registering ? 'new-password' : 'current-password'}
          value={password} onChange={e => setPassword(e.target.value)} required />
      </label>
      {registering && (
        <>
          <label>Confirm password
            <input type="password" autoComplete="new-password" value={confirmPassword}
              onChange={e => setConfirmPassword(e.target.value)} required />
          </label>
          <p>Use at least 8 characters. Avoid common passwords and your username.</p>
        </>
      )}
      <button type="submit" disabled={session.loading}>
        {session.loading ? 'Please wait…' : registering ? 'Create account' : 'Log in'}
      </button>
      <button type="button" disabled={session.loading} onClick={toggleMode}>
        {registering ? 'Already have an account? Log in' : 'New player? Create an account'}
      </button>
    </form>
  )
}
