import './App.css'
import { AuthForm } from './components/AuthForm'
import { Dashboard } from './components/Dashboard'
import { useSession } from './context/game'

export default function App() {
  const { loggedIn, error, notice } = useSession()
  return (
    <main>
      <h1>Idle Tycoon</h1>
      {error && <p className="message error-message" role="alert">{error}</p>}
      {notice && <p className="message" role="status">{notice}</p>}
      {loggedIn ? <Dashboard /> : <AuthForm />}
    </main>
  )
}
