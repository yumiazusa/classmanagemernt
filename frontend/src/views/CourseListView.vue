<template>
  <section class="page">
    <article class="panel hero">
      <div>
        <h2>我的课程</h2>
        <p>进入已开放的课程模块。</p>
      </div>
      <RouterLink class="btn primary" to="/dashboard">个人主页</RouterLink>
    </article>

    <article v-if="isLoading" class="panel">正在加载课程...</article>
    <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>
    <article v-else-if="courses.length === 0" class="panel">暂无可用课程</article>

    <div v-else class="course-grid">
      <RouterLink v-for="course in courses" :key="course.id" class="course-card" :to="`/courses/${course.id}/experience`">
        <div class="course-mark" :style="{ background: course.cover_color || '#dbeafe' }"></div>
        <div class="course-main">
          <div class="course-head">
            <h3>{{ course.title }}</h3>
            <span class="status">{{ courseExperiences[course.experience_key]?.label || "课程模块" }}</span>
          </div>
          <div class="meta-row">
            <span>{{ course.class_count }} 个班级</span>
          </div>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getCourses } from "../api/course";
import { courseExperiences } from "../course-experiences/registry";

const courses = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");

async function loadCourses() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    courses.value = await getCourses();
  } catch (error) {
    errorMessage.value = `课程加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadCourses);
</script>

<style scoped>
.page {
  display: grid;
  gap: 16px;
}
.panel,
.course-card {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}
.hero {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
}
.hero h2,
.course-head h3 {
  margin: 0;
}
.hero p,
.course-card p {
  margin: 8px 0 0;
  color: var(--text-muted);
}
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}
.course-card {
  display: grid;
  grid-template-columns: 10px minmax(0, 1fr);
  gap: 14px;
  color: inherit;
  text-decoration: none;
  transition: transform 160ms ease, border-color 160ms ease;
}
.course-card:hover {
  border-color: var(--brand-300);
  transform: translateY(-2px);
}
.course-mark {
  border-radius: 999px;
}
.course-head,
.meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.status,
.meta-row span {
  border-radius: 999px;
  padding: 4px 10px;
  background: var(--brand-soft);
  color: var(--brand-700);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}
.meta-row {
  justify-content: flex-start;
  flex-wrap: wrap;
  margin-top: 14px;
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
.btn {
  border-radius: 10px;
  padding: 10px 14px;
  text-decoration: none;
  font-weight: 700;
}
.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}
@media (max-width: 680px) {
  .hero {
    align-items: stretch;
    flex-direction: column;
  }
}
</style>
