<template>
  <section class="admin-docs-page">
    <article class="panel head-panel">
      <h2>文档管理</h2>
      <p>管理教学文档（新建、编辑、删除、发布控制）。</p>
    </article>

    <article class="panel filter-panel">
      <div class="filter-row">
        <input v-model.trim="filters.keyword" type="text" placeholder="搜索标题 / 摘要 / 正文" />
        <select v-model="filters.category">
          <option value="all">全部分类</option>
          <option v-for="item in categories" :key="item" :value="item">{{ item }}</option>
        </select>
        <button type="button" class="btn primary" :disabled="isLoading" @click="loadDocs">查询</button>
      </div>
    </article>

    <article v-if="message" :class="['panel', messageIsError ? 'error' : 'success']">{{ message }}</article>
    <article class="layout-grid">
      <section class="panel list-panel">
        <div class="list-header">
          <strong>文档列表（{{ docs.length }}）</strong>
          <button type="button" class="btn plain" @click="startCreate">新建文档</button>
        </div>

        <p v-if="isLoading" class="hint">正在加载文档...</p>
        <p v-else-if="docs.length === 0" class="hint">暂无文档</p>

        <ul v-else class="doc-list">
          <li v-for="item in docs" :key="item.id" :class="['doc-item', editingId === item.id ? 'active' : '']">
            <div class="doc-main">
              <div class="title-row">
                <strong>{{ item.title }}</strong>
                <span :class="['status', item.is_published ? 'published' : 'draft']">
                  {{ item.is_published ? "已发布" : "未发布" }}
                </span>
              </div>
              <p class="meta">
                分类：{{ item.category || "未分类" }}
                <span class="dot">·</span>
                slug：{{ item.slug }}
                <span class="dot">·</span>
                排序：{{ item.sort_order }}
              </p>
            </div>
            <div class="actions">
              <button type="button" class="btn mini plain" @click="startEdit(item)">编辑</button>
              <button type="button" class="btn mini" :class="item.is_published ? 'warn' : 'success'" @click="togglePublished(item)">
                {{ item.is_published ? "取消发布" : "发布" }}
              </button>
              <button type="button" class="btn mini danger" @click="removeDoc(item)">删除</button>
            </div>
          </li>
        </ul>
      </section>

      <section class="panel form-panel">
        <h3>{{ editingId ? "编辑文档" : "新建文档" }}</h3>
        <div class="form-grid">
          <label class="field">
            <span>标题</span>
            <input v-model.trim="form.title" type="text" placeholder="例如：课程配置说明" />
          </label>
          <label class="field">
            <span>slug</span>
            <input v-model.trim="form.slug" type="text" placeholder="例如：course-config-guide" />
          </label>
          <label class="field">
            <span>分类</span>
            <input
              v-model.trim="form.category"
              type="text"
              list="doc-category-options"
              placeholder="选择已有分类或输入新分类"
            />
          </label>
          <label class="field">
            <span>排序号</span>
            <input v-model.number="form.sort_order" type="number" />
          </label>
          <label class="field checkbox-field">
            <input v-model="form.is_published" type="checkbox" />
            <span>发布（学生可见）</span>
          </label>
        </div>

        <label class="field">
          <span>摘要</span>
          <textarea v-model="form.summary" rows="3" placeholder="简要说明文档内容"></textarea>
        </label>

        <label class="field">
          <span>Markdown 正文</span>
          <textarea v-model="form.content" rows="16" placeholder="# 标题\n\n正文内容"></textarea>
        </label>

        <datalist id="doc-category-options">
          <option v-for="item in categories" :key="`cat-${item}`" :value="item"></option>
        </datalist>

        <div class="form-actions">
          <button type="button" class="btn plain" @click="resetForm">重置</button>
          <button type="button" class="btn primary" :disabled="isSaving" @click="submitForm">
            {{ isSaving ? "保存中..." : editingId ? "保存修改" : "创建文档" }}
          </button>
        </div>
      </section>
    </article>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import {
  createAdminDoc,
  deleteAdminDoc,
  getAdminDocCategories,
  getAdminDocs,
  updateAdminDoc,
} from "../api/admin";

const docs = ref([]);
const categories = ref([]);
const isLoading = ref(false);
const isSaving = ref(false);
const editingId = ref(0);

const message = ref("");
const messageIsError = ref(false);

const filters = reactive({
  keyword: "",
  category: "all",
});

const initialForm = {
  title: "",
  slug: "",
  category: "",
  sort_order: 0,
  is_published: true,
  summary: "",
  content: "",
};

const form = reactive({ ...initialForm });

function setMessage(text, isError = false) {
  message.value = text;
  messageIsError.value = isError;
}

function resetForm() {
  Object.assign(form, initialForm);
  editingId.value = 0;
}

function startCreate() {
  resetForm();
}

function startEdit(item) {
  editingId.value = item.id;
  form.title = item.title || "";
  form.slug = item.slug || "";
  form.category = item.category || "";
  form.sort_order = Number.isFinite(Number(item.sort_order)) ? Number(item.sort_order) : 0;
  form.is_published = Boolean(item.is_published);
  form.summary = item.summary || "";
  form.content = item.content || "";
}

function buildPayload() {
  return {
    title: form.title.trim(),
    slug: form.slug.trim(),
    category: form.category.trim() || "未分类",
    sort_order: Number.isFinite(Number(form.sort_order)) ? Number(form.sort_order) : 0,
    is_published: Boolean(form.is_published),
    summary: form.summary.trim() || null,
    content: form.content,
  };
}

async function loadCategories() {
  try {
    categories.value = await getAdminDocCategories();
  } catch (error) {
    categories.value = [];
  }
}

async function loadDocs() {
  isLoading.value = true;
  setMessage("");
  try {
    docs.value = await getAdminDocs({
      keyword: filters.keyword,
      category: filters.category === "all" ? "" : filters.category,
    });
  } catch (error) {
    setMessage(`文档列表加载失败：${error.message}`, true);
    docs.value = [];
  } finally {
    isLoading.value = false;
  }
}

async function submitForm() {
  setMessage("");
  const payload = buildPayload();
  if (!payload.title) {
    setMessage("标题不能为空", true);
    return;
  }
  if (!payload.slug) {
    setMessage("slug 不能为空", true);
    return;
  }
  if (!payload.content.trim()) {
    setMessage("正文不能为空", true);
    return;
  }

  isSaving.value = true;
  try {
    if (editingId.value) {
      await updateAdminDoc(editingId.value, payload);
      setMessage("文档更新成功");
    } else {
      await createAdminDoc(payload);
      setMessage("文档创建成功");
    }
    await loadCategories();
    await loadDocs();
    resetForm();
  } catch (error) {
    setMessage(`保存失败：${error.message}`, true);
  } finally {
    isSaving.value = false;
  }
}

async function togglePublished(item) {
  const action = item.is_published ? "取消发布" : "发布";
  const confirmed = window.confirm(`确认${action}文档「${item.title}」吗？`);
  if (!confirmed) {
    return;
  }
  try {
    await updateAdminDoc(item.id, { is_published: !item.is_published });
    setMessage(`${action}成功`);
    await loadDocs();
  } catch (error) {
    setMessage(`${action}失败：${error.message}`, true);
  }
}

async function removeDoc(item) {
  const confirmed = window.confirm(`确认删除文档「${item.title}」吗？该操作不可恢复。`);
  if (!confirmed) {
    return;
  }
  try {
    await deleteAdminDoc(item.id);
    setMessage("文档删除成功");
    if (editingId.value === item.id) {
      resetForm();
    }
    await loadCategories();
    await loadDocs();
  } catch (error) {
    setMessage(`删除失败：${error.message}`, true);
  }
}

onMounted(async () => {
  await loadCategories();
  await loadDocs();
});
</script>

<style scoped>
.admin-docs-page {
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

.filter-row {
  display: grid;
  grid-template-columns: 1fr 180px 110px;
  gap: 10px;
}

.filter-row input,
.filter-row select {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
}

.layout-grid {
  display: grid;
  grid-template-columns: 420px minmax(0, 1fr);
  gap: 14px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.hint {
  color: var(--text-subtle);
  margin-top: 10px;
}

.doc-list {
  list-style: none;
  margin: 12px 0 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

.doc-item {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 10px;
  display: grid;
  gap: 8px;
}

.doc-item.active {
  border-color: var(--brand-border-strong);
  background: var(--brand-soft);
}

.title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.meta {
  margin: 0;
  color: var(--text-subtle);
  font-size: 13px;
}

.dot {
  margin: 0 4px;
}

.status {
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 13px;
  font-weight: 600;
}

.status.published {
  background: var(--success-soft);
  color: var(--success-strong);
}

.status.draft {
  background: var(--surface-2);
  color: var(--text-muted);
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.form-panel h3 {
  margin: 0;
}

.form-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.field {
  display: grid;
  gap: 6px;
  margin-top: 10px;
}

.field span {
  color: var(--text-muted);
  font-size: 14px;
}


.field input,
.field textarea {
  border: 1px solid var(--border-strong);
  border-radius: 8px;
  padding: 8px 10px;
  font-family: inherit;
}

.checkbox-field {
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-actions {
  margin-top: 12px;
  display: flex;
  gap: 10px;
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

.btn.warn {
  background: var(--warn-strong);
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

@media (max-width: 1080px) {
  .layout-grid {
    grid-template-columns: 1fr;
  }

  .filter-row {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
