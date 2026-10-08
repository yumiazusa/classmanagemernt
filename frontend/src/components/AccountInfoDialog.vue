<template>
  <Teleport to="body">
    <div v-if="visible" class="dialog-mask" @click.self="close" @keydown.esc.prevent="close">
      <form ref="formElement" class="dialog-card" role="dialog" aria-modal="true" aria-labelledby="account-info-edit-title" aria-describedby="account-info-edit-target" @submit.prevent="submit" @keydown.tab="trapFocus">
        <h3 id="account-info-edit-title">修改信息</h3>
        <p id="account-info-edit-target" class="subtitle">{{ target }}</p>
        <label class="field">
          <span>用户名</span>
          <input ref="usernameInput" v-model="username" type="text" autocomplete="off" placeholder="至少 3 位" :disabled="submitting" :aria-invalid="Boolean(error)" />
        </label>
        <label class="field">
          <span>姓名</span>
          <input v-model="fullName" type="text" autocomplete="off" placeholder="可留空" :disabled="submitting" />
        </label>
        <p v-if="error" class="dialog-error" role="alert">{{ error }}</p>
        <div class="dialog-actions">
          <button type="button" class="btn cancel" :disabled="submitting" @click="close">取消</button>
          <button type="submit" class="btn submit" :disabled="submitting">{{ submitting ? "正在保存..." : "保存" }}</button>
        </div>
      </form>
    </div>
  </Teleport>
</template>

<script setup>
import { nextTick, onBeforeUnmount, ref } from "vue";

const visible = ref(false);
const target = ref("");
const username = ref("");
const fullName = ref("");
const error = ref("");
const submitting = ref(false);
const usernameInput = ref(null);
const formElement = ref(null);
let onSubmit;
let previousFocus;
let previousOverflow;

function open(options) {
  if (visible.value) return;
  target.value = options.target;
  onSubmit = options.onSubmit;
  username.value = options.username || "";
  fullName.value = options.full_name || "";
  error.value = "";
  previousFocus = document.activeElement;
  previousOverflow = document.body.style.overflow;
  document.body.style.overflow = "hidden";
  visible.value = true;
  nextTick(() => usernameInput.value?.focus());
}

function close() {
  if (submitting.value) return;
  visible.value = false;
  username.value = "";
  fullName.value = "";
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
  const cleanedUsername = username.value.trim();
  if (cleanedUsername.length < 3) {
    error.value = "用户名长度不能少于 3 位";
    usernameInput.value?.focus();
    return;
  }
  submitting.value = true;
  try {
    await onSubmit({ username: cleanedUsername, full_name: fullName.value.trim() || null });
    submitting.value = false;
    close();
  } catch (err) {
    error.value = err.message || "修改信息失败，请重试";
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
