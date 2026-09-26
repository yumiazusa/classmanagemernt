<template>
  <section class="student-manage">
    <article v-if="actionMessage" :class="['panel', actionError ? 'error' : 'success']">{{ actionMessage }}</article>

    <article class="panel filter-panel">
      <h3>筛选与查询</h3>
      <div class="filter-grid">
        <label class="filter-item">
          <span>关键字</span>
          <input v-model="filters.keyword" type="text" placeholder="用户名 / 姓名 / 学号" :disabled="isLoading" @keyup.enter="handleSearch" />
        </label>
        <label v-if="showClassFilter" class="filter-item">
          <span>班级</span>
          <select v-model="filters.class_name" :disabled="isLoading || isClassOptionsLoading">
            <option value="">全部班级</option>
            <option v-for="name in classOptions" :key="name" :value="name">{{ name }}</option>
          </select>
        </label>
        <label class="filter-item">
          <span>学号</span>
          <input v-model="filters.student_no" type="text" placeholder="学号（可选）" :disabled="isLoading" @keyup.enter="handleSearch" />
        </label>
        <label class="filter-item">
          <span>账号状态</span>
          <select v-model="filters.is_enabled" :disabled="isLoading">
            <option value="all">全部</option>
            <option value="enabled">启用</option>
            <option value="disabled">停用</option>
          </select>
        </label>
        <label class="filter-item">
          <span>排序字段</span>
          <select v-model="filters.sort_by" :disabled="isLoading">
            <option value="created_at">创建时间</option>
            <option value="username">用户名</option>
            <option value="full_name">姓名</option>
            <option value="student_no">学号</option>
            <option value="class_name">班级</option>
            <option value="is_enabled">账号状态</option>
          </select>
        </label>
        <label class="filter-item">
          <span>排序方向</span>
          <select v-model="filters.sort_order" :disabled="isLoading">
            <option value="desc">降序</option>
            <option value="asc">升序</option>
          </select>
        </label>
      </div>
      <div class="filter-actions">
        <button type="button" class="btn primary" :disabled="isLoading" @click="handleSearch">查询</button>
        <button type="button" class="btn plain" :disabled="isLoading" @click="handleResetFilters">重置</button>
        <button type="button" class="btn plain" :disabled="isExporting || isLoading" @click="handleExport">
          {{ isExporting ? "导出中..." : "导出当前筛选" }}
        </button>
      </div>
    </article>

    <article class="panel">
      <div class="table-header">
        <h3>{{ title }}</h3>
        <div class="table-meta">共 {{ pagination.total }} 条，当前第 {{ pagination.page }} / {{ totalPagesText }} 页</div>
      </div>

      <div class="batch-ops">
        <span class="batch-meta">已选 {{ selectedCount }} 人</span>
        <div class="batch-actions">
          <button type="button" class="btn plain" :disabled="isLoading || students.length === 0" @click="toggleSelectCurrentPage">
            {{ isAllCurrentPageSelected ? "取消全选当前页" : "全选当前页" }}
          </button>
          <button type="button" class="btn plain" :disabled="selectedCount === 0 || isLoading" @click="clearSelection">清空选择</button>
          <button type="button" class="btn success" :disabled="selectedCount === 0 || isLoading || isActioning" @click="handleBatchEnable">批量启用</button>
          <button type="button" class="btn danger" :disabled="selectedCount === 0 || isLoading || isActioning" @click="handleBatchDisable">批量停用</button>
          <button type="button" class="btn plain" :disabled="selectedCount === 0 || isLoading || isActioning" @click="handleBatchResetPassword">
            批量重置密码
          </button>
        </div>
      </div>

      <p v-if="isLoading" class="hint">正在加载学生账号...</p>
      <p v-else-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      <p v-else-if="students.length === 0" class="hint">{{ emptyText }}</p>
      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>选择</th>
              <th>姓名</th>
              <th>学号</th>
              <th>班级</th>
              <th>用户名</th>
              <th>账号状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in students" :key="item.user_id">
              <td>
                <input type="checkbox" :checked="selectedUserIds.includes(item.user_id)" :disabled="isLoading || isActioning" @change="toggleUserSelection(item.user_id, $event.target.checked)" />
              </td>
              <td>{{ item.full_name || "-" }}</td>
              <td>{{ item.student_no || "-" }}</td>
              <td>{{ item.class_name || "-" }}</td>
              <td>{{ item.username }}</td>
              <td>
                <span :class="['status-tag', item.is_enabled ? 'enabled' : 'disabled']">{{ item.is_enabled ? "启用" : "停用" }}</span>
              </td>
              <td>{{ formatTime(item.created_at) }}</td>
              <td class="actions">
                <button type="button" class="btn mini success" :disabled="item.is_enabled || isActioning" @click="handleSingleEnable(item)">启用</button>
                <button type="button" class="btn mini danger" :disabled="!item.is_enabled || isActioning" @click="handleSingleDisable(item)">停用</button>
                <button type="button" class="btn mini plain" :disabled="isActioning" @click="handleSingleResetPassword(item)">重置密码</button>
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
          <span>条</span>
        </div>
        <div class="page-actions">
          <button type="button" class="btn plain" :disabled="isLoading || pagination.page <= 1" @click="goPrevPage">上一页</button>
          <span>第 {{ pagination.page }} / {{ totalPagesText }} 页</span>
          <button type="button" class="btn plain" :disabled="isLoading || pagination.page >= pagination.total_pages || pagination.total_pages === 0" @click="goNextPage">下一页</button>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";

const props = defineProps({
  api: { type: Object, required: true },
  title: { type: String, default: "学生账号列表" },
  emptyText: { type: String, default: "当前筛选条件下无学生数据" },
  showClassFilter: { type: Boolean, default: true },
  exportFilename: { type: String, default: "学生账号清单.xlsx" },
});

defineExpose({ reload: () => loadStudents({ preserveSelection: false }) });

const students = ref([]);
const isLoading = ref(false);
const isActioning = ref(false);
const isExporting = ref(false);
const isClassOptionsLoading = ref(false);
const errorMessage = ref("");
const actionMessage = ref("");
const actionError = ref(false);
const selectedUserIds = ref([]);
const classOptions = ref([]);

const filters = ref({
  keyword: "",
  class_name: "",
  student_no: "",
  is_enabled: "all",
  sort_by: "created_at",
  sort_order: "desc",
});

const pagination = ref({ page: 1, page_size: 10, total: 0, total_pages: 0 });
const totalPagesText = computed(() => (pagination.value.total_pages > 0 ? pagination.value.total_pages : 1));
const selectedCount = computed(() => selectedUserIds.value.length);
const isAllCurrentPageSelected = computed(() => students.value.length > 0 && students.value.every((item) => selectedUserIds.value.includes(item.user_id)));

function formatTime(value) {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function buildListQueryParams() {
  const params = {
    page: pagination.value.page,
    page_size: pagination.value.page_size,
    keyword: filters.value.keyword.trim(),
    student_no: filters.value.student_no.trim(),
    sort_by: filters.value.sort_by,
    sort_order: filters.value.sort_order,
  };
  if (props.showClassFilter) {
    params.class_name = filters.value.class_name.trim();
  }
  if (filters.value.is_enabled === "enabled") params.is_enabled = true;
  if (filters.value.is_enabled === "disabled") params.is_enabled = false;
  return params;
}

function triggerFileDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

function setActionMessage(text, isError = false) {
  actionMessage.value = text;
  actionError.value = isError;
}

function resetActionMessage() {
  actionMessage.value = "";
  actionError.value = false;
}

async function loadStudents({ preserveSelection = true } = {}) {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const data = await props.api.list(buildListQueryParams());
    students.value = data.items || [];
    pagination.value.total = data.total || 0;
    pagination.value.total_pages = data.total_pages || 0;
    pagination.value.page = data.page || pagination.value.page;
    pagination.value.page_size = data.page_size || pagination.value.page_size;
    if (preserveSelection) {
      const currentIds = new Set(students.value.map((item) => item.user_id));
      selectedUserIds.value = selectedUserIds.value.filter((id) => currentIds.has(id));
    } else {
      selectedUserIds.value = [];
    }
  } catch (error) {
    errorMessage.value = `学生列表加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

async function loadClassOptions() {
  if (!props.showClassFilter || !props.api.classOptions) return;
  isClassOptionsLoading.value = true;
  try {
    const options = await props.api.classOptions();
    classOptions.value = Array.isArray(options) ? options : [];
  } catch (error) {
    setActionMessage(`班级选项加载失败：${error.message}`, true);
  } finally {
    isClassOptionsLoading.value = false;
  }
}

async function handleSearch() {
  pagination.value.page = 1;
  await loadStudents({ preserveSelection: false });
}

async function handleResetFilters() {
  filters.value = { keyword: "", class_name: "", student_no: "", is_enabled: "all", sort_by: "created_at", sort_order: "desc" };
  pagination.value.page = 1;
  await loadStudents({ preserveSelection: false });
}

function toggleUserSelection(userId, checked) {
  selectedUserIds.value = checked ? Array.from(new Set([...selectedUserIds.value, userId])) : selectedUserIds.value.filter((id) => id !== userId);
}

function toggleSelectCurrentPage() {
  const currentIds = students.value.map((item) => item.user_id);
  if (isAllCurrentPageSelected.value) {
    selectedUserIds.value = selectedUserIds.value.filter((id) => !currentIds.includes(id));
    return;
  }
  selectedUserIds.value = Array.from(new Set([...selectedUserIds.value, ...currentIds]));
}

function clearSelection() {
  selectedUserIds.value = [];
}

function promptNewPassword() {
  const value = window.prompt("请输入新密码（不少于6位）", "123456");
  if (value === null) return null;
  const cleaned = value.trim();
  if (cleaned.length < 6) {
    window.alert("密码长度不能少于 6 位");
    return null;
  }
  return cleaned;
}

async function handleSingleEnable(item) {
  if (!window.confirm(`确认启用账号：${item.username}？`)) return;
  isActioning.value = true;
  resetActionMessage();
  try {
    await props.api.enable(item.user_id);
    setActionMessage(`账号已启用：${item.username}`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`启用失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleSingleDisable(item) {
  if (!window.confirm(`确认停用账号：${item.username}？`)) return;
  isActioning.value = true;
  resetActionMessage();
  try {
    await props.api.disable(item.user_id);
    setActionMessage(`账号已停用：${item.username}`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`停用失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleSingleResetPassword(item) {
  const newPassword = promptNewPassword();
  if (!newPassword || !window.confirm(`确认重置账号 ${item.username} 的密码？`)) return;
  isActioning.value = true;
  resetActionMessage();
  try {
    if (props.api.resetPassword) {
      await props.api.resetPassword(item.user_id, { new_password: newPassword });
      setActionMessage(`账号密码已重置：${item.username}`);
    } else {
      const result = await props.api.batchResetPassword({ user_ids: [item.user_id], new_password: newPassword });
      setActionMessage(`已成功重置 ${result.success_count} 个账号密码`);
    }
    await loadStudents();
  } catch (error) {
    setActionMessage(`重置密码失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleBatchEnable() {
  if (selectedUserIds.value.length === 0 || !window.confirm(`确认批量启用已选 ${selectedUserIds.value.length} 个账号？`)) return;
  isActioning.value = true;
  resetActionMessage();
  try {
    const result = await props.api.batchEnable({ user_ids: selectedUserIds.value });
    setActionMessage(`批量启用完成：成功 ${result.success_count} 个，失败 ${result.failed_count} 个`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`批量启用失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleBatchDisable() {
  if (selectedUserIds.value.length === 0 || !window.confirm(`确认批量停用已选 ${selectedUserIds.value.length} 个账号？`)) return;
  isActioning.value = true;
  resetActionMessage();
  try {
    const result = await props.api.batchDisable({ user_ids: selectedUserIds.value });
    setActionMessage(`批量停用完成：成功 ${result.success_count} 个，失败 ${result.failed_count} 个`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`批量停用失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleBatchResetPassword() {
  const newPassword = promptNewPassword();
  if (!newPassword || selectedUserIds.value.length === 0 || !window.confirm(`确认批量重置已选 ${selectedUserIds.value.length} 个账号密码？`)) return;
  isActioning.value = true;
  resetActionMessage();
  try {
    const result = await props.api.batchResetPassword({ user_ids: selectedUserIds.value, new_password: newPassword });
    setActionMessage(`已成功重置 ${result.success_count} 个账号密码，失败 ${result.failed_count} 个`);
    await loadStudents();
  } catch (error) {
    setActionMessage(`批量重置密码失败：${error.message}`, true);
  } finally {
    isActioning.value = false;
  }
}

async function handleExport() {
  isExporting.value = true;
  resetActionMessage();
  try {
    const query = buildListQueryParams();
    delete query.page;
    delete query.page_size;
    const blob = await props.api.export(query);
    triggerFileDownload(blob, props.exportFilename);
    setActionMessage("导出成功");
  } catch (error) {
    setActionMessage(`导出失败：${error.message}`, true);
  } finally {
    isExporting.value = false;
  }
}

async function handlePageSizeChange() {
  pagination.value.page = 1;
  await loadStudents({ preserveSelection: false });
}

async function goPrevPage() {
  if (pagination.value.page <= 1) return;
  pagination.value.page -= 1;
  await loadStudents({ preserveSelection: false });
}

async function goNextPage() {
  if (pagination.value.page >= pagination.value.total_pages) return;
  pagination.value.page += 1;
  await loadStudents({ preserveSelection: false });
}

onMounted(async () => {
  await loadClassOptions();
  await loadStudents({ preserveSelection: false });
});
</script>

<style scoped>
.student-manage {
  display: grid;
  gap: 16px;
}
.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}
.success {
  border-color: var(--success-border);
  background: var(--success-soft);
  color: var(--success-strong);
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
.filter-panel h3,
.table-header h3 {
  margin: 0;
}
.filter-grid {
  margin-top: 12px;
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}
.filter-item {
  display: grid;
  gap: 6px;
}
.filter-item span,
.table-meta,
.batch-meta,
.hint {
  color: var(--text-muted);
}
.filter-item input,
.filter-item select,
.page-size select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
  font: inherit;
}
.filter-actions,
.batch-actions,
.pagination,
.page-size,
.page-actions,
.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}
.filter-actions,
.batch-ops {
  margin-top: 12px;
}
.table-header,
.batch-ops {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}
.table-wrap {
  margin-top: 12px;
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  border-bottom: 1px solid var(--border-soft);
  padding: 10px;
  text-align: left;
  white-space: nowrap;
}
.btn {
  border: 0;
  border-radius: 8px;
  padding: 8px 12px;
  font-weight: 600;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
.status-tag {
  border-radius: 999px;
  padding: 4px 9px;
  font-size: 13px;
  font-weight: 700;
}
.status-tag.enabled {
  background: var(--success-soft);
  color: var(--success-strong);
}
.status-tag.disabled {
  background: var(--danger-soft);
  color: var(--danger-strong);
}
.pagination {
  margin-top: 14px;
  justify-content: space-between;
}
.error-text {
  color: var(--danger-strong);
}
@media (max-width: 860px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
  .table-header,
  .batch-ops,
  .pagination {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
