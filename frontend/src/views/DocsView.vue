<template>
  <section class="docs-page">
    <article class="card top-card">
      <div>
        <h2>平台资料</h2>
        <p>浏览平台指南、课程配置说明和教学资料。</p>
      </div>
      <form class="search-row" @submit.prevent="handleSearch">
        <input v-model.trim="keyword" type="text" placeholder="搜索标题 / 摘要 / 正文" />
        <select v-model="categoryFilter">
          <option value="all">全部分类</option>
          <option v-for="item in categories" :key="item" :value="item">{{ item }}</option>
        </select>
        <button type="submit" :disabled="isLoadingList">搜索</button>
      </form>
    </article>

    <article class="card docs-layout">
      <aside class="doc-sidebar">
        <h3>资料目录</h3>
        <p v-if="isLoadingList" class="side-hint">正在加载资料列表...</p>
        <p v-else-if="listError" class="side-hint error">{{ listError }}</p>
        <p v-else-if="catalogGroups.length === 0" class="side-hint">暂无资料</p>
        <section v-for="group in catalogGroups" v-else :key="group.title" class="tree-group">
          <h4>{{ group.title }}</h4>
          <button
            v-for="item in group.items"
            :key="item.slug"
            type="button"
            :class="['tree-item', selectedSlug === item.slug ? 'active' : '']"
            @click="selectDoc(item.slug)"
          >
            {{ item.title }}
          </button>
        </section>
      </aside>

      <main class="doc-content">
        <header class="doc-head">
          <h3>{{ docDetail?.title || "平台资料" }}</h3>
          <span>{{ docDetail?.updated_at ? `更新时间：${formatTime(docDetail.updated_at)}` : "" }}</span>
        </header>
        <p v-if="detailError" class="content-error">{{ detailError }}</p>
        <p v-else-if="isLoadingDetail" class="content-hint">正在加载资料内容...</p>
        <article v-else class="markdown-body" v-html="renderedHtml"></article>
      </main>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import MarkdownIt from "markdown-it";
import hljs from "highlight.js/lib/core";
import javascriptLang from "highlight.js/lib/languages/javascript";
import sqlLang from "highlight.js/lib/languages/sql";
import "highlight.js/styles/github.css";

import { getDocBySlug, getDocCategories, getDocs } from "../api/docs";
import { formatApiDateTime } from "../utils/datetime";

hljs.registerLanguage("javascript", javascriptLang);
hljs.registerLanguage("sql", sqlLang);

const md = new MarkdownIt({
  html: false,
  linkify: true,
  typographer: true,
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return `<pre class="hljs"><code>${hljs.highlight(code, { language: lang }).value}</code></pre>`;
    }
    return `<pre class="hljs"><code>${md.utils.escapeHtml(code)}</code></pre>`;
  },
});

const keyword = ref("");
const categoryFilter = ref("all");
const categories = ref([]);
const docs = ref([]);
const selectedSlug = ref("");
const docDetail = ref(null);
const isLoadingList = ref(false);
const isLoadingDetail = ref(false);
const listError = ref("");
const detailError = ref("");

const catalogGroups = computed(() => {
  const bucket = new Map();
  docs.value.forEach((item) => {
    const category = item.category || "未分类";
    if (!bucket.has(category)) {
      bucket.set(category, []);
    }
    bucket.get(category).push(item);
  });
  return Array.from(bucket.entries()).map(([title, items]) => ({ title, items }));
});

const renderedHtml = computed(() => {
  if (!docDetail.value) {
    return md.render("# 欢迎使用平台资料\n\n请从左侧选择一篇资料。");
  }
  return md.render(docDetail.value.content || "暂无内容");
});

function formatTime(value) {
  return formatApiDateTime(value);
}

async function loadDocs() {
  isLoadingList.value = true;
  listError.value = "";
  try {
    const params = { keyword: keyword.value };
    if (categoryFilter.value !== "all") {
      params.category = categoryFilter.value;
    }
    docs.value = await getDocs(params);
    if (!selectedSlug.value && docs.value.length > 0) {
      await selectDoc(docs.value[0].slug);
    }
  } catch (error) {
    listError.value = error.message || "资料列表加载失败";
  } finally {
    isLoadingList.value = false;
  }
}

async function loadCategories() {
  try {
    categories.value = await getDocCategories();
  } catch (error) {
    categories.value = [];
  }
}

async function selectDoc(slug) {
  selectedSlug.value = slug;
  isLoadingDetail.value = true;
  detailError.value = "";
  try {
    docDetail.value = await getDocBySlug(slug);
  } catch (error) {
    detailError.value = error.message || "资料内容加载失败";
  } finally {
    isLoadingDetail.value = false;
  }
}

function handleSearch() {
  selectedSlug.value = "";
  docDetail.value = null;
  loadDocs();
}

onMounted(async () => {
  await Promise.all([loadCategories(), loadDocs()]);
});
</script>

<style scoped>
.docs-page {
  display: grid;
  gap: 14px;
}
.card {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}
.top-card {
  display: grid;
  gap: 14px;
}
h2,
h3,
h4 {
  margin: 0;
}
p {
  margin: 8px 0 0;
  color: var(--text-muted);
}
.search-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 180px 96px;
  gap: 10px;
}
input,
select,
button {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
}
button {
  background: var(--brand-600);
  color: var(--surface-1);
  font-weight: 700;
  cursor: pointer;
}
.docs-layout {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 18px;
  align-items: start;
}
.doc-sidebar {
  display: grid;
  gap: 14px;
}
.tree-group {
  display: grid;
  gap: 8px;
}
.tree-item {
  width: 100%;
  text-align: left;
  background: var(--surface-2);
  color: var(--text-body);
}
.tree-item.active {
  background: var(--brand-soft);
  color: var(--brand-700);
}
.doc-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--border-soft);
  padding-bottom: 12px;
  margin-bottom: 16px;
}
.doc-head span,
.side-hint {
  color: var(--text-muted);
}
.content-error,
.error {
  color: var(--danger-strong);
}
.markdown-body {
  line-height: 1.75;
}
@media (max-width: 860px) {
  .docs-layout,
  .search-row {
    grid-template-columns: 1fr;
  }
}
</style>
