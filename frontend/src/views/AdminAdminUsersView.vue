<template>
  <section class="admin-page">
    <article class="panel head-panel">
      <h2>管理员管理</h2>
      <p>仅管理员可管理管理员账号，支持创建、启用/停用、修改信息、重置密码与删除。</p>
    </article>

    <article class="panel create-panel">
      <h3>新建管理员</h3>
      <div class="create-grid">
        <label class="field">
          <span>用户名</span>
          <input v-model.trim="createForm.username" type="text" placeholder="例如：admin_zhang" />
        </label>
        <label class="field">
          <span>姓名</span>
          <input v-model.trim="createForm.full_name" type="text" placeholder="例如：张管理员" />
        </label>
        <label class="field">
          <span>初始密码</span>
          <input v-model="createForm.password" type="password" placeholder="至少6位" />
        </label>
      </div>
      <div class="actions-row">
        <button type="button" class="btn primary" :disabled="isLoading" @click="handleCreateAdmin">创建管理员</button>
      </div>
      <p class="hint">创建成功后默认启用，并要求该管理员首次登录修改密码。</p>
    </article>

    <article class="panel filter-panel">
      <div class="filters-grid">
        <label class="field">
          <span>关键词</span>
          <input v-model.trim="filters.keyword" type="text" placeholder="用户名 / 姓名" />
        </label>
        <label class="field">
          <span>账号状态</span>
          <select v-model="filters.is_enabled">
            <option value="all">全部</option>
            <option value="enabled">启用</option>
            <option value="disabled">停用</option>
          </select>
        </label>
      </div>
      <div class="actions-row">
        <button type="button" class="btn primary" :disabled="isLoading" @click="handleSearch">查询</button>
        <button type="button" class="btn plain" :disabled="isLoading" @click="handleReset">重置</button>
      </div>
    </article>

    <article v-if="actionMessage" :class="['panel', actionError ? 'error' : 'success']">{{ actionMessage }}</article>
    <article v-if="errorMessage" class="panel error">{{ errorMessage }}</article>

    <article class="panel table-panel">
      <div class="table-meta">共 {{ pagination.total }} 条，当前第 {{ pagination.page }} / {{ totalPagesText }} 页</div>

      <p v-if="isLoading" class="hint">正在加载管理员列表...</p>
      <p v-else-if="admins.length === 0" class="hint">当前筛选条件下无管理员数据</p>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>用户名</th>
              <th>姓名</th>
              <th>账号状态</th>
              <th>强制改密</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in admins" :key="item.user_id">
              <td>{{ item.username }}</td>
              <td>{{ item.full_name || "-" }}</td>
              <td>
                <span :class="['status-pill', item.is_enabled ? 'enabled' : 'disabled']">
                  {{ item.is_enabled ? "启用" : "停用" }}
                </span>
              </td>
              <td>
                <span :class="['status-pill', item.must_change_password ? 'warn' : 'enabled']">
                  {{ item.must_change_password ? "是" : "否" }}
                </span>
              </td>
              <td>{{ formatTime(item.created_at) }}</td>
              <td>
                <div class="row-actions">
                  <button
                    v-if="!item.is_enabled"
                    type="button"
                    class="btn mini success"
                    :disabled="isLoading"
                    @click="handleToggleEnabled(item, true)"
                  >
                    启用
                  </button>
                  <button
                    v-else
                    type="button"
                    class="btn mini danger"
                    :disabled="isLoading"
                    @click="handleToggleEnabled(item, false)"
                  >
                    停用
                  </button>
                  <button
                    type="button"
                    class="btn mini plain"
                    :disabled="isLoading"
                    @click="handleResetPassword(item)"
                  >
                    重置密码
                  </button>
                  <button
                    type="button"
                    class="btn mini plain"
                    :disabled="isLoading"
                    @click="handleUpdateInfo(item)"
                  >
                    修改信息
                  </button>
                  <button
                    type="button"
                    class="btn mini danger"
                    :disabled="isLoading || isSelf(item)"
                    @click="handleDeleteAdmin(item)"
                  >
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <div class="page-size">
          <span>每页</span>
          <select v-model.number="pagination.page_size" :disabled="isLoading" @change="handlePageSizeChange">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
          </select>
        </div>
        <div class="page-actions">
          <button type="button" class="btn plain" :disabled="isLoading || pagination.page <= 1" @click="goPrevPage">上一页</button>
          <span>第 {{ pagination.page }} / {{ totalPagesText }} 页</span>
          <button
            type="button"
            class="btn plain"
            :disabled="isLoading || pagination.page >= pagination.total_pages || pagination.total_pages === 0"
            @click="goNextPage"
          >
            下一页
          </button>
        </div>
      </div>
    </article>
    <PasswordResetDialog ref="passwordResetDialog" />
    <AccountInfoDialog ref="accountInfoDialog" />
  </section>
</template>

<script setup>
import AccountInfoDialog from "../components/AccountInfoDialog.vue";
import PasswordResetDialog from "../components/PasswordResetDialog.vue";

import { computed, onMounted, reactive, ref } from "vue";

const passwordResetDialog = ref(null);
const accountInfoDialog = ref(null);

import { getStoredCurrentUser } from "../api/auth";
import {
  createAdminAdminUser,
  deleteAdminUser,
  disableAdminAdminUser,
  enableAdminAdminUser,
  getAdminAdminUsers,
  resetAdminAdminUserPassword,
  updateAdminUserInfo,
} from "../api/admin";

const admins = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");
const actionMessage = ref("");
const actionError = ref(false);
const currentUserId = ref(getStoredCurrentUser()?.id || 0);

const createForm = reactive({
  username: "",
  full_name: "",
  password: "123456",
});

const filters = reactive({
  keyword: "",
  is_enabled: "all",
});

const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
});

const totalPagesText = computed(() => (pagination.value.total_pages > 0 ? pagination.value.total_pages : 1));

function formatTime(value) {
  if (!value) {
    return "-";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", { hour12: false });
}

function isSelf(item) {
  return item?.user_id === currentUserId.value;
}

function buildQueryParams() {
  const params = {
    page: pagination.value.page,
    page_size: pagination.value.page_size,
    keyword: filters.keyword,
  };
  if (filters.is_enabled === "enabled") {
    params.is_enabled = true;
  } else if (filters.is_enabled === "disabled") {
    params.is_enabled = false;
  }
  return params;
}

async function loadAdmins() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const data = await getAdminAdminUsers(buildQueryParams());
    admins.value = data.items || [];
    pagination.value.total = data.total || 0;
    pagination.value.total_pages = data.total_pages || 0;
    pagination.value.page = data.page || pagination.value.page;
    pagination.value.page_size = data.page_size || pagination.value.page_size;
  } catch (error) {
    errorMessage.value = `管理员列表加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

async function handleCreateAdmin() {
  actionMessage.value = "";
  actionError.value = false;

  const username = createForm.username.trim();
  const fullName = createForm.full_name.trim();
  const password = createForm.password;

  if (!username) {
    actionMessage.value = "请输入管理员用户名";
    actionError.value = true;
    return;
  }
  if (!password || password.length < 6) {
    actionMessage.value = "初始密码长度不能少于 6 位";
    actionError.value = true;
    return;
  }

  const confirmed = window.confirm(`确认创建管理员账号 ${username} 吗？`);
  if (!confirmed) {
    return;
  }

  isLoading.value = true;
  try {
    await createAdminAdminUser({
      username,
      full_name: fullName || null,
      password,
    });
    actionMessage.value = `管理员账号已创建：${username}`;
    createForm.username = "";
    createForm.full_name = "";
    createForm.password = "123456";
    pagination.value.page = 1;
    await loadAdmins();
  } catch (error) {
    actionMessage.value = `创建管理员失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

function handleSearch() {
  pagination.value.page = 1;
  loadAdmins();
}

function handleReset() {
  filters.keyword = "";
  filters.is_enabled = "all";
  pagination.value.page = 1;
  loadAdmins();
}

function handlePageSizeChange() {
  pagination.value.page = 1;
  loadAdmins();
}

function goPrevPage() {
  if (pagination.value.page <= 1) {
    return;
  }
  pagination.value.page -= 1;
  loadAdmins();
}

function goNextPage() {
  if (pagination.value.total_pages === 0 || pagination.value.page >= pagination.value.total_pages) {
    return;
  }
  pagination.value.page += 1;
  loadAdmins();
}

async function handleToggleEnabled(item, targetEnabled) {
  actionMessage.value = "";
  actionError.value = false;

  if (!targetEnabled && isSelf(item)) {
    actionMessage.value = "不能停用当前登录的管理员账号";
    actionError.value = true;
    return;
  }

  const actionText = targetEnabled ? "启用" : "停用";
  const confirmed = window.confirm(`确认${actionText}管理员账号 ${item.username} 吗？`);
  if (!confirmed) {
    return;
  }

  isLoading.value = true;
  try {
    if (targetEnabled) {
      await enableAdminAdminUser(item.user_id);
    } else {
      await disableAdminAdminUser(item.user_id);
    }
    actionMessage.value = `${actionText}成功：${item.username}`;
    await loadAdmins();
  } catch (error) {
    const rawMessage = error.message || "";
    if (rawMessage.includes("不能停用当前登录的管理员账号")) {
      actionMessage.value = "不能停用当前登录的管理员账号";
    } else if (rawMessage.includes("系统必须至少保留一个启用中的管理员账号")) {
      actionMessage.value = "系统必须至少保留一个启用中的管理员账号";
    } else {
      actionMessage.value = `${actionText}失败：${rawMessage}`;
    }
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

function handleResetPassword(item) {
  passwordResetDialog.value.open({
    target: `账号：${item.username}`,
    onSubmit: (newPassword) => submitHandleResetPassword(item, newPassword),
  });
}

async function submitHandleResetPassword(item, newPassword) {
  actionMessage.value = "";
  actionError.value = false;
  isLoading.value = true;
  try {
    await resetAdminAdminUserPassword(item.user_id, { new_password: newPassword });
    actionMessage.value = `已重置 ${item.username} 的密码，账号将被要求首次登录改密`;
    await loadAdmins();
  } catch (error) {
    actionMessage.value = `重置密码失败：${error.message}`;
    actionError.value = true;
    throw error;
  } finally {
    isLoading.value = false;
  }
}

async function handleDeleteAdmin(item) {
  actionMessage.value = "";
  actionError.value = false;
  if (isSelf(item)) {
    actionMessage.value = "不能删除当前登录管理员账号";
    actionError.value = true;
    return;
  }
  const confirmed = window.confirm(`确认删除管理员账号 ${item.username} 吗？删除后无法恢复。`);
  if (!confirmed) {
    return;
  }
  isLoading.value = true;
  try {
    await deleteAdminUser(item.user_id);
    actionMessage.value = `已删除管理员账号：${item.username}`;
    if (admins.value.length === 1 && pagination.value.page > 1) {
      pagination.value.page -= 1;
    }
    await loadAdmins();
  } catch (error) {
    const rawMessage = error.message || "";
    if (rawMessage.includes("系统必须至少保留一个启用中的管理员账号")) {
      actionMessage.value = "系统必须至少保留一个启用中的管理员账号";
    } else if (rawMessage.includes("系统至少保留一个管理员账号")) {
      actionMessage.value = "系统至少保留一个管理员账号";
    } else {
      actionMessage.value = `删除失败：${rawMessage}`;
    }
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

function handleUpdateInfo(item) {
  accountInfoDialog.value.open({
    target: `账号：${item.username}`,
    username: item.username,
    full_name: item.full_name,
    onSubmit: (payload) => submitUpdateInfo(item, payload),
  });
}

async function submitUpdateInfo(item, payload) {
  actionMessage.value = "";
  actionError.value = false;
  isLoading.value = true;
  try {
    await updateAdminUserInfo(item.user_id, payload);
    actionMessage.value = "管理员信息更新成功";
    await loadAdmins();
  } catch (error) {
    actionMessage.value = `信息更新失败：${error.message}`;
    actionError.value = true;
    throw error;
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => {
  loadAdmins();
});
</script>

<style scoped>
.admin-page {
  display: grid;
  gap: 14px;
}

.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 16px;
}

.head-panel h2 {
  margin: 0;
}

.head-panel p {
  margin: 8px 0 0;
  color: var(--text-muted);
}

.create-panel h3 {
  margin: 0;
}

.create-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.field {
  display: grid;
  gap: 6px;
}

.field span {
  font-size: 14px;
  color: var(--text-muted);
}

.field input,
.field select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
}

.actions-row {
  margin-top: 10px;
  display: flex;
  gap: 10px;
}

.table-meta {
  color: var(--text-muted);
  font-size: 14px;
}

.table-wrap {
  margin-top: 10px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid var(--border-soft);
  padding: 10px 8px;
  text-align: left;
  font-size: 14px;
}

.status-pill {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
}

.status-pill.enabled {
  background: var(--success-soft);
  color: var(--success-strong);
}

.status-pill.disabled {
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.status-pill.warn {
  background: var(--warn-soft);
  color: var(--warn-strong);
}

.row-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  border: 0;
  border-radius: 8px;
  padding: 8px 12px;
  font-weight: 600;
  cursor: pointer;
}

.btn.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}

.btn.plain {
  background: var(--neutral-btn);
  color: var(--text-strong);
}

.btn.success {
  background: var(--success-strong);
  color: var(--surface-1);
}

.btn.danger {
  background: var(--danger-strong);
  color: var(--surface-1);
}

.btn.mini {
  padding: 6px 10px;
  font-size: 13px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.hint {
  margin: 10px 0 0;
  color: var(--text-subtle);
}

.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.page-size {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-size select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 6px 8px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.success {
  border-color: var(--success-border);
  background: var(--success-soft);
  color: var(--success-strong);
}

@media (max-width: 920px) {
  .create-grid,
  .filters-grid {
    grid-template-columns: 1fr;
  }
}
</style>
