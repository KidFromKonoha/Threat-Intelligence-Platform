// Custom event dispatched when a refresh token fails or session expires.
// This decouples the Axios interceptor from React context and navigation.

export const AUTH_EVENTS = {
  UNAUTHORIZED: 'tip:auth:unauthorized',
} as const;

export const dispatchUnauthorized = () => {
  window.dispatchEvent(new CustomEvent(AUTH_EVENTS.UNAUTHORIZED));
};
