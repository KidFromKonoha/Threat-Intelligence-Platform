export const tokenStorage = {
  getToken: (): string | null => {
    return localStorage.getItem('tip_access_token');
  },
  
  setToken: (token: string): void => {
    localStorage.setItem('tip_access_token', token);
  },
  
  clearToken: (): void => {
    localStorage.removeItem('tip_access_token');
  }
};
