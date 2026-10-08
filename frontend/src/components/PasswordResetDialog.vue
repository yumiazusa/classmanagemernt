<template>
  <Teleport to="body">
    <div v-if="visible" class="dialog-mask" @click.self="close" @keydown.esc.prevent="close">
      <form ref="formElement" class="dialog-card" role="dialog" aria-modal="true" aria-labelledby="password-reset-title" aria-describedby="password-reset-target" @submit.prevent="submit" @keydown.tab="trapFocus">
        <h3 id="password-reset-title">重置密码</h3>
        <p id="password-reset-target" class="subtitle">{{ target }}</p>
        <label class="field">
          <span>新密码</span>
          <input ref="passwordInput" v-model="password" type="password" autocomplete="new-password" placeholder="至少 6 位" :disabled="submitting" :aria-invalid="Boolean(error)" />
        </label>
        <label class="field">
          <span>确认新密码</span>
          <input v-model="confirmation" type="password" autocomplete="new-password" placeholder="再次输入新密码" :disabled="submitting" :aria-invalid="Boolean(error)" />
        </label>
        <p class="hint">重置后，账号下次登录时需要修改密码。</p>
        <p v-if="error" class="dialog-error" role="alert">{{ error }}</p>
        <div class="dialog-actions">
          <button type="button" class="btn cancel" :disabled="submitting" @click="close">取消</button>
          <button type="submit" class="btn submit" :disabled="submitting">{{ submitting ? "正在重置..." : "确认重置" }}</button>
        </div>
      </form>
    </div>
  </Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";

const visible = ref(false);
const target = ref("");
const password = ref("");
const confirmation = ref("");
const error = ref("");
const submitting = ref(false);
const passwordInput = ref(null);
const formElement = ref(null);
let onSubmit;
let previousFocus;
let previousOverflow;

function open(options) {
  if (visible.value) return;
  target.value = options.target;
  onSubmit = options.onSubmit;
  password.value = "";
  confirmation.value = "";
  error.value = "";
  previousFocus = document.activeElement;
  previousOverflow = document.body.style.overflow;
  document.body.style.overflow = "hidden";
  visible.value = true;
  nextTick(() => passwordInput.value?.focus());
}

function close() {
  if (submitting.value) return;
  visible.value = false;
  password.value = "";
  confirmation.value = "";
  onSubmit = null;
  document.body.style.overflow = previousOverflow ?? "";
  previousFocus?.focus();
}

function trapFocus(event) {
  const elements = [...formElement.value.querySelectorAll("input:not(:disabled), button:not(:disabled)")];
  const first = elements[0];
  const last = elements[elements.length - 1];
  if (!first || (event.shiftKey && document.activeElement === first) || (!event.shiftKey && document.activeElement === last)) {
    event.preventDefault();
    (event.shiftKey ? last : first)?.focus();
  }
}

async function submit() {
  if (submitting.value) return;
  error.value = "";
  const newPassword = password.value.trim();
  if (newPassword.length < 6) {
    error.value = "新密码长度不能少于 6 位";
    passwordInput.value?.focus();
    return;
  }
  if (newPassword !== confirmation.value.trim()) {
    error.value = "两次输入的密码不一致";
    return;
  }
  submitting.value = true;
  try {
    await onSubmit(newPassword);
    submitting.value = false;
    close();
  } catch (err) {
    error.value = err.message || "重置密码失败，请重试";
  } finally {
    submitting.value = false;
  }
}

onBeforeUnmount(() => {
  if (visible.value) document.body.style.overflow = previousOverflow ?? "";
});
defineExpose({ open });
</script>

<style scoped>
.dialog-mask { position: fixed; inset: 0; background: var(--overlay-soft); display: flex; align-items: center; justify-content: center; z-index: var(--z-dialog); padding: 16px; }
.dialog-card { width: min(420px, 92vw); box-sizing: border-box; background: var(--surface-1); border: 1px solid var(--border-soft); border-radius: 12px; padding: 16px; display: grid; gap: 10px; max-height: 86vh; overflow: auto; box-shadow: var(--shadow-soft); }
h3, p { margin: 0; }
.subtitle { color: var(--text-body); overflow-wrap: anywhere; }
.field { display: grid; gap: 6px; }
.field span, .hint { color: var(--text-subtle); font-size: 14px; }
.field input { width: 100%; box-sizing: border-box; border: 1px solid var(--border-strong); border-radius: 8px; padding: 8px 10px; }
.dialog-error { color: var(--danger-strong); font-size: 14px; }
.dialog-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 6px; }
.btn { border: 0; border-radius: 8px; padding: 9px 12px; font-weight: 600; cursor: pointer; }
.cancel { background: var(--neutral-btn); color: var(--text-strong); }
.submit { background: var(--brand-600); color: var(--surface-1); }
.btn:disabled { opacity: .65; cursor: wait; }
@media (max-width: 720px) { .dialog-actions { display: grid; grid-template-columns: 1fr; } .btn { width: 100%; } }
</style>
