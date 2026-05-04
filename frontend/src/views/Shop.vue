<script setup>
import { ref, onMounted, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { fetchProducts, createProduct, placeOrder } from "../api";

const route = useRoute();
const router = useRouter();

const products = ref([]);
const loading = ref(false);
const error = ref("");
const success = ref("");
const orderingId = ref(null);

const newProduct = reactive({
  name: "",
  description: "",
  price: "",
  stock: "",
  image_url: "",
});
const saving = ref(false);

const qtyById = reactive({});
const imageFailed = reactive({});

function money(n) {
  try {
    return new Intl.NumberFormat("zh-CN", {
      style: "currency",
      currency: "CNY",
    }).format(Number(n));
  } catch {
    return `¥${n}`;
  }
}

function toLogin() {
  router.push({ path: "/login", query: { redirect: route.fullPath } });
}

function handleAuthError(e) {
  if (e.name === "Unauthorized") {
    toLogin();
    return true;
  }
  return false;
}

async function load() {
  loading.value = true;
  error.value = "";
  success.value = "";
  try {
    products.value = await fetchProducts();
    for (const p of products.value) {
      if (qtyById[p.id] == null) qtyById[p.id] = 1;
    }
  } catch (e) {
    error.value = e.message || String(e);
  } finally {
    loading.value = false;
  }
}

async function onBuy(p) {
  const q = Math.max(1, parseInt(String(qtyById[p.id] || 1), 10) || 1);
  orderingId.value = p.id;
  error.value = "";
  success.value = "";
  try {
    const res = await placeOrder(p.id, q);
    success.value = `订单 #${res.order.id} 已生成，合计 ${money(res.order.total)}`;
    await load();
  } catch (e) {
    if (handleAuthError(e)) {
      error.value = "请先登录后再下单";
    } else {
      error.value = e.message || String(e);
    }
  } finally {
    orderingId.value = null;
  }
}

async function onCreateProduct() {
  saving.value = true;
  error.value = "";
  success.value = "";
  try {
    const price = Number(newProduct.price);
    const stock = parseInt(String(newProduct.stock), 10);
    await createProduct({
      name: newProduct.name.trim(),
      description: newProduct.description.trim(),
      price,
      stock,
      image_url: newProduct.image_url.trim() || undefined,
    });
    newProduct.name = "";
    newProduct.description = "";
    newProduct.price = "";
    newProduct.stock = "";
    newProduct.image_url = "";
    success.value = "商品已上架";
    await load();
  } catch (e) {
    if (handleAuthError(e)) {
      error.value = "请先登录后再上架商品";
    } else {
      error.value = e.message || String(e);
    }
  } finally {
    saving.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="page">
    <header class="hero">
      <div class="hero-inner">
        <p class="badge">Flask · Vue · MySQL</p>
        <h1>优选商城</h1>
        <p class="tagline">登录后可上架商品、下单购买</p>
      </div>
    </header>

    <section class="card panel">
      <h2 class="panel-title">商家上架 <span class="subtip">（需登录）</span></h2>
      <div class="form-grid">
        <label class="field">
          <span>商品名称</span>
          <input v-model="newProduct.name" type="text" maxlength="200" placeholder="例如：不锈钢吸管杯" />
        </label>
        <label class="field">
          <span>单价（元）</span>
          <input v-model="newProduct.price" type="number" min="0" step="0.01" placeholder="99.00" />
        </label>
        <label class="field">
          <span>库存</span>
          <input v-model="newProduct.stock" type="number" min="0" step="1" placeholder="100" />
        </label>
        <label class="field wide">
          <span>图片 URL（可选）</span>
          <input v-model="newProduct.image_url" type="url" placeholder="https://..." />
        </label>
        <label class="field wide">
          <span>商品描述</span>
          <textarea v-model="newProduct.description" rows="2" maxlength="5000" placeholder="卖点、规格等" />
        </label>
      </div>
      <button type="button" class="btn accent" :disabled="saving || !newProduct.name.trim()" @click="onCreateProduct">
        {{ saving ? "提交中…" : "上架商品" }}
      </button>
    </section>

    <p v-if="error" class="banner error">{{ error }}</p>
    <p v-if="success" class="banner ok">{{ success }}</p>

    <section class="toolbar">
      <h2>在售商品</h2>
      <button type="button" class="btn ghost" :disabled="loading" @click="load">
        {{ loading ? "刷新中…" : "刷新列表" }}
      </button>
    </section>

    <div v-if="loading && !products.length" class="empty-block">加载中…</div>
    <div v-else-if="!products.length" class="empty-block">暂无商品，请先上架或检查后端与数据库连接。</div>
    <ul v-else class="grid">
      <li v-for="p in products" :key="p.id" class="product">
        <div class="thumb-wrap">
          <img
            v-if="p.image_url && !imageFailed[p.id]"
            class="thumb"
            :src="p.image_url"
            :alt="p.name"
            loading="lazy"
            @error="imageFailed[p.id] = true"
          />
          <div v-else class="thumb placeholder">
            {{ p.image_url ? "图片不可用" : "无图" }}
          </div>
        </div>
        <div class="body">
          <h3 class="name">{{ p.name }}</h3>
          <p class="desc">{{ p.description || "暂无描述" }}</p>
          <div class="meta">
            <span class="price">{{ money(p.price) }}</span>
            <span class="stock">库存 {{ p.stock }}</span>
          </div>
          <div class="buy-row">
            <label class="qty">
              数量
              <input
                v-model.number="qtyById[p.id]"
                type="number"
                min="1"
                :max="Math.max(1, p.stock)"
                :disabled="p.stock < 1"
              />
            </label>
            <button
              type="button"
              class="btn buy"
              :disabled="p.stock < 1 || orderingId === p.id"
              @click="onBuy(p)"
            >
              {{ orderingId === p.id ? "处理中…" : "立即购买" }}
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.page {
  max-width: 1080px;
  margin: 0 auto;
  padding: 0 1.25rem 3rem;
}

.hero {
  padding: 2.25rem 0 1.5rem;
}

.hero-inner {
  text-align: center;
}

.badge {
  display: inline-block;
  margin: 0 0 0.5rem;
  padding: 0.2rem 0.65rem;
  font-size: 0.72rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #c2410c;
  background: #ffedd5;
  border-radius: 999px;
}

.hero h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(105deg, #ea580c, #7c3aed);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.tagline {
  margin: 0.5rem 0 0;
  color: #64748b;
  font-size: 1rem;
}

.subtip {
  font-weight: 400;
  font-size: 0.85rem;
  color: #94a3b8;
}

.card {
  background: #fff;
  border-radius: 16px;
  padding: 1.35rem 1.5rem;
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.8);
}

.panel-title {
  margin: 0 0 1rem;
  font-size: 1.05rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.85rem 1rem;
  margin-bottom: 1rem;
}

.field.wide {
  grid-column: 1 / -1;
}

.field span {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  color: #475569;
  margin-bottom: 0.35rem;
}

.field input,
.field textarea {
  width: 100%;
  padding: 0.55rem 0.65rem;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font: inherit;
}

.field input:focus,
.field textarea:focus {
  outline: none;
  border-color: #a855f7;
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.18);
}

.btn {
  padding: 0.5rem 1.1rem;
  border-radius: 10px;
  border: 1px solid transparent;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.accent {
  background: linear-gradient(120deg, #ea580c, #c026d3);
  color: #fff;
}

.btn.accent:hover:not(:disabled) {
  filter: brightness(1.05);
}

.btn.ghost {
  background: #fff;
  border-color: #e2e8f0;
  color: #475569;
}

.btn.buy {
  background: #0f172a;
  color: #fff;
  flex: 1;
  min-width: 7rem;
}

.btn.buy:hover:not(:disabled) {
  background: #1e293b;
}

.banner {
  padding: 0.75rem 1rem;
  border-radius: 10px;
  margin: 0.75rem 0;
  font-size: 0.92rem;
}

.banner.error {
  background: #fef2f2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.banner.ok {
  background: #ecfdf5;
  color: #047857;
  border: 1px solid #a7f3d0;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 1.5rem 0 1rem;
}

.toolbar h2 {
  margin: 0;
  font-size: 1.2rem;
}

.grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.25rem;
}

.product {
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.07);
  border: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
}

.thumb-wrap {
  aspect-ratio: 4 / 3;
  background: #f8fafc;
}

.thumb {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.thumb.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 0.9rem;
  height: 100%;
}

.body {
  padding: 1rem 1.1rem 1.15rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.name {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.desc {
  margin: 0.35rem 0 0;
  font-size: 0.88rem;
  color: #64748b;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-top: 0.85rem;
}

.price {
  font-size: 1.25rem;
  font-weight: 800;
  color: #ea580c;
}

.stock {
  font-size: 0.82rem;
  color: #94a3b8;
}

.buy-row {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-top: 0.85rem;
}

.qty {
  font-size: 0.82rem;
  color: #475569;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.qty input {
  width: 3.5rem;
  padding: 0.35rem 0.4rem;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font: inherit;
}

.empty-block {
  text-align: center;
  padding: 2rem;
  color: #64748b;
}
</style>
