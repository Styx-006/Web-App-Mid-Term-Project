export type BuyMode = '1' | '10' | 'max'
export interface PurchaseQuote {
  quantity: number
  cost: string
}
export interface Achievement {
  code: string
  name: string
  description: string
  progress: string
  target: string
  points: number
  category: string
  eligible: boolean
  claimed: boolean
}

export interface Business {
  unlocked: boolean
  unlock_at: string
  upgrade_level: number
  max_upgrade_level: number
  upgrade_cost: string | null
  quotes: Record<BuyMode, PurchaseQuote>
  id: number
  name: string
  description: string
  quantity: number
  next_price: string
  income_per_second: string
}

export interface GameState {
  username: string
  money: string
  lifetime_earnings: string
  income_per_second: string
  income_earned?: string
  achievements: Achievement[]
  daily_reward: { amount: string
  available: boolean
  next_claim_at: string | null }
  achievement_points: number
  income_multiplier: string
  global_upgrades: GlobalUpgrade[]
  prestige: Prestige
  statistics: Statistics
  businesses: Business[]
}

export interface GlobalUpgrade {
  code: string
  name: string
  level: number
  max_level: number
  bonus_percent: number
  next_cost: number
}
export interface Prestige {
  available: boolean
  requirement: string
  run_earnings: string
  current_multiplier: string
  next_multiplier: string
}
export interface Statistics {
  lifetime_earnings: string
  run_earnings: string
  total_businesses_purchased: number
  businesses_owned: number
  total_upgrades_purchased: number
  total_work_actions: number
  total_daily_claims: number
  achievements_claimed: number
  achievements_total: number
  total_points_earned: number
  points_spent: number
  global_upgrade_levels: number
  prestige_count: number
}
export type GameAction =
  | { type: 'work' | 'daily' | 'prestige' }
  | { type: 'buy'
  id: number
  quantity: BuyMode }
  | { type: 'upgrade'
  id: number }
  | { type: 'achievement' | 'global'
  code: string }

