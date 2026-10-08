<template>
  <section class="admin-page">
    <article class="panel head-panel">
      <h2>用户管理</h2>
      <p>查看全部用户并执行启用、停用、角色设置、密码重置与删除。</p>
    </article>

    <article class="panel filter-panel">
      <div class="filters-grid">
        <label class="field">
          <span>关键词</span>
          <input v-model.trim="filters.keyword" type="text" placeholder="用户名 / 姓名 / 学号" />
        </label>
        <label class="field">
          <span>班级</span>
          <select v-model="filters.class_name">
            <option value="">全部班级</option>
            <option v-for="item in classOptions" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>
        <label class="field">
          <span>角色</span>
          <select v-model="filters.role">
            <option value="all">全部</option>
            <option value="student">学生</option>
            <option value="teacher">教师</option>
            <option value="admin">管理员</option>
          </select>
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
      <div class="batch-actions">
        <button type="button" class="btn plain" :disabled="isLoading || users.length === 0" @click="toggleSelectCurrentPage">
          {{ isAllCurrentPageSelected ? "取消全选当前页" : "全选当前页" }}
        </button>
        <button
          type="button"
          class="btn success"
          :disabled="isLoading || selectedUserIds.length === 0"
          @click="handleBatchToggleEnabled(true)"
        >
          批量启用（{{ selectedUserIds.length }}）
        </button>
        <button
          type="button"
          class="btn danger"
          :disabled="isLoading || selectedUserIds.length === 0"
          @click="handleBatchToggleEnabled(false)"
        >
          批量停用（{{ selectedUserIds.length }}）
        </button>
        <button
          type="button"
          class="btn plain"
          :disabled="isLoading || selectedUserIds.length === 0"
          @click="handleBatchResetPassword"
        >
          批量重置密码（{{ selectedUserIds.length }}）
        </button>
        <button
          type="button"
          class="btn danger"
          :disabled="isLoading || selectedUserIds.length === 0"
          @click="handleBatchDelete"
        >
          批量删除（{{ selectedUserIds.length }}）
        </button>
      </div>

      <p v-if="isLoading" class="hint">正在加载用户列表...</p>
      <p v-else-if="users.length === 0" class="hint">当前筛选条件下无用户数据</p>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>选择</th>
              <th>用户名</th>
              <th>姓名</th>
              <th>角色</th>
              <th>学号</th>
              <th>班级</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in users" :key="item.user_id">
              <td>
                <input
                  type="checkbox"
                  :checked="selectedUserIds.includes(item.user_id)"
                  :disabled="isLoading || isSelfRow(item)"
                  @change="toggleRowSelected(item.user_id, $event.target.checked)"
                />
              </td>
              <td>{{ item.username }}</td>
              <td>{{ item.full_name || "-" }}</td>
              <td>{{ roleText(item.role) }}</td>
              <td>{{ item.student_no || "-" }}</td>
              <td>{{ item.class_name || "-" }}</td>
              <td>
                <span :class="['status-pill', item.is_enabled ? 'enabled' : 'disabled']">
                  {{ item.is_enabled ? "启用" : "停用" }}
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
                    :disabled="isLoading || isSelfRow(item)"
                    @click="handleToggleEnabled(item, false)"
                  >
                    停用
                  </button>
                  <button type="button" class="btn mini plain" :disabled="isLoading" @click="handleResetPassword(item)">
                    重置密码
                  </button>
                  <button
                    type="button"
                    class="btn mini plain"
                    :disabled="isLoading"
                    @click="handleChangeRole(item)"
                  >
                    改角色
                  </button>
                  <button
                    type="button"
                    class="btn mini danger"
                    :disabled="isLoading || isSelfRow(item)"
                    @click="handleDeleteUser(item)"
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

    <div v-if="roleDialog.visible" class="dialog-mask" @click.self="closeRoleDialog">
      <div class="dialog-card">
        <h3>修改角色</h3>
        <p class="dialog-desc">账号：{{ roleDialog.username }}</p>
        <p class="dialog-desc">当前角色：{{ roleText(roleDialog.currentRole) }}</p>
        <label class="field">
          <span>目标角色</span>
          <select v-model="roleDialog.targetRole" :disabled="isLoading">
            <option value="student">学生</option>
            <option value="teacher">教师</option>
            <option value="admin">管理员</option>
          </select>
        </label>
        <div class="dialog-actions">
          <button type="button" class="btn plain" :disabled="isLoading" @click="closeRoleDialog">取消</button>
          <button
            type="button"
            class="btn primary"
            :disabled="isLoading || roleDialog.targetRole === roleDialog.currentRole"
            @click="confirmRoleChange"
          >
            确认修改
          </button>
        </div>
      </div>
    </div>
    <PasswordResetDialog ref="passwordResetDialog" />
  </section>
</template>

<script setup>
import PasswordResetDialog from "../components/PasswordResetDialog.vue";

import { computed, onMounted, reactive, ref } from "vue";

const passwordResetDialog = ref(null);

import { getStoredCurrentUser } from "../api/auth";
import {
  batchDisableAdminUsers,
  batchDeleteAdminUsers,
  batchEnableAdminUsers,
  batchResetAdminUserPasswords,
  deleteAdminUser,
  disableAdminUser,
  enableAdminUser,
  getAdminUserClassOptions,
  getAdminUsers,
  resetAdminUserPassword,
  setAdminUserRole,
} from "../api/admin";

const users = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");
const actionMessage = ref("");
const actionError = ref(false);
const currentUserId = ref(getStoredCurrentUser()?.id || 0);
const classOptions = ref([]);
const selectedUserIds = ref([]);
const roleDialog = reactive({
  visible: false,
  userId: 0,
  username: "",
  currentRole: "student",
  targetRole: "student",
});

const filters = reactive({
  keyword: "",
  class_name: "",
  role: "all",
  is_enabled: "all",
});

const pagination = ref({
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
});

const totalPagesText = computed(() => (pagination.value.total_pages > 0 ? pagination.value.total_pages : 1));
const selectableUserIds = computed(() => users.value.filter((item) => !isSelfRow(item)).map((item) => item.user_id));
const isAllCurrentPageSelected = computed(() => {
  if (selectableUserIds.value.length === 0) {
    return false;
  }
  return selectableUserIds.value.every((id) => selectedUserIds.value.includes(id));
});

function isSelfRow(item) {
  return item?.user_id === currentUserId.value;
}

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

function roleText(role) {
  if (role === "admin") return "管理员";
  if (role === "teacher") return "教师";
  return "学生";
}

function buildQueryParams() {
  const params = {
    page: pagination.value.page,
    page_size: pagination.value.page_size,
    keyword: filters.keyword,
    class_name: filters.class_name,
    role: filters.role,
  };
  if (filters.is_enabled === "enabled") {
    params.is_enabled = true;
  } else if (filters.is_enabled === "disabled") {
    params.is_enabled = false;
  }
  return params;
}

async function loadUsers() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const data = await getAdminUsers(buildQueryParams());
    users.value = data.items || [];
    selectedUserIds.value = [];
    pagination.value.total = data.total || 0;
    pagination.value.total_pages = data.total_pages || 0;
    pagination.value.page = data.page || pagination.value.page;
    pagination.value.page_size = data.page_size || pagination.value.page_size;
  } catch (error) {
    errorMessage.value = `用户列表加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

async function loadClassOptions() {
  try {
    classOptions.value = await getAdminUserClassOptions();
  } catch (error) {
    classOptions.value = [];
  }
}

function handleSearch() {
  pagination.value.page = 1;
  loadUsers();
}

function handleReset() {
  filters.keyword = "";
  filters.class_name = "";
  filters.role = "all";
  filters.is_enabled = "all";
  pagination.value.page = 1;
  loadUsers();
}

function handlePageSizeChange() {
  pagination.value.page = 1;
  loadUsers();
}

function goPrevPage() {
  if (pagination.value.page <= 1) {
    return;
  }
  pagination.value.page -= 1;
  loadUsers();
}

function goNextPage() {
  if (pagination.value.total_pages === 0 || pagination.value.page >= pagination.value.total_pages) {
    return;
  }
  pagination.value.page += 1;
  loadUsers();
}

function toggleRowSelected(userId, checked) {
  if (checked) {
    if (!selectedUserIds.value.includes(userId)) {
      selectedUserIds.value = [...selectedUserIds.value, userId];
    }
    return;
  }
  selectedUserIds.value = selectedUserIds.value.filter((id) => id !== userId);
}

function toggleSelectCurrentPage() {
  if (isAllCurrentPageSelected.value) {
    selectedUserIds.value = selectedUserIds.value.filter((id) => !selectableUserIds.value.includes(id));
    return;
  }
  const merged = new Set([...selectedUserIds.value, ...selectableUserIds.value]);
  selectedUserIds.value = Array.from(merged);
}

async function handleBatchToggleEnabled(targetEnabled) {
  actionMessage.value = "";
  actionError.value = false;
  if (selectedUserIds.value.length === 0) {
    actionMessage.value = "请先勾选要操作的用户";
    actionError.value = true;
    return;
  }
  const actionText = targetEnabled ? "启用" : "停用";
  const confirmed = window.confirm(`确认批量${actionText} ${selectedUserIds.value.length} 个账号吗？`);
  if (!confirmed) {
    return;
  }
  isLoading.value = true;
  try {
    const result = targetEnabled
      ? await batchEnableAdminUsers({ user_ids: selectedUserIds.value })
      : await batchDisableAdminUsers({ user_ids: selectedUserIds.value });
    actionMessage.value = `批量${actionText}完成：成功 ${result.success_count}，失败 ${result.failed_count}`;
    actionError.value = Boolean(result.failed_count);
    await loadUsers();
  } catch (error) {
    actionMessage.value = `批量${actionText}失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

async function handleToggleEnabled(item, targetEnabled) {
  actionMessage.value = "";
  actionError.value = false;

  if (!targetEnabled && isSelfRow(item)) {
    actionMessage.value = "不能停用当前登录管理员账号";
    actionError.value = true;
    return;
  }

  const actionText = targetEnabled ? "启用" : "停用";
  const confirmed = window.confirm(`确认${actionText}用户 ${item.username} 吗？`);
  if (!confirmed) {
    return;
  }

  isLoading.value = true;
  try {
    if (targetEnabled) {
      await enableAdminUser(item.user_id);
    } else {
      await disableAdminUser(item.user_id);
    }
    actionMessage.value = `${actionText}成功：${item.username}`;
    await loadUsers();
  } catch (error) {
    actionMessage.value = `${actionText}失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

async function handleDeleteUser(item) {
  actionMessage.value = "";
  actionError.value = false;
  if (isSelfRow(item)) {
    actionMessage.value = "不能删除当前登录管理员账号";
    actionError.value = true;
    return;
  }
  const confirmed = window.confirm(`确认删除用户 ${item.username} 吗？删除后无法恢复。`);
  if (!confirmed) {
    return;
  }
  isLoading.value = true;
  try {
    await deleteAdminUser(item.user_id);
    actionMessage.value = `已删除用户：${item.username}`;
    await loadUsers();
    await loadClassOptions();
  } catch (error) {
    actionMessage.value = `删除失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

async function handleBatchDelete() {
  actionMessage.value = "";
  actionError.value = false;
  if (selectedUserIds.value.length === 0) {
    actionMessage.value = "请先勾选要删除的用户";
    actionError.value = true;
    return;
  }
  const confirmed = window.confirm(`确认批量删除 ${selectedUserIds.value.length} 个账号吗？删除后无法恢复。`);
  if (!confirmed) {
    return;
  }
  isLoading.value = true;
  try {
    const result = await batchDeleteAdminUsers({ user_ids: selectedUserIds.value });
    actionMessage.value = `批量删除完成：成功 ${result.success_count}，失败 ${result.failed_count}`;
    actionError.value = Boolean(result.failed_count);
    await loadUsers();
    await loadClassOptions();
  } catch (error) {
    actionMessage.value = `批量删除失败：${error.message}`;
    actionError.value = true;
  } finally {
    isLoading.value = false;
  }
}

function handleBatchResetPassword() {
  if (selectedUserIds.value.length === 0) {
    actionMessage.value = "请先勾选要重置密码的用户";
    actionError.value = true;
    return;
  }
  const userIds = [...selectedUserIds.value];
  passwordResetDialog.value.open({
    target: `已选 ${selectedUserIds.value.length} 个账号将使用同一个新密码`,
    onSubmit: (newPassword) => submitHandleBatchResetPassword(userIds, newPassword),
  });
}

async function submitHandleBatchResetPassword(userIds, newPassword) {
  actionMessage.value = "";
  actionError.value = false;
  isLoading.value = true;
  try {
    const result = await batchResetAdminUserPasswords({
      user_ids: userIds,
      new_password: newPassword,
    });
    actionMessage.value = `批量重置密码完成：成功 ${result.success_count}，失败 ${result.failed_count}`;
    actionError.value = Boolean(result.failed_count);
    await loadUsers();
  } catch (error) {
    actionMessage.value = `批量重置密码失败：${error.message}`;
    actionError.value = true;
    throw error;
  } finally {
    isLoading.value = false;
  }
}

async function handleChangeRole(item) {
  actionMessage.value = "";
  actionError.value = false;
  if (!item?.user_id) {
    return;
  }
  roleDialog.visible = true;
  roleDialog.userId = item.user_id;
  roleDialog.username = item.username || "-";
  roleDialog.currentRole = item.role || "student";
  roleDialog.targetRole = item.role || "student";
}

function closeRoleDialog() {
  if (isLoading.value) {
    return;
  }
  roleDialog.visible = false;
}

async function confirmRoleChange() {
  actionMessage.value = "";
  actionError.value = false;
  const targetRole = roleDialog.targetRole;
  const currentRole = roleDialog.currentRole;
  if (targetRole === currentRole) {
    return;
  }
  const targetItem = users.value.find((item) => item.user_id === roleDialog.userId);
  if (targetItem && isSelfRow(targetItem) && targetRole !== "admin") {
    actionMessage.value = "不能修改当前登录管理员为非管理员角色";
    actionError.value = true;
    return;
  }
  const roleName = roleText(targetRole);
  const confirmed = window.confirm(`确认将 ${roleDialog.username} 的角色改为“${roleName}”吗？`);
  if (!confirmed) {
    return;
  }
  isLoading.value = true;
  try {
    await setAdminUserRole(roleDialog.userId, { role: targetRole });
    actionMessage.value = `角色更新成功：${roleDialog.username} -> ${roleName}`;
    roleDialog.visible = false;
    await loadUsers();
    await loadClassOptions();
  } catch (error) {
    actionMessage.value = `角色更新失败：${error.message}`;
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
    await resetAdminUserPassword(item.user_id, { new_password: newPassword });
    actionMessage.value = `已重置 ${item.username} 的密码`;
    await loadUsers();
  } catch (error) {
    actionMessage.value = `重置密码失败：${error.message}`;
    actionError.value = true;
    throw error;
  } finally {
    isLoading.value = false;
  }
}

onMounted(async () => {
  await Promise.all([loadUsers(), loadClassOptions()]);
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

.filters-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
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

.batch-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
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

.dialog-mask {
  position: fixed;
  inset: 0;
  background: var(--overlay-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-dialog);
  padding: 16px;
}

.dialog-card {
  width: 100%;
  max-width: 420px;
  background: var(--surface-1);
  border-radius: 12px;
  border: 1px solid var(--border-soft);
  padding: 16px;
  display: grid;
  gap: 10px;
  max-height: min(86vh, 620px);
  overflow: auto;
}

.dialog-card h3 {
  margin: 0;
}

.dialog-desc {
  margin: 0;
  color: var(--text-muted);
  font-size: 14px;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 920px) {
  .filters-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .dialog-actions {
    display: grid;
    grid-template-columns: 1fr;
  }

  .dialog-actions .btn {
    width: 100%;
  }
}
</style>
