# Purpose

This document serves as the permanent architectural rulebook for the frontend of the Threat Intelligence Platform (TIP). It is not an implementation log. It documents the conventions, structures, and guidelines established during Phase F1 that must be strictly followed throughout the lifetime of the project.

# Directory Structure

The frontend utilizes a feature-based architecture.
Code is grouped by the domain feature it belongs to rather than technical concerns, except for global infrastructure.

```
src/
  api/          # Axios client and interceptors
  app/          # Global setup (e.g., router, query-client)
  components/   # Reusable, domain-agnostic UI (common, layout, feedback, ui)
  config/       # Static application configuration
  features/     # Feature-based domain code (dashboard, search, etc.)
  hooks/        # Global hooks
  layouts/      # Application shell definitions
  providers/    # Context providers
  services/     # Global services (e.g., token storage)
  styles/       # CSS tokens and globals
  types/        # Global types
  utils/        # Global utilities
```

# Component Guidelines

- **Presentation vs Business Logic**: Components should remain purely presentational. Move business logic to hooks or utility functions.
- **Composition over Inheritance**: Build complex UIs by composing smaller components instead of creating monolithic components with excessive props.
- **Small Reusable Components**: Keep files small and focused. Extract shared UI logic into `src/components/`.
- **Strict TypeScript**: No `any`. Type everything explicitly.

# Routing

- **Protected Routes**: Handled via the `<ProtectedRoute>` wrapper, which intercepts unauthenticated users and redirects them.
- **Layout Hierarchy**: Routes are deeply nested inside `<AppLayout>` to provide the application shell (Sidebar, Top Navigation).
- **Feature Routing**: Routes should point to feature pages exported from `src/features/<feature_name>/pages/`.

# API Layer

- **Axios Client**: The canonical instance is exported from `src/api/client.ts`. It includes baseline configuration like timeouts.
- **Interceptors**: Located in `src/api/interceptors.ts`, responsible for injecting authorization headers from token storage and handling global error responses.
- **Future API Module Organization**: Each feature will eventually house its own specific API calls in `src/features/<feature_name>/api/`.

# Authentication

- **Provider Responsibilities**: The `AuthProvider` (`src/providers/auth-provider.tsx`) is solely responsible for determining authenticated state and exposing it via context. It does not render forms.
- **Token Storage**: Managed via the abstraction `src/services/auth/token-storage.ts`.
- **Future Refresh Flow**: To be implemented as an Axios response interceptor that transparently requests and stores a new token without component intervention.

# TanStack Query

- **Server State Conventions**: Use TanStack Query exclusively for server state. Do not use local state (`useState` / `useEffect`) for data fetching.
- **Query Keys**: Must be strictly typed and consistently structured (e.g., arrays).
- **Mutation Conventions**: Use `useMutation` for writes, and ensure queries are invalidated on success to keep the UI fresh.

# Styling

- **Dark-First**: The UI defaults to a dark mode tailored for SOC analysts.
- **Information-Dense UI**: Prioritize compactness and density. Utilize smaller fonts, reduced padding, and sharp layouts.
- **Design Tokens**: Configured in `src/styles/tokens.css` using Tailwind v4 inline themes.
- **Global Styles**: Defined in `src/styles/globals.css`.
- **Strict Rules**: No gradients, no oversized cards, and no colorful widgets. Maintain a highly professional and analytical appearance.

# Naming Conventions

- **Filenames**: Always use `kebab-case` for all files (e.g., `auth-provider.tsx`, `page-loader.tsx`). Avoid PascalCase filenames.
- **Component Naming**: Use PascalCase for the exported React component names inside the files (e.g., `export const PageLoader = ...`).
- **Folder Naming**: Use `kebab-case` for all directories.

# Error Handling

Use the standard suite of reusable feedback primitives located in `src/components/feedback/`:
- **`PageLoader`**: Full page or block-level loading state.
- **`PageSkeleton`**: Skeleton structure for initial data loads.
- **`PageError`**: Rendering API failures or unexpected states.
- **`EmptyState`**: Rendering when a list is empty or a search returns no results.
- **`ErrorBoundary`**: Catching unhandled React runtime errors to prevent application crashes.

# Future Feature Structure

Every new feature introduced in future phases must conform to the following standard structure within `src/features/<feature-name>/`:

```
features/
  feature-name/
    api/         # Feature-specific Axios calls
    components/  # Feature-specific UI
    hooks/       # Feature-specific React hooks
    pages/       # Feature-specific route entrypoints
    types/       # Feature-specific TypeScript interfaces
    utils/       # Feature-specific helper functions
```

This structure ensures the frontend scales gracefully across subsequent phases without necessitating massive restructuring.
