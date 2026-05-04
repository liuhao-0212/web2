<script setup>
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { currentUser, getToken, clearSession } from "./auth";
import { fetchMe } from "./api";

const router = useRouter();

async function refreshUser() {
  if (!getToken()) {
    currentUser.value = null;
    return;
  }
  try {
    const { user } = await fetchMe();
    currentUser.value = user;
  } catch {
    clearSession();
  }
}

function logout() {
  clearSession();
  router.push("/");
}

onMounted(refreshUser);
</script>

<template>
  <div class="shell">
    <header class="topnav">
      <router-link class="brand" to="/">优选商城</router-link>
      <nav class="nav-actions">
        <template v-if="currentUser">
          <span class="who">{{ currentUser.username }}</span>
          <button type="button" class="btn-logout" @click="logout">退出</button>
        </template>
        <router-link v-else class="btn-login" to="/login">登录</router-link>
      </nav>
    </header>
    <router-view />
  </div>
</template>

<style>
:root {
  font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
  color: #0f172a;
  background: linear-gradient(160deg, #fff7ed 0%, #f8fafc 45%, #eef2ff 100%);
  line-height: 1.5;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
}

.shell {
  min-height: 100vh;
}

.topnav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.65rem 1.25rem;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #f1f5f9;
  position: sticky;
  top: 0;
  z-index: 10;
}

.brand {
  font-weight: 800;
  font-size: 1.05rem;
  text-decoration: none;
  background: linear-gradient(105deg, #ea580c, #7c3aed);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.who {
  font-size: 0.9rem;
  color: #475569;
}

.btn-login {
  padding: 0.4rem 0.9rem;
  border-radius: 8px;
  background: linear-gradient(120deg, #ea580c, #c026d3);
  color: #fff !important;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.88rem;
}

.btn-logout {
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
  font: inherit;
  font-size: 0.85rem;
  cursor: pointer;
  color: #64748b;
}

.btn-logout:hover {
  background: #f8fafc;
}
</style>
