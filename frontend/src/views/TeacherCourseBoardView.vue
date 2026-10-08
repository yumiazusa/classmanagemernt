<template>
  <section class="page">
    <article class="panel hero">
      <div>
        <h2>课程管理</h2>
        <p>查看分配给你的课程，按课程管理学生与课程文档。</p>
      </div>
    </article>
    <article v-if="isLoading" class="panel">正在加载课程...</article>
    <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>
    <article v-else-if="courses.length === 0" class="panel">暂无分配给你的课程</article>
    <div v-else class="grid">
      <article v-for="course in courses" :key="course.id" class="panel course-card">
        <h3>{{ course.title }}</h3>
        <div class="meta">
          <span>{{ course.class_count }} 班级</span>
          <span>{{ canEnter(course) ? "已开放" : "未开放" }}</span>
        </div>
        <div class="card-actions">
          <RouterLink v-if="canEnter(course)" class="btn primary" :to="`/courses/${course.id}/experience`">进入课程</RouterLink>
          <span v-else class="btn unavailable">课程模块暂不可进入</span>
          <RouterLink class="btn plain" :to="`/teacher/courses/${course.id}/students`">学生管理</RouterLink>
          <RouterLink class="btn plain" :to="`/teacher/courses/${course.id}/submissions`">提交批阅 · 开发中</RouterLink>
          <RouterLink class="btn plain" :to="`/courses/${course.id}/docs`">文档阅读</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getTeacherCourses } from "../api/teacher-course";
import { courseExperiences } from "../course-experiences/registry";

const courses = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");
const canEnter = (course) => course.is_active && course.status === "published" && Boolean(courseExperiences[course.experience_key]);

async function loadCourses() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    courses.value = await getTeacherCourses();
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
  gap: 14px;
}
.panel {
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
h2,
h3 {
  margin: 0;
}
p {
  margin: 8px 0 0;
  color: var(--text-muted);
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}
.course-card {
  display: grid;
  gap: 12px;
}
.card-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
  display: inline-flex;
  justify-content: center;
  border-radius: 10px;
  padding: 10px 14px;
  text-decoration: none;
  font-weight: 700;
}
.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}
.plain {
  background: var(--surface-2);
  color: var(--text-strong);
}
.unavailable { background: var(--surface-2); color: var(--text-muted); cursor: default; }
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
</style>
