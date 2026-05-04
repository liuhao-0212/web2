import { clearToken, getToken } from "./auth";

/** 开发默认 "/api"，由 Vite 代理到 Flask；打包直连后端时可在 frontend/.env 设置 VITE_API_BASE */
const raw = import.meta.env.VITE_API_BASE ?? "/api";
const base = raw.replace(/\/$/, "");

export function authHeaders() {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

async function fetchWithAuth(url, options = {}) {
  const headers = {
    Accept: "application/json",
    ...(options.headers || {}),
    ...authHeaders(),
  };
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    clearToken();
    const err = new Error("登录已失效或未登录");
    err.name = "Unauthorized";
    throw err;
  }
  return res;
}

export async function fetchMe() {
  const res = await fetchWithAuth(`${base}/auth/me`);
  return res.json();
}

export async function login(username, password) {
  const res = await fetch(`${base}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `登录失败 (${res.status})`);
  return data;
}

export async function register(username, password) {
  const res = await fetch(`${base}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `注册失败 (${res.status})`);
  return data;
}

export async function fetchProducts() {
  const res = await fetch(`${base}/products`);
  if (!res.ok) throw new Error(`加载商品失败: ${res.status}`);
  const data = await res.json();
  return data.items ?? [];
}

export async function createProduct(payload) {
  const res = await fetchWithAuth(`${base}/products`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `上架失败: ${res.status}`);
  return data;
}

export async function placeOrder(productId, quantity) {
  const res = await fetchWithAuth(`${base}/orders`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ product_id: productId, quantity }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `下单失败: ${res.status}`);
  return data;
}
