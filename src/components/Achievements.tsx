import { memo, useState } from 'react'
import type { Achievement, GameAction } from '../api/client'

interface Props {
  achievements: Achievement[]; busy: boolean
  onAction: (action: GameAction) => Promise<void>
}

export function Achievements({ achievements, busy, onAction }: Props) {
  const [filter, setFilter] = useState('all')
  const [category, setCategory] = useState('all')
  const visible = achievements.filter(item => {
    if (category !== 'all' && item.category !== category) return false
    if (filter === 'ready') return item.eligible && !item.claimed
    if (filter === 'claimed') return item.claimed
    if (filter === 'unclaimed') return !item.claimed
    return true
  })
  return (
    <section className="rewards-panel" aria-labelledby="achievements-heading">
      <h3 id="achievements-heading">Achievements</h3>
      <p>{achievements.filter(item => item.claimed).length} / {achievements.length} claimed. Harder goals award more points.</p>
      <div className="achievement-filters">
        <label>Status <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="all">All</option><option value="ready">Ready to claim</option>
          <option value="unclaimed">Unclaimed</option><option value="claimed">Claimed</option>
        </select></label>
        <label>Category <select value={category} onChange={e => setCategory(e.target.value)}>
          <option value="all">All categories</option>
          {[...new Set(achievements.map(item => item.category))].map(value => <option key={value}>{value}</option>)}
        </select></label>
      </div>
      {visible.length === 0 && <p>No achievements match these filters.</p>}
      <div className="achievement-list">
        {visible.map(item => <AchievementCard key={item.code} item={item} busy={busy} onAction={onAction} />)}
      </div>
    </section>
  )
}


const AchievementCard = memo(function AchievementCard({ item, busy, onAction }: {
  item: Achievement; busy: boolean; onAction: (action: GameAction) => Promise<void>
}) {
  let label = 'Keep going'
  if (item.eligible) label = 'Claim points'
  if (item.claimed) label = 'Claimed'
  return (
    <article className="achievement-card">
      <h4>{item.name}</h4><p>{item.description}</p>
      <p>Progress: {item.progress} / {item.target}</p>
      <p><strong>{item.points} achievement points</strong></p>
      <button type="button" disabled={busy || item.claimed || !item.eligible}
        onClick={() => void onAction({ type: 'achievement', code: item.code })}>{label}</button>
    </article>
  )
})
