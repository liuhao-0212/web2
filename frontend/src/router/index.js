import { createRouter, createWebHistory } from "vue-router";
import Shop from "../views/Shop.vue";
import Login from "../views/Login.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", name: "shop", component: Shop },
    { path: "/login", name: "login", component: Login, meta: { public: true } },
  ],
});

export default router;
