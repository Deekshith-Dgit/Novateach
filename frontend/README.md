# React + Vite

## Novateach deployment configuration

The frontend calls the API using `VITE_API_BASE_URL`. Set it in the frontend
hosting provider to the deployed backend's origin, including `https://` and
without a trailing slash. For local development, the app defaults to
`http://127.0.0.1:8000`.

Set `FRONTEND_ORIGIN` in the backend hosting provider to the deployed
frontend's origin, including `https://` and without a path. The API uses this
value for CORS and continues to allow the local Vite development origins.

After changing `VITE_API_BASE_URL`, rebuild/redeploy the frontend. Restart or
redeploy the backend after changing `FRONTEND_ORIGIN`.

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.
