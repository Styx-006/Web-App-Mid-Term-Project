# Idle Tycoon

## Run locally

In backend PowerShell:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

In a separate frontend PowerShell: `npm.cmd run dev`. Open http://127.0.0.1:5173. Keep both servers running.

For a fresh checkout, install Python, create `.venv`, install `requirements.txt`, copy `.env.example` to `.env`, set a random secret, and run migrations. An optional admin account can be created with `manage.py createsuperuser`. Exclude secrets, local databases, virtual environments, and node_modules from Git. Deployment requires production settings.

## Progression rules

- Work: $1, with one paid action per second.
- Purchases: 15% price growth per copy. Buy 10 sums individually rounded prices. Buy Max purchases only affordable copies.
- Passive income: elapsed whole seconds, calculated by the server. Rate changes settle the previous rate first and discard the fractional second. Repeated reads do not double-credit income.
- Unlocks: lifetime earnings of one tenth of base business price; businesses priced at $10 or less start unlocked. Previously discovered businesses stay unlocked through prestige.
- Individual upgrades: 10 levels, doubling income for all copies per level. First upgrade costs 10 times the business base price; later costs triple.
- Achievements: 50 general goals plus one discovery goal per business (62 total for 12 businesses). Claims award points instead of cash. General awards range from 5 to 450 points. Business discovery awards rise from 5 to 720 points with business difficulty. Each claim is unique per player and achievement code.
- Global upgrades: six choices, three levels each, purchased with achievement points. Level costs double. Percentage bonuses add together, then multiply with prestige. Global upgrades and points survive prestige.
- Prestige: first threshold $1,000,000 earned this run; thresholds increase tenfold up to $1,000,000,000,000,000,000,000. Each prestige adds 0.25 to the permanent multiplier (1.00x, 1.25x, 1.50x...). UI confirmation and a boolean API confirmation are required.
- Prestige resets cash, businesses, individual upgrades, and run earnings. It retains lifetime statistics, discoveries/unlocks, achievement claims, points, global upgrades, and daily cooldown.
- Daily reward: $100 per 24 hours using server time.
- Currency: exact decimal text on SQLite avoids late-game floating point precision loss. Balances and earnings cap at $9,999,999,999,999,999,999,999.99. Business prices are sorted numerically in Python.

## Existing saves

Migrations preserve cash, ownership, and claims. Previously claimed achievements receive their new points once; historical cash awards remain. Initial purchase totals use current ownership; run earnings use lifetime earnings. Historical work and full daily-claim counts were not stored: work tracking begins with this update, and the known prior daily claim counts as one. New counters persist across prestige.

## API

Account routes: POST `/api/accounts/register/`, `/api/accounts/login/`, and `/api/accounts/token/refresh/`.

Authenticated game routes:

- GET `/api/game/state/`: state, quotes, upgrades, achievements, daily status, prestige, statistics, and elapsed income.
- POST `/api/game/work/`.
- POST `/api/game/businesses/<id>/buy/`: string quantity `1`, `10`, or `max`.
- POST `/api/game/businesses/<id>/upgrade/`.
- POST `/api/game/global-upgrades/<code>/buy/`.
- POST `/api/game/rewards/daily/`.
- POST `/api/game/achievements/<code>/claim/`.
- POST `/api/game/prestige/`: JSON boolean `confirm: true`.

Use an Authorization Bearer access token. Session authentication is also enabled for browsable API testing, with CSRF protection. All purchases, rewards, and resets use transactions. SQLite uses IMMEDIATE transactions; row-locking calls support PostgreSQL.

## Frontend and validation

Business cards, achievement filters, and progression/statistics panels have separate typed React components. Expired sessions return to login. Offline summaries show cash already credited by the server.

Run `manage.py test` and `manage.py check` with the virtual environment Python. From frontend, run `npm.cmd run build` and `npm.cmd run lint`.
