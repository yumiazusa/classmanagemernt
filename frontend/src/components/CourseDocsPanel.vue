<template>
  <section class="section course-docs">
    <div class="section-head">
      <div><h3>课程文档</h3><p class="hint">仅在当前课程中管理，发布后供本课程成员阅读。</p></div>
      <button class="btn secondary" type="button" @click="startCreate">新建课程文档</button>
    </div>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-if="message" class="notice success" role="status">{{ message }}</p>
    <p v-if="loading" class="hint">正在加载课程文档...</p>
    <div v-else class="doc-layout">
      <div class="doc-list">
        <p v-if="!docs.length" class="hint">暂无课程文档</p>
        <div v-for="doc in docs" :key="doc.id" :class="['doc-item', editingId === doc.id ? 'active' : '']">
          <div><strong>{{ doc.title }}</strong><small>{{ doc.is_published ? '已发布' : '未发布' }} · {{ doc.slug }}</small></div>
          <div class="item-actions"><button class="text-button" type="button" @click="startEdit(doc)">编辑</button><button class="text-button danger-text" type="button" @click="removeDoc(doc)">删除</button></div>
        </div>
      </div>
      <form class="doc-form" @submit.prevent="saveDoc">
        <h4>{{ editingId ? '编辑课程文档' : '新建课程文档' }}</h4>
        <label class="field"><span>标题</span><input ref="titleInput" v-model.trim="form.title" required maxlength="200" /></label>
        <label class="field"><span>slug</span><input v-model.trim="form.slug" required maxlength="120" placeholder="例如：course-reading-guide" /></label>
        <label class="field"><span>摘要</span><textarea v-model="form.summary" rows="2" /></label>
        <label class="field"><span>Markdown 正文</span><textarea v-model="form.content" required rows="12" /></label>
        <label class="field"><span>排序号</span><input v-model.number="form.sort_order" type="number" /></label>
        <label class="publish"><input v-model="form.is_published" type="checkbox" />发布给课程成员</label>
        <div class="actions"><button class="btn secondary" type="button" @click="startCreate">重置</button><button class="btn primary" type="submit" :disabled="saving">{{ saving ? '保存中...' : editingId ? '保存修改' : '创建文档' }}</button><RouterLink class="btn secondary" :to="`/admin/courses/${courseId}`">返回课程编辑</RouterLink></div>
      </form>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, reactive, ref, watch } from "vue";
import { createAdminCourseDoc, deleteAdminCourseDoc, getAdminCourseDocs, updateAdminCourseDoc } from "../api/admin-course";

const props = defineProps({ courseId: { type: Number, required: true } });
const courseId = computed(() => props.courseId);
const docs = ref([]);
const loading = ref(false);
const saving = ref(false);
const editingId = ref(0);
const titleInput = ref(null);
const error = ref("");
const message = ref("");
const initial = { title: "", slug: "", summary: "", content: "", sort_order: 0, is_published: true };
const form = reactive({ ...initial });

async function loadDocs() {
  loading.value = true;
  error.value = "";
  try { docs.value = await getAdminCourseDocs(courseId.value); }
  catch (cause) { error.value = `课程文档加载失败：${cause.message}`; }
  finally { loading.value = false; }
}

watch(() => props.courseId, () => { editingId.value = 0; Object.assign(form, initial); error.value = ""; message.value = ""; loadDocs(); }, { immediate: true });

async function startCreate() {
  editingId.value = 0;
  Object.assign(form, initial);
  error.value = "";
  message.value = "";
  await nextTick();
  titleInput.value?.focus();
}

function startEdit(doc) {
  editingId.value = doc.id;
  Object.assign(form, { title: doc.title, slug: doc.slug, summary: doc.summary || "", content: doc.content, sort_order: doc.sort_order, is_published: doc.is_published });
  error.value = "";
  message.value = "";
  nextTick(() => titleInput.value?.focus());
}

async function saveDoc() {
  error.value = "";
  message.value = "";
  const payload = { ...form, title: form.title.trim(), slug: form.slug.trim(), content: form.content.trim(), summary: form.summary.trim() || null };
  if (!payload.title || !payload.slug || !payload.content) { error.value = "请填写标题、slug 和正文"; return; }
  saving.value = true;
  try {
    if (editingId.value) await updateAdminCourseDoc(courseId.value, editingId.value, payload);
    else await createAdminCourseDoc(courseId.value, payload);
    await loadDocs();
    editingId.value = 0;
    Object.assign(form, initial);
    message.value = "课程文档已保存";
  } catch (cause) { error.value = `保存失败：${cause.message}`; }
  finally { saving.value = false; }
}

async function removeDoc(doc) {
  if (!window.confirm(`确认删除课程文档「${doc.title}」吗？`)) return;
  error.value = "";
  message.value = "";
  try {
    await deleteAdminCourseDoc(courseId.value, doc.id);
    if (editingId.value === doc.id) { editingId.value = 0; Object.assign(form, initial); }
    await loadDocs();
    message.value = "课程文档已删除";
  } catch (cause) { error.value = `删除失败：${cause.message}`; }
}
</script>

<style scoped>
.section { background: var(--surface-1); border: 1px solid var(--border-soft); border-radius: 8px; padding: 20px 24px; display: grid; gap: 18px; }
.section-head { display: flex; justify-content: space-between; align-items: start; gap: 12px; }
h3, h4 { margin: 0; }
.hint { margin: 6px 0 0; color: var(--text-muted); font-size: 14px; }
.doc-layout { display: grid; grid-template-columns: minmax(220px, 300px) minmax(0, 1fr); gap: 18px; }
.doc-list, .doc-form { display: grid; align-content: start; gap: 12px; }
.doc-item { border: 1px solid var(--border-soft); border-radius: 8px; padding: 12px; display: grid; gap: 8px; }
.doc-item.active { border-color: var(--brand-600); background: var(--brand-soft); }
.doc-item small { display: block; margin-top: 5px; color: var(--text-muted); overflow-wrap: anywhere; }
.item-actions, .actions { display: flex; gap: 12px; align-items: center; }
.text-button { border: 0; padding: 0; background: none; color: var(--brand-700); font: inherit; font-weight: 700; cursor: pointer; }
.danger-text { color: var(--danger-strong); }
.field { display: grid; gap: 7px; color: var(--text-muted); font-size: 14px; font-weight: 600; }
.field input, .field textarea, .field select { min-width: 0; width: 100%; box-sizing: border-box; border: 1px solid var(--border-soft); border-radius: 8px; padding: 9px 12px; color: var(--text-strong); font: inherit; }
.publish { display: flex; align-items: center; gap: 8px; }
.btn { display: inline-flex; align-items: center; min-height: 42px; border-radius: 8px; padding: 8px 16px; font: inherit; font-weight: 700; text-decoration: none; cursor: pointer; }
.primary { border: 0; background: var(--brand-600); color: var(--surface-1); }
.secondary { border: 1px solid var(--brand-600); background: var(--surface-1); color: var(--brand-700); }
.btn:disabled { opacity: .55; cursor: not-allowed; }
.notice { margin: 0; padding: 12px; border-radius: 8px; }
.error { color: var(--danger-strong); background: var(--danger-soft); }
.success { color: var(--success-strong); background: var(--success-soft); }
@media (max-width: 750px) { .section { padding: 16px; } .section-head { flex-direction: column; } .doc-layout { grid-template-columns: 1fr; } }
</style>
