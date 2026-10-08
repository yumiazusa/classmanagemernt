<template>
  <section class="workspace">
    <header class="page-head">
      <div>
        <RouterLink class="back-link" :to="`/admin/courses/${courseId}`">返回课程编辑</RouterLink>
        <h2>{{ courseTitle }} · 课程文档</h2>
      </div>
    </header>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <CourseDocsPanel :course-id="courseId" />
  </section>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import CourseDocsPanel from "../components/CourseDocsPanel.vue";
import { getAdminCourseWorkspace } from "../api/admin-course";

const route = useRoute();
const courseId = computed(() => Number(route.params.id));
const courseTitle = ref("课程");
const error = ref("");
watch(courseId, async () => {
  error.value = "";
  try { courseTitle.value = (await getAdminCourseWorkspace(courseId.value)).course.title; }
  catch (cause) { error.value = `课程信息加载失败：${cause.message}`; }
}, { immediate: true });
</script>

<style scoped>
.workspace { display: grid; gap: 18px; }
.page-head { padding: 5px 0 16px; border-bottom: 1px solid var(--border-soft); }
.back-link { color: var(--brand-700); font-size: 14px; font-weight: 700; text-decoration: none; }
h2 { font-size: 26px; margin: 12px 0 0; }
.notice { margin: 0; padding: 14px 18px; border-radius: 8px; }
.error { color: var(--danger-strong); background: var(--danger-soft); }
</style>
