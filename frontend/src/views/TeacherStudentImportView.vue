<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>添加学生</h2>
      <p>可以单个添加，也可以用 .xlsx 批量导入。教师只能添加到自己课程关联的班级。</p>
      <RouterLink class="back-button" to="/teacher/students">返回学生管理</RouterLink>
    </article>

    <article v-if="isRoleChecking" class="panel">正在验证教师权限...</article>
    <article v-else-if="roleError" class="panel error">{{ roleError }}</article>
    <article v-else-if="!isTeacher" class="panel error">仅教师可访问当前页面</article>

    <StudentImportPanel
      v-else
      :api="importApi"
      title="单个添加或批量导入"
      hint="单个添加请选择班级；批量导入模板必须包含班级、学号、姓名。"
    />
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getCurrentUserProfile } from "../api/auth";
import { createTeacherStudent, downloadTeacherStudentImportTemplate, getTeacherStudentClassOptions, importTeacherStudents } from "../api/teacher";
import StudentImportPanel from "../components/StudentImportPanel.vue";

const isRoleChecking = ref(false);
const roleError = ref("");
const isTeacher = ref(false);
const importApi = {
  createOne: createTeacherStudent,
  classOptions: getTeacherStudentClassOptions,
  importFile: importTeacherStudents,
  downloadTemplate: downloadTeacherStudentImportTemplate,
};

async function verifyTeacherRole() {
  isRoleChecking.value = true;
  roleError.value = "";
  try {
    const user = await getCurrentUserProfile();
    isTeacher.value = user?.role === "teacher";
  } catch (error) {
    isTeacher.value = false;
    roleError.value = `权限验证失败：${error.message}`;
  } finally {
    isRoleChecking.value = false;
  }
}

onMounted(verifyTeacherRole);
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
