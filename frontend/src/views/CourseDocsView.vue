<template>
  <section class="page">
    <RouterLink class="back" :to="backTo">返回课程</RouterLink>
    <header class="head"><h2>课程文档</h2><p>阅读本课程已发布的文档。</p></header>
    <p v-if="loading" class="notice">正在加载课程文档...</p>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <div v-if="!loading && !error" class="layout">
      <aside class="list">
        <p v-if="!docs.length" class="hint">暂无已发布的课程文档</p>
        <button v-for="doc in docs" :key="doc.id" type="button" :class="['item', selected?.id === doc.id ? 'active' : '']" @click="selected = doc">{{ doc.title }}</button>
      </aside>
      <article class="content">
        <template v-if="selected"><h3>{{ selected.title }}</h3><p v-if="selected.summary" class="hint">{{ selected.summary }}</p><div class="markdown-body" v-html="renderedHtml"></div></template>
        <p v-else class="hint">请选择一篇文档。</p>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import MarkdownIt from "markdown-it";
import { getStoredCurrentUser } from "../api/auth";
import { getCourseDocs } from "../api/course";

const route = useRoute();
const courseId = computed(() => Number(route.params.id));
const backTo = computed(() => getStoredCurrentUser()?.role === "teacher" ? "/teacher/courses" : `/courses/${courseId.value}/experience`);
const docs = ref([]);
const selected = ref(null);
const loading = ref(false);
const error = ref("");
const md = new MarkdownIt({ html: false, linkify: true });
const renderedHtml = computed(() => md.render(selected.value?.content || ""));

watch(courseId, async () => {
  loading.value = true;
  error.value = "";
  try { docs.value = await getCourseDocs(courseId.value); selected.value = docs.value[0] || null; }
  catch (cause) { error.value = `课程文档加载失败：${cause.message}`; }
  finally { loading.value = false; }
}, { immediate: true });
</script>

<style scoped>
.page { display: grid; gap: 16px; }
.back { color: var(--brand-700); font-weight: 700; text-decoration: none; }
.head, .list, .content, .notice { background: var(--surface-1); border: 1px solid var(--border-soft); border-radius: 10px; padding: 18px; }
h2, h3 { margin: 0; }
.head p, .hint { color: var(--text-muted); }
.layout { display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: 16px; }
.list { display: grid; align-content: start; gap: 8px; }
.item { border: 0; border-radius: 8px; padding: 10px 12px; background: var(--surface-2); color: var(--text-strong); text-align: left; font: inherit; cursor: pointer; }
.item.active { background: var(--brand-soft); color: var(--brand-700); font-weight: 700; }
.content { min-height: 320px; }
.markdown-body { line-height: 1.75; overflow-wrap: anywhere; }
.error { color: var(--danger-strong); background: var(--danger-soft); }
@media (max-width: 700px) { .layout { grid-template-columns: 1fr; } }
</style>
