export function canAfford(balance: string, cost: string | null): boolean {
  if (cost === null) return false
  return BigInt(balance.replace('.', '')) >= BigInt(cost.replace('.', ''))
}
