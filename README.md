# Frontend

React + TypeScript + plain CSS. Strict TypeScript is enabled.

```powershell
npm.cmd install
npm.cmd run dev
```

Open http://127.0.0.1:5173 and keep Django running on port 8000.

Copy `.env.example` to `.env` only if you need to change `VITE_API_URL`.

```powershell
npm.cmd test
npm.cmd run build
npm.cmd run lint
```

The tests use Node's built-in test runner (Node 24 recommended), with no extra test libraries.

See `../CODE_GUIDE.md` for a short explanation of the files and `../README.md` for the full setup.
