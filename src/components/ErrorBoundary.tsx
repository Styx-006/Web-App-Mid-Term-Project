import { Component, type ReactNode } from 'react'

export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  render() {
    if (this.state.failed) {
      return <main><h1>Idle Tycoon</h1><p role="alert">Something went wrong. Reload the game to try again.</p>
        <button type="button" onClick={() => window.location.reload()}>Reload game</button></main>
    }
    return this.props.children
  }
}
