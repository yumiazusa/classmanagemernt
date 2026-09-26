<template>
  <section class="teacher-page">
    <article class="panel header-panel">
      <h2>学生账号管理</h2>
      <p class="header-desc">支持筛选、启停用、重置密码与导出账号清单。</p>
      <p class="header-hint">建议先导入学生名单，再进行筛选和批量操作。</p>
      <div class="toolbar">
        <RouterLink class="btn back-nav" to="/teacher/courses">返回课程看板</RouterLink>
        <RouterLink class="btn import-nav" to="/teacher/student-import">添加/导入学生</RouterLink>
      </div>
    </article>

    <article v-if="isRoleChecking" class="panel">正在验证教师权限...</article>
    <article v-else-if="roleError" class="panel error">{{ roleError }}</article>
    <article v-else-if="!isTeacher" class="panel error">仅教师可访问当前页面</article>

    <StudentManagePanel v-else :api="studentApi" />
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getCurrentUserProfile } from "../api/auth";
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

const isRoleChecking = ref(false);
const roleError = ref("");
const isTeacher = ref(false);

const studentApi = {
  list: getTeacherStudents,
  classOptions: getTeacherStudentClassOptions,
  export: exportTeacherStudents,
  enable: enableTeacherStudent,
  disable: disableTeacherStudent,
  resetPassword: resetTeacherStudentPassword,
  batchEnable: batchEnableTeacherStudents,
  batchDisable: batchDisableTeacherStudents,
  batchResetPassword: batchResetTeacherStudentPasswords,
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
