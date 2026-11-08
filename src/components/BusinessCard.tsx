import { memo } from 'react'
import type { Business, BuyMode, GameAction } from '../api/client'

interface Props {
  business: Business; mode: BuyMode; canBuy: boolean; canUpgrade: boolean; busy: boolean
  onAction: (action: GameAction) => Promise<void>
}

export const BusinessCard = memo(function BusinessCard({ business, mode, canBuy, canUpgrade, busy, onAction }: Props) {
  const quote = business.quotes[mode]
  return (
    <article className={`business-card ${business.unlocked ? '' : 'locked-card'}`}>
      <h4>{business.name}</h4>
      {business.description && <p>{business.description}</p>}
      {!business.unlocked ? (
        <>
          <p><strong>Locked</strong></p>
          <p>Unlock at ${business.unlock_at} lifetime earnings.</p>
          <button type="button" disabled>Locked</button>
        </>
      ) : (
        <>
          <p>Owned: {business.quantity} · Level {business.upgrade_level}</p>
          <p>Each earns ${business.income_per_second} per second</p>
          <div className="card-actions">
            <button type="button" disabled={busy || !canBuy}
              onClick={() => void onAction({ type: 'buy', id: business.id, quantity: mode })}>
              Buy {quote.quantity} for ${quote.cost}
            </button>
            {business.quantity > 0 && (
              <button type="button"
                disabled={busy || !canUpgrade}
                onClick={() => void onAction({ type: 'upgrade', id: business.id })}>
                {business.upgrade_cost === null ? 'Fully upgraded' : `Double income: $${business.upgrade_cost}`}
              </button>
            )}
          </div>
        </>
      )}
    </article>
  )
})
