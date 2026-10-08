<template>
  <section v-if="loading" class="state">正在加载课程...</section>
  <section v-else-if="error" class="state error">{{ error }}</section>
  <section v-else-if="extension" class="course-experience">
    <RouterLink class="docs-link" :to="`/courses/${course.id}/docs`">查看课程文档</RouterLink>
    <component :is="extension.component" :course="course" />
  </section>
  <section v-else class="state error">该课程模块尚未安装，请联系管理员。</section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { getCourseById } from "../api/course";
import { courseExperiences } from "../course-experiences/registry";

const route = useRoute();
const course = ref(null);
const loading = ref(false);
const error = ref("");
const extension = computed(() => courseExperiences[course.value?.experience_key] || null);

watch(() => route.params.id, async (id) => {
  loading.value = true;
  error.value = "";
  course.value = null;
  try {
    course.value = await getCourseById(id);
  } catch (cause) {
    error.value = `课程加载失败：${cause.message}`;
  } finally {
    loading.value = false;
  }
}, { immediate: true });
</script>

<style scoped>
.course-experience { display: grid; gap: 14px; }
.docs-link { justify-self: end; color: var(--brand-700); font-weight: 700; text-decoration: none; }
.state { padding: 24px; background: var(--surface-1); border: 1px solid var(--border-soft); border-radius: 8px; }
.error { color: var(--danger-strong); background: var(--danger-soft); }
</style>
