<template>
  <section class="page">
    <article v-if="course" class="panel hero">
      <div>
        <RouterLink class="back-link" to="/courses">返回我的课程</RouterLink>
        <h2>{{ course.title }}</h2>
        <p>{{ course.description || course.summary || "暂无课程说明" }}</p>
      </div>
      <span class="hero-badge">{{ course.task_count }} 个任务</span>
    </article>
    <article v-if="isLoading" class="panel">正在加载课程详情...</article>
    <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>

    <div v-else class="module-list">
      <article v-for="module in modulesWithTasks" :key="module.id" class="panel module-card">
        <div class="module-head">
          <div>
            <h3>{{ module.title }}</h3>
            <p>{{ module.summary || "暂无模块说明" }}</p>
          </div>
          <span>{{ module.tasks.length }} 个任务</span>
        </div>
        <div class="task-list">
          <RouterLink v-for="task in module.tasks" :key="task.id" class="task-row" :to="`/tasks/${task.id}`">
            <div>
              <h4>{{ task.title }}</h4>
              <p>{{ task.summary || "查看任务说明并提交学习成果" }}</p>
            </div>
            <span>{{ taskTypeLabels[task.task_type] || task.task_type }}</span>
          </RouterLink>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { getCourseById, getCourseModules, getCourseTasks } from "../api/course";
import { platformConfig } from "../config/platform";

const route = useRoute();
const course = ref(null);
const modules = ref([]);
const tasks = ref([]);
const isLoading = ref(false);
const errorMessage = ref("");
const { taskTypeLabels } = platformConfig;

const modulesWithTasks = computed(() => {
  const groups = modules.value.map((module) => ({
    ...module,
    tasks: tasks.value.filter((task) => task.module_id === module.id),
  }));
  const looseTasks = tasks.value.filter((task) => !task.module_id);
  if (looseTasks.length > 0) {
    groups.push({ id: "loose", title: "未分组任务", summary: "", tasks: looseTasks });
  }
  return groups;
});

async function loadDetail() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const courseId = route.params.id;
    const [courseData, moduleData, taskData] = await Promise.all([
      getCourseById(courseId),
      getCourseModules(courseId),
      getCourseTasks(courseId),
    ]);
    course.value = courseData;
    modules.value = moduleData;
    tasks.value = taskData;
  } catch (error) {
    errorMessage.value = `课程详情加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

onMounted(loadDetail);
</script>

<style scoped>
.page,
.module-list,
.task-list {
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
.module-head,
.task-row {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}
h2,
h3,
h4 {
  margin: 0;
}
p {
  margin: 8px 0 0;
  color: var(--text-muted);
}
.back-link {
  display: inline-flex;
  margin-bottom: 10px;
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 700;
}
.hero-badge,
.module-head span,
.task-row span {
  align-self: flex-start;
  border-radius: 999px;
  padding: 5px 10px;
  background: var(--brand-soft);
  color: var(--brand-700);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}
.task-row {
  align-items: center;
  color: inherit;
  text-decoration: none;
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 14px;
}
.task-row:hover {
  border-color: var(--brand-300);
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
@media (max-width: 680px) {
  .hero,
  .module-head,
  .task-row {
    flex-direction: column;
  }
}
</style>
