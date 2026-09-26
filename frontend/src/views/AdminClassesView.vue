<template>
  <section class="page">
    <article class="panel hero">
      <div>
        <h2>班级管理</h2>
        <p>维护通用班级，学生导入后的班级名称会自动同步为班级记录。</p>
      </div>
    </article>
    <article class="panel form-panel">
      <input v-model.trim="form.name" placeholder="班级名称" />
      <input v-model.trim="form.grade" placeholder="年级 / 学期" />
      <input v-model.trim="form.description" placeholder="说明" />
      <button class="btn primary" type="button" @click="createClass">新建班级</button>
    </article>
    <article v-if="message" :class="['panel', messageType]">{{ message }}</article>
    <article v-if="isLoading" class="panel">正在加载班级...</article>
    <div class="list">
      <article v-for="item in classes" :key="item.id" class="panel class-row">
        <div>
          <h3>{{ item.name }}</h3>
          <p>{{ item.description || item.grade || "暂无说明" }}</p>
        </div>
        <div class="meta">
          <span class="meta-pill members">{{ item.member_count }} 名成员</span>
          <span class="meta-pill courses">{{ item.course_count }} 门课程</span>
          <span :class="['meta-pill', item.is_active ? 'active' : 'inactive']">{{ item.is_active ? "启用" : "停用" }}</span>
          <RouterLink class="btn manage-link" :to="`/admin/classes/${item.id}/students`">学生管理</RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

import { createAdminClass, getAdminClasses } from "../api/admin-course";

const classes = ref([]);
const isLoading = ref(false);
const message = ref("");
const messageType = ref("success");
const form = reactive({ name: "", grade: "", description: "" });

async function loadClasses() {
  isLoading.value = true;
  try {
    const data = await getAdminClasses({ page: 1, page_size: 100 });
    classes.value = data.items || [];
  } catch (error) {
    message.value = `班级加载失败：${error.message}`;
    messageType.value = "error";
  } finally {
    isLoading.value = false;
  }
}

async function createClass() {
  message.value = "";
  if (!form.name) {
    message.value = "班级名称必填";
    messageType.value = "error";
    return;
  }
  try {
    await createAdminClass({ ...form, is_active: true });
    form.name = "";
    form.grade = "";
    form.description = "";
    message.value = "班级已创建";
    messageType.value = "success";
    await loadClasses();
  } catch (error) {
    message.value = `创建失败：${error.message}`;
    messageType.value = "error";
  }
}

onMounted(loadClasses);
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
.form-panel,
.class-row,
.meta {
  display: flex;
  gap: 10px;
}
.class-row {
  justify-content: space-between;
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
input {
  flex: 1;
  min-width: 0;
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
}
.meta {
  flex-wrap: wrap;
  align-content: center;
  align-items: center;
  justify-content: flex-end;
}
.meta-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 78px;
  min-height: 38px;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 700;
  line-height: 1;
  text-align: center;
  white-space: nowrap;
}
.meta-pill.members {
  background: var(--brand-soft);
  color: var(--brand-700);
}
.meta-pill.courses {
  background: var(--accent-cyan-soft);
  color: var(--accent-cyan-strong);
}
.meta-pill.active {
  background: var(--success-soft);
  color: var(--success-strong);
}
.meta-pill.inactive {
  background: var(--danger-soft);
  color: var(--danger-strong);
}
.btn {
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}
.manage-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  text-decoration: none;
  background: var(--brand-600);
  color: var(--surface-1);
}
.primary {
  background: var(--brand-600);
  color: var(--surface-1);
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
  .form-panel,
  .class-row {
    flex-direction: column;
  }
}
</style>
