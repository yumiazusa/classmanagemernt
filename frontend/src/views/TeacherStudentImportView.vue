<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>{{ courseId ? `${courseTitle} · 添加学生` : "添加学生" }}</h2>
      <p>可以单个添加，也可以用 .xlsx 批量导入。学生须属于你负责课程关联的班级。</p>
      <RouterLink class="back-button" :to="courseId ? `/teacher/courses/${courseId}/students` : '/teacher/students'">返回学生管理</RouterLink>
    </article>

    <article v-if="isLoadingCourse" class="panel">正在加载课程...</article>
    <article v-else-if="courseError" class="panel error">{{ courseError }}</article>

    <StudentImportPanel
      v-else
      :key="courseId"
      :api="importApi"
      title="单个添加或批量导入"
      hint="单个添加请选择班级；批量导入模板必须包含班级、学号、姓名。"
    />
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";

import { getTeacherCourse } from "../api/teacher-course";
import { createTeacherStudent, downloadTeacherStudentImportTemplate, getTeacherStudentClassOptions, importTeacherStudents } from "../api/teacher";
import StudentImportPanel from "../components/StudentImportPanel.vue";

const route = useRoute();
const courseId = computed(() => route.params.id ? Number(route.params.id) : null);
const courseTitle = ref("课程");
const isLoadingCourse = ref(false);
const courseError = ref("");
const importApi = {
  createOne: (payload) => createTeacherStudent(payload, courseId.value),
  classOptions: () => getTeacherStudentClassOptions(courseId.value),
  importFile: (file) => importTeacherStudents(file, courseId.value),
  downloadTemplate: downloadTeacherStudentImportTemplate,
};

watch(courseId, async () => {
  isLoadingCourse.value = true;
  courseError.value = "";
  if (!courseId.value) {
    courseTitle.value = "";
    isLoadingCourse.value = false;
    return;
  }
  try {
    courseTitle.value = (await getTeacherCourse(courseId.value)).title;
  } catch (error) {
    courseError.value = `课程加载失败：${error.message}`;
  } finally {
    isLoadingCourse.value = false;
  }
}, { immediate: true });
</script>

<style scoped>
.teacher-page {
  display: grid;
  gap: 16px;
}
.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}
.header-panel h2 {
  margin: 0;
}
.header-panel p {
  margin: 8px 0 12px;
  color: var(--text-subtle);
}
.back-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: fit-content;
  min-height: 38px;
  border-radius: 8px;
  padding: 8px 13px;
  background: var(--neutral-btn);
  color: var(--text-strong);
  text-decoration: none;
  font-weight: 700;
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
</style>
