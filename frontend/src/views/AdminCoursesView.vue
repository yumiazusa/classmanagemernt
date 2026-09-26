<template>
  <section class="page">
    <article class="panel hero">
      <div>
        <h2>课程管理</h2>
        <p>创建课程并维护基础发布状态，模块和任务可在创建后快速补充。</p>
      </div>
    </article>

    <article class="panel form-panel">
      <div class="form-grid">
        <input v-model.trim="form.title" placeholder="课程标题" />
        <input v-model.trim="form.slug" placeholder="slug，例如 design-thinking" />
        <select v-model="form.status">
          <option v-for="(label, value) in courseStatusLabels" :key="value" :value="value">{{ label }}</option>
        </select>
        <input v-model.trim="form.summary" placeholder="课程简介" />
      </div>
      <button class="btn primary" type="button" @click="createCourse">新建课程</button>
    </article>

    <article v-if="message" :class="['panel', messageType]">{{ message }}</article>
    <article v-if="isLoading" class="panel">正在加载课程...</article>

    <div class="list">
      <article v-for="course in courses" :key="course.id" class="panel course">
        <div>
          <h3>{{ course.title }}</h3>
          <p>{{ course.summary || "暂无课程简介" }}</p>
          <div class="meta">
            <span>{{ courseStatusLabels[course.status] || course.status }}</span>
            <span>{{ course.module_count }} 模块</span>
            <span>{{ course.task_count }} 任务</span>
          </div>
        </div>
        <div class="actions">
          <RouterLink class="btn plain" :to="`/courses/${course.id}`">预览</RouterLink>
          <button class="btn danger" type="button" @click="removeCourse(course)">删除</button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import { createAdminCourse, deleteAdminCourse, getAdminCourses } from "../api/admin-course";
import { platformConfig } from "../config/platform";

const courses = ref([]);
const isLoading = ref(false);
const message = ref("");
const messageType = ref("success");
const { courseStatusLabels } = platformConfig;
const form = reactive({ title: "", slug: "", status: "draft", summary: "" });

async function loadCourses() {
  isLoading.value = true;
  try {
    const data = await getAdminCourses({ page: 1, page_size: 100 });
    courses.value = data.items || [];
  } catch (error) {
    message.value = `课程加载失败：${error.message}`;
    messageType.value = "error";
  } finally {
    isLoading.value = false;
  }
}

async function createCourse() {
  message.value = "";
  if (!form.title || !form.slug) {
    message.value = "课程标题和 slug 必填";
    messageType.value = "error";
    return;
  }
  try {
    await createAdminCourse({ ...form, is_active: true, sort_order: 0 });
    form.title = "";
    form.slug = "";
    form.summary = "";
    form.status = "draft";
    message.value = "课程已创建";
    messageType.value = "success";
    await loadCourses();
  } catch (error) {
    message.value = `创建失败：${error.message}`;
    messageType.value = "error";
  }
}

async function removeCourse(course) {
  if (!window.confirm(`确认删除课程「${course.title}」吗？`)) {
    return;
  }
  try {
    await deleteAdminCourse(course.id);
    message.value = "课程已删除";
    messageType.value = "success";
    await loadCourses();
  } catch (error) {
    message.value = `删除失败：${error.message}`;
    messageType.value = "error";
  }
}

onMounted(loadCourses);
</script>

<style scoped>
.page,
.list {
  display: grid;
  gap: 14px;
}
.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}
.hero,
.course,
.actions {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}
h2,
h3 {
  margin: 0;
}
p {
  margin: 8px 0 0;
  color: var(--text-muted);
}
.form-panel {
  display: grid;
  gap: 12px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}
input,
select {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}
.meta span {
  border-radius: 999px;
  background: var(--brand-soft);
  color: var(--brand-700);
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 700;
}
.btn {
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  text-decoration: none;
  font-weight: 700;
  cursor: pointer;
}
.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}
.plain {
  background: var(--surface-2);
  color: var(--text-strong);
}
.danger {
  background: var(--danger-soft);
  color: var(--danger-strong);
}
.success {
  color: var(--success-strong);
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
@media (max-width: 860px) {
  .hero,
  .course,
  .actions {
    flex-direction: column;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
