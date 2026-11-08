import assert from 'node:assert/strict'
import { afterEach, test } from 'node:test'
import { ApiError, getGameState, login, performAction, register } from '../src/api/client.ts'
import { canAfford } from '../src/money.ts'

const originalFetch = globalThis.fetch

afterEach(() => { globalThis.fetch = originalFetch })

function respond(status, body) {
  globalThis.fetch = async () => new Response(JSON.stringify(body), {
    status, headers: { 'Content-Type': 'application/json' },
  })
}

test('login sends credentials and returns the access token', async () => {
  globalThis.fetch = async (url, options) => {
    assert.match(url, /accounts\/login\/$/)
    assert.equal(options.method, 'POST')
    assert.deepEqual(JSON.parse(options.body), { username: 'student', password: 'test-password' })
    return new Response(JSON.stringify({ access: 'test-access' }))
  }
  assert.equal(await login('student', 'test-password'), 'test-access')
})

test('bulk purchase sends quantity and authentication', async () => {
  globalThis.fetch = async (url, options) => {
    assert.match(url, /businesses\/12\/buy\/$/)
    assert.equal(options.headers.Authorization, 'Bearer test-token')
    assert.deepEqual(JSON.parse(options.body), { quantity: '10' })
    return new Response(JSON.stringify({ money: '100.00' }))
  }
  assert.equal((await performAction('test-token', { type: 'buy', id: 12, quantity: '10' })).money, '100.00')
})

for (const status of [400, 401, 403, 404]) {
  test(`HTTP ${status} is exposed as a readable API error`, async () => {
    respond(status, { detail: 'Test error message' })
    await assert.rejects(() => getGameState('test-token'), error =>
      error instanceof ApiError && error.status === status && error.message === 'Test error message')
  })
}

test('registration explains field validation errors', async () => {
  respond(400, { password: ['Use a stronger password.'] })
  await assert.rejects(() => register('student', 'short'), /password: Use a stronger password/)
})

test('HTTP 500 does not show server internals', async () => {
  respond(500, { detail: 'Private database error' })
  await assert.rejects(() => getGameState('test-token'), error =>
    error.status === 500 && error.message === 'The server had a problem. Please try again shortly.')
})

test('unavailable server gives actionable feedback', async () => {
  globalThis.fetch = async () => { throw new TypeError('fetch failed') }
  await assert.rejects(() => getGameState('test-token'), /Check that Django is running/)
})

test('cancelled polls are not treated as connection errors', async () => {
  const controller = new AbortController()
  controller.abort()
  globalThis.fetch = async () => { throw new DOMException('Aborted', 'AbortError') }
  await assert.rejects(() => getGameState('test-token', controller.signal), { name: 'AbortError' })
})

test('late-game affordability keeps every cent', () => {
  assert.equal(canAfford('9999999999999999999999.98', '9999999999999999999999.99'), false)
  assert.equal(canAfford('9999999999999999999999.99', '9999999999999999999999.99'), true)
  assert.equal(canAfford('10.00', '11.50'), false)
  assert.equal(canAfford('11.50', '11.50'), true)
  assert.equal(canAfford('999.00', null), false)
})
