import { useState } from 'react'
import type { GameState, GameAction } from '../api/client'

interface Props { game: GameState; busy: boolean; onAction: (action: GameAction) => Promise<void> }

export function ProgressionPanels({ game, busy, onAction }: Props) {
  const [confirming, setConfirming] = useState(false)
  const stats = game.statistics
  return (
    <>
      <section className="rewards-panel" aria-labelledby="global-heading">
        <h3 id="global-heading">Global upgrades</h3>
        <p><strong>{game.achievement_points} achievement points available</strong></p>
        <p>Permanent bonuses apply to all business income. Global bonuses add together, then multiply with prestige.</p>
        <div className="achievement-list">
          {game.global_upgrades.map(item => (
            <article className="achievement-card" key={item.code}>
              <h4>{item.name}</h4><p>Level {item.level} / {item.max_level}</p>
              <p>+{item.bonus_percent}% global business income per level</p>
              <button type="button" disabled={busy || item.level >= item.max_level || game.achievement_points < item.next_cost}
                onClick={() => void onAction({ type: 'global', code: item.code })}>
                {item.level >= item.max_level ? 'Max level' : `Buy: ${item.next_cost} points`}
              </button>
            </article>
          ))}
        </div>
      </section>
      <section className="rewards-panel" aria-labelledby="prestige-heading">
        <h3 id="prestige-heading">Prestige</h3>
        <p>This run: ${game.prestige.run_earnings} / ${game.prestige.requirement} earned.</p>
        <p>Permanent prestige income multiplier: {game.prestige.current_multiplier}× → {game.prestige.next_multiplier}×</p>
        <p>Prestige resets your cash, owned businesses, and individual business upgrades.
          You keep lifetime statistics, business unlocks, achievement claims, points, global upgrades, and daily reward cooldown.</p>
        {!confirming ? (
          <button type="button" disabled={busy || !game.prestige.available} onClick={() => setConfirming(true)}>
            {game.prestige.available ? 'Review prestige reset' : 'Earn more this run to prestige'}
          </button>
        ) : (
          <div className="prestige-confirm" role="group" aria-label="Confirm prestige reset">
            <p><strong>Reset your current cash and businesses for {game.prestige.next_multiplier}× prestige income?</strong></p>
            <button type="button" disabled={busy || !game.prestige.available} onClick={() => {
              setConfirming(false)
              void onAction({ type: 'prestige' })
            }}>Confirm reset</button>
            <button type="button" disabled={busy} onClick={() => setConfirming(false)}>Cancel</button>
          </div>
        )}
      </section>
      <section className="rewards-panel" aria-labelledby="statistics-heading">
        <h3 id="statistics-heading">Your statistics</h3>
        <dl className="statistics-grid">
          <div><dt>Lifetime cash earned</dt><dd>${stats.lifetime_earnings}</dd></div>
          <div><dt>Cash earned this run</dt><dd>${stats.run_earnings}</dd></div>
          <div><dt>Businesses owned</dt><dd>{stats.businesses_owned}</dd></div>
          <div><dt>Lifetime businesses purchased</dt><dd>{stats.total_businesses_purchased}</dd></div>
          <div><dt>Business upgrades purchased</dt><dd>{stats.total_upgrades_purchased}</dd></div>
          <div><dt>Work actions</dt><dd>{stats.total_work_actions}</dd></div>
          <div><dt>Daily rewards claimed</dt><dd>{stats.total_daily_claims}</dd></div>
          <div><dt>Achievements claimed</dt><dd>{stats.achievements_claimed} / {stats.achievements_total}</dd></div>
          <div><dt>Total points earned</dt><dd>{stats.total_points_earned}</dd></div>
          <div><dt>Points spent</dt><dd>{stats.points_spent}</dd></div>
          <div><dt>Global upgrade levels</dt><dd>{stats.global_upgrade_levels}</dd></div>
          <div><dt>Prestiges</dt><dd>{stats.prestige_count}</dd></div>
        </dl>
      </section>
    </>
  )
}
