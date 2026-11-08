import { memo, useState } from 'react'
import type { BuyMode } from '../api/client'
import { useGame, useSession } from '../context/game'
import { canAfford } from '../money'
import { BusinessCard } from './BusinessCard'
import { Achievements } from './Achievements'
import { ProgressionPanels } from './ProgressionPanels'

function BalancePanel() {
  const { game, busy, runAction, offlineEarnings, dismissOffline } = useGame()
  const { logout } = useSession()
  return (
    <section aria-label="Player balance">
      <h2>Welcome, {game.username}!</h2>
      <button className="logout-button" type="button" onClick={() => logout()}>Log out</button>
      {offlineEarnings !== null && (
        <aside className="offline-summary" aria-label="Offline earnings">
          <h3>Welcome back!</h3>
          <p>Your businesses earned <strong>${offlineEarnings}</strong> while you were away.</p>
          <p>This money is already included in your balance.</p>
          <button type="button" onClick={dismissOffline}>Got it</button>
        </aside>
      )}
      <p>Money: ${game.money}</p>
      <p>Income: ${game.income_per_second} per second · {game.income_multiplier}× bonus multiplier</p>
      <p><strong>Achievement points: {game.achievement_points}</strong></p>
      <button type="button" disabled={busy} onClick={() => void runAction({ type: 'work' })}>Work (+$1)</button>
      <p>Work once per second. Your balance updates automatically.</p>
    </section>
  )
}

function DailyReward() {
  const { game, busy, runAction } = useGame()
  const reward = game.daily_reward
  return (
    <section className="rewards-panel" aria-labelledby="daily-heading">
      <h3 id="daily-heading">Daily reward</h3>
      <p>Collect ${reward.amount} once every 24 hours.</p>
      {!reward.available && reward.next_claim_at && <p>Next reward: {new Date(reward.next_claim_at).toLocaleString()}</p>}
      <button type="button" disabled={busy || !reward.available} onClick={() => void runAction({ type: 'daily' })}>
        {reward.available ? `Claim $${reward.amount}` : 'Daily reward claimed'}
      </button>
    </section>
  )
}

function BusinessList() {
  const { game, busy, runAction } = useGame()
  const [mode, setMode] = useState<BuyMode>('1')
  return (
    <section aria-labelledby="business-heading">
      <h3 id="business-heading">Your businesses</h3>
      <fieldset className="bulk-controls" disabled={busy}>
        <legend>Purchase quantity</legend>
        {(['1', '10', 'max'] as const).map(value => (
          <label key={value}>
            <input type="radio" name="buy-mode" checked={mode === value} onChange={() => setMode(value)} />
            Buy {value === 'max' ? 'Max' : value}
          </label>
        ))}
      </fieldset>
      <div className="business-grid">
        {game.businesses.map(business => (
          <BusinessCard key={business.id} business={business} mode={mode} busy={busy} onAction={runAction}
            canBuy={business.quotes[mode].quantity > 0 && canAfford(game.money, business.quotes[mode].cost)}
            canUpgrade={canAfford(game.money, business.upgrade_cost)} />
        ))}
      </div>
    </section>
  )
}

function ProgressionSection() {
  const { game, busy, runAction } = useGame()
  return <ProgressionPanels game={game} busy={busy} onAction={runAction} />
}

function AchievementsSection() {
  const { game, busy, runAction } = useGame()
  return <Achievements achievements={game.achievements} busy={busy} onAction={runAction} />
}
export const Dashboard = memo(function Dashboard() {
  return <><BalancePanel /><DailyReward /><BusinessList /><ProgressionSection /><AchievementsSection /></>
})
