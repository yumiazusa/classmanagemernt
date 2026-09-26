<template>
  <section class="page">
    <article class="panel hero">
      <div>
        <RouterLink class="back-button" :to="`/admin/classes/${classId}/students`">返回学生列表</RouterLink>
        <h2>{{ classInfo?.name || "添加学生" }}</h2>
        <p>单个添加或批量导入学生，账号会自动归属到当前班级。</p>
      </div>
      <div class="summary">
        <span>{{ classInfo?.member_count || 0 }} 名学生</span>
        <span>{{ classInfo?.course_count || 0 }} 门课程</span>
      </div>
    </article>

    <article v-if="isLoadingClass" class="panel">正在加载班级信息...</article>
    <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>

    <StudentImportPanel
      v-else-if="classInfo"
      :api="importApi"
      :show-class-input="false"
      title="添加当前班级学生"
      hint="单个添加无需选择班级；批量导入模板可包含班级列，但系统会优先绑定到当前班级。"
      @imported="loadClassInfo"
    />
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import {
  createAdminClassStudent,
  downloadAdminClassStudentImportTemplate,
  getAdminClassById,
  importAdminClassStudents,
} from "../api/admin-course";
import StudentImportPanel from "../components/StudentImportPanel.vue";

const route = useRoute();
const classId = computed(() => Number(route.params.classId));
const classInfo = ref(null);
const isLoadingClass = ref(false);
const errorMessage = ref("");

const importApi = computed(() => ({
  createOne: (payload) => createAdminClassStudent(classId.value, payload),
  importFile: (file) => importAdminClassStudents(classId.value, file),
  downloadTemplate: () => downloadAdminClassStudentImportTemplate(classId.value),
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
  padding: 18px;
}
.hero {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: flex-start;
}
h2 {
  margin: 8px 0 0;
}
p {
  margin: 8px 0 0;
  color: var(--text-muted);
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
  font-weight: 700;
  text-decoration: none;
}
.summary {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-end;
}
.summary span {
  border-radius: 999px;
  background: var(--brand-soft);
  color: var(--brand-700);
  padding: 5px 10px;
  font-size: 13px;
  font-weight: 700;
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
@media (max-width: 760px) {
  .hero {
    flex-direction: column;
  }
}
</style>
