---
name: react-state-management
description: Best practices for modern React state management — choosing between local state, Context, and Redux Toolkit, plus server-state caching (RTK Query / TanStack Query), selectors, performance, and structure. Use this whenever adding or reviewing state in a React app, deciding where state should live, introducing Redux or Context, reaching for a global store, fetching/caching server data, or debugging unnecessary re-renders or prop drilling. Trigger even when the user just says "manage this state", "add a context", "use Redux", or "share this across components" without mentioning best practices. Assumes modern React (function components, hooks) and Redux Toolkit, not legacy Redux.
---

# Modern React State Management

Most React state problems are really *categorization* problems: people put server data in Redux, or app state in Context, or global state where local would do — and then fight re-renders and stale data forever. The first and most important step is to identify **what kind of state** you have, because each kind has a different right tool. Reach for the least powerful option that works.

## Step 1: Categorize the state (this decides everything)

- **Server / remote state** — data owned by the backend (lists, entities, anything you fetch). It's cached, can go stale, and needs revalidation. **Use a data-fetching cache (RTK Query or TanStack Query), not hand-written Redux/Context.** This is the most common mistake — manually storing fetched data in a store and reinventing caching, loading, and invalidation badly.
- **URL state** — current page, filters, sort, selected id. Keep it in the URL (router/query params) so it's shareable and bookmarkable, not duplicated in a store.
- **Local UI state** — open/closed, hover, input focus, a single form's values. Keep it in the component with `useState`/`useReducer`. Don't globalize it.
- **Form state** — use the component or a form library (React Hook Form); rarely belongs in a global store.
- **Shared client/app state** — genuinely cross-cutting client state used by many distant components (auth/user, theme, feature flags, a complex client-side workflow). This is what Context or Redux is actually for.

If state isn't shared, it doesn't need Context or Redux. **Colocate state with the component that uses it and lift it only as far as necessary.**

## Step 2: Pick the tool

- **`useState` / `useReducer`** — default for local state. Use `useReducer` when updates are complex or interdependent.
- **Context** — for low-frequency, widely-read values (theme, current user, locale, DI of services). Great for avoiding prop drilling; **not** a general state manager.
- **Redux Toolkit (RTK)** — for complex, frequently-updated client state shared across the app, where you want devtools/time-travel, middleware, and predictable updates. Use RTK, never legacy hand-written Redux.
- **Lightweight stores (Zustand / Jotai)** — valid alternatives when you need shared client state without Redux's ceremony. Reasonable defaults for small/medium apps; mention them rather than reaching for Redux reflexively.

---

## Context — use it right

Context is dependency injection for React, not a performance-optimized store.

- **Use it for** values that change rarely and are read widely: theme, authenticated user, locale, configuration, service instances.
- **The re-render trap:** every consumer re-renders when the context *value* changes. If the value is a new object every render, all consumers re-render constantly.
  - **Memoize the value** with `useMemo` so its identity is stable.
  - **Split contexts** by update frequency/concern (e.g. separate `AuthContext` from `ThemeContext`, or separate state from dispatch) so a change in one doesn't re-render consumers of the other.
- **Context + `useReducer`** is a clean pattern for modest shared state without Redux: hold state in a reducer, expose state and dispatch via two contexts.
- **Don't** put high-frequency or large app state in a single Context — it causes wide re-renders. That's Redux/Zustand territory.

```tsx
// Split state and dispatch so updates don't re-render dispatch-only consumers
const StateContext = createContext<State | null>(null);
const DispatchContext = createContext<Dispatch<Action> | null>(null);

export function Provider({ children }: PropsWithChildren) {
  const [state, dispatch] = useReducer(reducer, initial);
  return (
    <StateContext.Provider value={state}>
      <DispatchContext.Provider value={dispatch}>{children}</DispatchContext.Provider>
    </StateContext.Provider>
  );
}
```

## Redux — modern (Redux Toolkit only)

- **Always use Redux Toolkit.** Legacy Redux (hand-written action types, switch reducers, manual immutability, `connect` boilerplate) is obsolete. RTK's `configureStore`, `createSlice`, and built-in Immer are the standard.
- **Write slices with `createSlice`.** Reducers look like they mutate state but Immer makes it immutable under the hood — so write straightforward `state.x = y`, but only inside RTK reducers.

```ts
const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    itemAdded(state, action: PayloadAction<Item>) {
      state.items.push(action.payload); // Immer-backed, safe
    },
  },
});
export const { itemAdded } = cartSlice.actions;
```

- **Type everything.** Define `RootState`/`AppDispatch` from the store and export typed `useAppSelector`/`useAppDispatch` hooks; don't use the untyped hooks directly.
- **Organize by feature** (a slice per feature/domain), not by type (no global `actions/`, `reducers/` folders).
- **Async:** use **RTK Query** for server data (it generates hooks with caching, dedup, and invalidation). Use `createAsyncThunk` only for non-data async logic that genuinely belongs in the store. Don't fetch in components and dump results into slices manually.

## Server state — don't reinvent it

- Use **RTK Query** (if you're already on Redux) or **TanStack Query (React Query)** for fetching. They give you caching, request dedup, background revalidation, loading/error states, pagination, and invalidation for free.
- **Don't store server data in Redux/Context by hand** and re-implement these — that's where stale-data and over-fetching bugs come from.
- Keep server state and client state separate concerns; mixing them is a frequent source of confusion.

## Selectors & performance

- **Select narrowly.** `useSelector` re-renders when its selected value changes, so select the smallest slice you need — not the whole store object.
- **Memoize derived/computed selections** with `createSelector` (Reselect, bundled with RTK) so expensive derivations don't recompute and don't return new references each render.
- **Normalize collections** with `createEntityAdapter` (store entities by id) instead of nested arrays — it makes lookups, updates, and memoized selection efficient.
- Watch for selectors that return a new object/array every call (e.g. `.map`/`.filter` inline) — they defeat memoization and cause re-renders.

## Structure & conventions

- Feature-based folders: each feature owns its slice, selectors, and (RTK Query) API endpoints.
- Keep components dumb where possible: read via typed selectors/hooks, dispatch actions; keep logic in slices/thunks/queries.
- One store, composed from feature reducers via `configureStore`.

---

## Decision guide (quick)

1. Is it server data? → RTK Query / TanStack Query.
2. Is it in the URL's concern (filters, current id, page)? → URL/router.
3. Is it used by only one component (or a parent + a couple children)? → `useState`/`useReducer`, lift if needed.
4. Is it low-frequency and widely read (theme, user, locale)? → Context (memoized, split).
5. Is it complex client state shared widely, needing devtools/middleware? → Redux Toolkit (or Zustand/Jotai for less ceremony).

## Review checklist

1. Is each piece of state in the right category/tool (not server data in Redux-by-hand)?
2. Is non-shared state colocated rather than globalized?
3. For Context: is the value memoized and are concerns split to avoid wide re-renders?
4. Is Redux done via RTK (`createSlice`/`configureStore`, Immer), not legacy boilerplate?
5. Is server data fetched via RTK Query / TanStack Query with proper caching/invalidation?
6. Are selectors narrow and memoized; are collections normalized?
7. Are store hooks and state types properly typed?
8. Is URL state kept in the URL, not duplicated in a store?

## Anti-patterns to reject

- Storing fetched server data in Redux/Context and hand-rolling caching/invalidation.
- Using Context as a high-frequency global store (wide re-renders).
- Unmemoized Context values (`value={{ ... }}`) re-rendering all consumers every render.
- Legacy Redux: hand-written action constants, switch reducers, manual immutable spreads, `connect` everywhere.
- Putting purely-local UI state into a global store.
- Mutating state outside RTK reducers (Immer only applies inside them).
- `useSelector` selecting the whole store, or selectors returning fresh objects each call.
- Duplicating URL state (filters, selected id) into Redux/Context.

When unsure where state belongs, ask: *who needs it, how often does it change, and does the server own it?* The answers point to exactly one of useState, URL, Context, a data-fetching cache, or Redux — reach for the least powerful one that fits.
