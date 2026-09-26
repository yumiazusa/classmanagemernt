<template>
  <section class="login-page">
    <article class="login-card">
      <h2>账号登录</h2>
      <p class="subtitle">请使用学生、教师或管理员账号登录教学平台。</p>

      <form class="login-form" @submit.prevent="handleLogin">
        <label class="field">
          <span>用户名</span>
          <input v-model.trim="form.username" type="text" autocomplete="username" placeholder="请输入用户名" />
        </label>
        <label class="field">
          <span>密码</span>
          <input v-model="form.password" type="password" autocomplete="current-password" placeholder="请输入密码" />
        </label>
        <button class="btn-login" type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? "登录中..." : "登录" }}
        </button>
      </form>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    </article>
  </section>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getCurrentUser, login } from "../api/auth";

const route = useRoute();
const router = useRouter();

const form = reactive({
  username: "",
  password: "",
});

const isSubmitting = ref(false);
const errorMessage = ref("");

function resolveRedirectTarget(userRole) {
  if (userRole?.must_change_password) {
    return "/change-password";
  }
  const redirect = typeof route.query.redirect === "string" ? route.query.redirect : "";
  if (redirect && redirect.startsWith("/") && !redirect.startsWith("/login")) {
    return redirect;
  }
  if (userRole?.role === "admin") {
    return "/admin";
  }
  return userRole?.role === "teacher" ? "/teacher/courses" : "/courses";
}

async function handleLogin() {
  const username = form.username.trim();
  const password = form.password;
  if (!username || !password) {
    errorMessage.value = "请输入用户名和密码";
    return;
  }

  isSubmitting.value = true;
  errorMessage.value = "";
  try {
    await login({ username, password });
    const user = await getCurrentUser({ forceRefresh: true });
    await router.replace(resolveRedirectTarget(user));
  } catch (error) {
    errorMessage.value = error.message || "登录失败，请稍后重试";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.login-page {
  min-height: calc(100dvh - 90px);
  display: grid;
  place-items: center;
  padding: clamp(14px, 3vw, 32px);
}

.login-card {
  width: min(460px, 100%);
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: clamp(18px, 2.4vw, 28px);
  box-shadow: var(--shadow-soft);
}

.login-card h2 {
  margin: 0;
  color: var(--text-strong);
  font-size: clamp(24px, 2.6vw, 28px);
}

.subtitle {
  margin: 10px 0 18px;
  color: var(--text-subtle);
  font-size: 14px;
  line-height: 1.5;
}

.login-form {
  display: grid;
  gap: 12px;
}

.field {
  display: grid;
  gap: 6px;
}

.field span {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.02em;
  color: var(--text-body);
}

.field input {
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm);
  padding: 12px 12px;
  min-height: 46px;
  font-size: 16px;
  background: var(--surface-2);
}

.btn-login {
  border: 0;
  border-radius: var(--radius-sm);
  background: var(--brand-600);
  color: var(--surface-1);
  padding: 12px 14px;
  min-height: 46px;
  font-weight: 600;
  cursor: pointer;
}

.btn-login:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-text {
  margin: 12px 0 0;
  border-radius: var(--radius-sm);
  background: var(--danger-soft);
  border: 1px solid var(--danger-border);
  color: var(--danger-strong);
  padding: 10px 12px;
  font-size: 14px;
}

@media (max-width: 860px) {
  .login-page {
    place-items: start center;
    padding-top: clamp(16px, 6vw, 34px);
  }
}

@media (max-width: 520px) {
  .login-card {
    border-radius: var(--radius-md);
    padding: 16px;
  }

  .subtitle {
    margin-top: 8px;
    margin-bottom: 14px;
    font-size: 14px;
  }
}
</style>
