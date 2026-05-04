<script setup>
import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { login, register as apiRegister } from "../api";
import { setSession } from "../auth";

const router = useRouter();
const route = useRoute();

const mode = ref("login");
const username = ref("");
const password = ref("");
const loading = ref(false);
const error = ref("");

const title = computed(() => (mode.value === "login" ? "登录" : "注册"));

async function submit() {
  loading.value = true;
  error.value = "";
  try {
    const u = username.value.trim();
    const p = password.value;
    const data =
      mode.value === "login"
        ? await login(u, p)
        : await apiRegister(u, p);
    setSession(data.token, data.user);
    const redirect = route.query.redirect;
    router.replace(typeof redirect === "string" && redirect.startsWith("/") ? redirect : "/");
  } catch (e) {
    error.value = e.message || String(e);
  } finally {
    loading.value = false;
  }
}

function toggleMode() {
  mode.value = mode.value === "login" ? "register" : "login";
  error.value = "";
}
</script>

<template>
  <div class="login-page">
    <div class="card">
      <h1>{{ title }}</h1>
      <p class="hint">演示账号：<code>demo</code> / <code>demo123</code></p>

      <form class="form" @submit.prevent="submit">
        <label class="field">
          <span>用户名</span>
          <input v-model="username" type="text" autocomplete="username" maxlength="64" required />
        </label>
        <label class="field">
          <span>密码</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            :minlength="mode === 'register' ? 6 : 1"
            required
          />
        </label>
        <p v-if="error" class="err">{{ error }}</p>
        <button type="submit" class="btn primary" :disabled="loading">
          {{ loading ? "提交中…" : title }}
        </button>
      </form>

      <button type="button" class="link" @click="toggleMode">
        {{ mode === "login" ? "没有账号？注册" : "已有账号？登录" }}
      </button>

      <router-link class="back" to="/">← 返回商城</router-link>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: calc(100vh - 56px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 2rem 1.75rem;
  box-shadow: 0 8px 32px rgba(15, 23, 42, 0.08);
  border: 1px solid #f1f5f9;
}

h1 {
  margin: 0 0 0.5rem;
  font-size: 1.5rem;
  text-align: center;
}

.hint {
  margin: 0 0 1.25rem;
  font-size: 0.85rem;
  color: #64748b;
  text-align: center;
}

.hint code {
  background: #f1f5f9;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field span {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.35rem;
}

.field input {
  width: 100%;
  padding: 0.6rem 0.75rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font: inherit;
}

.field input:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.18);
}

.err {
  margin: 0;
  font-size: 0.88rem;
  color: #b91c1c;
}

.btn {
  padding: 0.65rem 1rem;
  border-radius: 10px;
  border: none;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.btn.primary {
  background: linear-gradient(120deg, #ea580c, #c026d3);
  color: #fff;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.link {
  display: block;
  margin-top: 1rem;
  width: 100%;
  background: none;
  border: none;
  color: #7c3aed;
  font-size: 0.92rem;
  cursor: pointer;
  text-decoration: underline;
}

.back {
  display: block;
  margin-top: 1.25rem;
  text-align: center;
  font-size: 0.9rem;
  color: #64748b;
}
</style>
