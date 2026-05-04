import { ref } from "vue";

const TOKEN_KEY = "web1_token";

export const currentUser = ref(null);

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function setSession(token, user) {
  setToken(token);
  currentUser.value = user;
}

export function clearSession() {
  clearToken();
  currentUser.value = null;
}
