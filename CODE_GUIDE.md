# How this code works

## Start here

`frontend/src/App.tsx` chooses between the login form and the game dashboard.

`frontend/src/components/Dashboard.tsx` arranges the balance, daily reward, businesses, upgrades, statistics, and achievements.

## What happens when you click Buy

1. `BusinessCard.tsx` calls `runAction` with the business ID and purchase quantity.
2. `context/GameProvider.tsx` marks the action busy and calls the API client.
3. `api/client.ts` sends a POST request with the login token.
4. Django's router in `game/urls.py` sends the request to `GameViewSet.buy_business`.
5. `PurchaseSerializer` checks the quantity. The view loads only the logged-in player's progress.
6. `services/economy.py` calculates income and the purchase price. Django checks unlocks and affordability.
7. A database transaction saves the money and ownership together.
8. `GameStateSerializer` returns the updated data. Context stores it and React updates the screen.

## Frontend files

- `api/types.ts`: the shapes of API data, such as a Business or Achievement.
- `api/client.ts`: requests and readable error messages. It does not draw anything.
- `context/game.ts`: the Context definitions and the `useSession` / `useGame` hooks.
- `context/GameProvider.tsx`: login state, shared progress, requests, and the once-per-second update timer.
- `components/AuthForm.tsx`: login and registration inputs.
- `components/BusinessCard.tsx`: one business and its Buy/Upgrade buttons.
- `components/Achievements.tsx`: achievement filters and claim buttons.
- `components/ProgressionPanels.tsx`: global upgrades, prestige, and statistics.
- `components/ErrorBoundary.tsx`: a reload message if rendering fails.
- `index.css`: basic page styles. `App.css`: cards and responsive layouts.

The Context provider contains the state and request logic. Most components just display data and call a function when a button is clicked. This keeps the screen files shorter.

## Backend files

- `models.py`: the saved data and relationships. A user has one progress record; a player can own many business types.
- `serializers.py`: checks request inputs and formats responses.
- `views.py`: handles API routes and checks permissions, affordability, and eligibility.
- `services/economy.py`: calculates cash, elapsed income, and purchase prices.
- `services/progression.py`: defines upgrades, unlocks, and prestige.
- `services/rewards.py`: defines achievements, point rewards, and daily eligibility.
- `fields.py`: one small custom field that keeps large decimal amounts exact in SQLite. It is necessary because this game reaches trillions of dollars.
- `management/commands/seed_businesses.py`: adds the 12 starting business types.
- `migrations/`: Django-generated database changes; do not delete these from an existing project.
- `tests.py`: automated checks for the game rules and API.

## Where to make common changes

- Change achievement goals or points: `services/rewards.py`.
- Change global upgrade costs or bonuses: `services/progression.py`.
- Change a business name, description, price, or income: Django admin.
- Change the card color or layout: `frontend/src/App.css`.
- Add a game action: a serializer/view action, the client action type/request, and a button.

Keep all real money calculations and reward checks in Django. The frontend only displays the server's result.
