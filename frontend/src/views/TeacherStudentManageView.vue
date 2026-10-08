<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>{{ courseId ? `${courseTitle} · 学生管理` : "学生管理" }}</h2>
      <p class="header-desc">{{ courseId ? "仅显示当前课程关联班级的学生。" : "显示你负责课程关联班级的学生。" }}支持筛选、启停用、重置密码与导出账号清单。</p>
      <div class="toolbar">
        <RouterLink class="btn back-nav" to="/teacher/courses">返回课程管理</RouterLink>
        <RouterLink class="btn import-nav" :to="courseId ? `/teacher/courses/${courseId}/students/import` : '/teacher/student-import'">添加/导入学生</RouterLink>
      </div>
    </article>

    <article v-if="isLoadingCourse" class="panel">正在加载课程...</article>
    <article v-else-if="courseError" class="panel error">{{ courseError }}</article>

    <StudentManagePanel v-else :key="courseId" :api="studentApi" />
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { getTeacherCourse } from "../api/teacher-course";
import {
  batchDisableTeacherStudents,
  batchEnableTeacherStudents,
  batchResetTeacherStudentPasswords,
  disableTeacherStudent,
  enableTeacherStudent,
  exportTeacherStudents,
  getTeacherStudentClassOptions,
  getTeacherStudents,
  resetTeacherStudentPassword,
} from "../api/teacher";
import StudentManagePanel from "../components/StudentManagePanel.vue";

const route = useRoute();
const courseId = computed(() => route.params.id ? Number(route.params.id) : null);
const courseTitle = ref("课程");
const isLoadingCourse = ref(false);
const courseError = ref("");

const studentApi = {
  list: (params) => getTeacherStudents({ ...params, course_id: courseId.value }),
  classOptions: () => getTeacherStudentClassOptions(courseId.value),
  export: (params) => exportTeacherStudents({ ...params, course_id: courseId.value }),
  enable: (userId) => enableTeacherStudent(userId, courseId.value),
  disable: (userId) => disableTeacherStudent(userId, courseId.value),
  resetPassword: (userId, payload) => resetTeacherStudentPassword(userId, payload, courseId.value),
  batchEnable: (payload) => batchEnableTeacherStudents(payload, courseId.value),
  batchDisable: (payload) => batchDisableTeacherStudents(payload, courseId.value),
  batchResetPassword: (payload) => batchResetTeacherStudentPasswords(payload, courseId.value),
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
  font-size: clamp(30px, 2.45vw, 43px);
  line-height: 1.2;
}
.header-desc,
.header-hint {
  color: var(--text-muted);
  margin: 8px 0 0;
}
.toolbar {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  min-height: 44px;
  padding: 9px 12px;
  text-decoration: none;
  font-weight: 700;
}
.back-nav {
  background: var(--text-strong);
  color: var(--surface-1);
}
.import-nav {
  background: var(--accent-teal-strong);
  color: var(--surface-1);
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
</style>
