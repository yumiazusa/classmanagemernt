<template>
  <section class="page">
    <article class="panel hero">
      <div class="class-copy">
        <span class="eyebrow">班级学生管理</span>
        <h2>{{ classInfo?.name || "班级学生管理" }}</h2>
        <p>{{ classInfo?.description || classInfo?.grade || "管理当前班级下的学生账号、导入和批量操作。" }}</p>
      </div>
      <div class="hero-side">
        <div class="summary">
          <span>{{ classInfo?.member_count || 0 }} 名学生</span>
          <span>{{ classInfo?.course_count || 0 }} 门课程</span>
        </div>
        <div class="toolbar">
          <RouterLink class="btn secondary" to="/admin/classes">返回班级管理</RouterLink>
          <RouterLink class="btn primary" :to="`/admin/classes/${classId}/students/import`">添加/导入学生</RouterLink>
        </div>
      </div>
    </article>

    <article v-if="isLoadingClass" class="panel">正在加载班级信息...</article>
    <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>

    <template v-else-if="classInfo">
      <StudentManagePanel
        :api="studentApi"
        :show-class-filter="false"
        :title="`${classInfo.name} 学生列表`"
        empty-text="当前班级暂无学生数据"
      />
    </template>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import {
  batchDisableAdminClassStudents,
  batchEnableAdminClassStudents,
  batchResetAdminClassStudentPasswords,
  disableAdminClassStudent,
  enableAdminClassStudent,
  exportAdminClassStudents,
  getAdminClassById,
  getAdminClassStudents,
  resetAdminClassStudentPassword,
} from "../api/admin-course";
import StudentManagePanel from "../components/StudentManagePanel.vue";

const route = useRoute();
const classInfo = ref(null);
const isLoadingClass = ref(false);
const errorMessage = ref("");
const classId = computed(() => Number(route.params.classId));

const studentApi = computed(() => ({
  list: (params) => getAdminClassStudents(classId.value, params),
  export: (params) => exportAdminClassStudents(classId.value, params),
  enable: (userId) => enableAdminClassStudent(classId.value, userId),
  disable: (userId) => disableAdminClassStudent(classId.value, userId),
  resetPassword: (userId, payload) => resetAdminClassStudentPassword(classId.value, userId, payload),
  batchEnable: (payload) => batchEnableAdminClassStudents(classId.value, payload),
  batchDisable: (payload) => batchDisableAdminClassStudents(classId.value, payload),
  batchResetPassword: (payload) => batchResetAdminClassStudentPasswords(classId.value, payload),
}));

async function loadClassInfo() {
  isLoadingClass.value = true;
  errorMessage.value = "";
  try {
    classInfo.value = await getAdminClassById(classId.value);
  } catch (error) {
    errorMessage.value = `班级信息加载失败：${error.message}`;
  } finally {
    isLoadingClass.value = false;
  }
}

onMounted(loadClassInfo);
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
  padding: 22px 24px;
}
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 28px;
  align-items: center;
}
.class-copy {
  min-width: 0;
}
.hero-side {
  display: flex;
  min-width: 320px;
  flex-direction: column;
  gap: 18px;
  align-items: flex-end;
}
.eyebrow {
  display: inline-flex;
  width: fit-content;
  border-radius: 999px;
  background: var(--brand-soft);
  color: var(--brand-700);
  padding: 5px 11px;
  font-size: 13px;
  font-weight: 700;
}
h2 {
  margin: 12px 0 0;
  font-size: clamp(30px, 2.4vw, 40px);
  line-height: 1.18;
}
p {
  margin: 10px 0 0;
  color: var(--text-muted);
}
.summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.summary span {
  border-radius: 999px;
  background: color-mix(in srgb, var(--brand-soft) 82%, var(--surface-1) 18%);
  color: var(--brand-700);
  padding: 7px 12px;
  font-size: 13px;
  font-weight: 700;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: flex-end;
  align-items: center;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 0;
  border-radius: 10px;
  min-height: 42px;
  padding: 10px 14px;
  font: inherit;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
}
.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}
.secondary {
  background: var(--neutral-btn);
  color: var(--text-strong);
}
.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
@media (max-width: 760px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .hero-side {
    min-width: 0;
    align-items: flex-start;
  }
  .toolbar {
    justify-content: flex-start;
  }
}
</style>
