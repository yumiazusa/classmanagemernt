<template>
  <section class="page">
    <header class="page-head">
      <h2>课程管理</h2>
      <p>维护课程名称、授课范围与课程模块连接。</p>
    </header>

    <form class="create-row" @submit.prevent="createCourse">
      <label class="field grow"><span>课程名称</span><input v-model.trim="form.title" placeholder="输入课程名称" required /></label>
      <label class="field module-field"><span>连接模块</span>
        <select v-model="form.experience_key">
          <option value="unlinked">暂不连接</option>
          <option v-for="item in experiences" :key="item.key" :value="item.key">{{ item.label }}</option>
        </select>
      </label>
      <button class="btn primary" :disabled="saving">{{ saving ? "创建中..." : "新建课程" }}</button>
    </form>
    <p v-if="!experiences.length" class="hint">当前没有已接入的课程模块。可先建立课程，连接模块后再启用。</p>

    <p v-if="message" :class="['notice', messageType]" role="status">{{ message }}</p>
    <p v-if="loading" class="notice">正在加载课程...</p>
    <p v-else-if="!courses.length" class="notice">暂无课程</p>
    <div v-else class="list">
      <article v-for="course in courses" :key="course.id" class="course-row">
        <div class="course-info">
          <h3>{{ course.title }}</h3>
          <div class="meta">
            <span :class="['state', course.experience_key === 'unlinked' ? 'pending' : course.is_active ? 'on' : 'off']">
              {{ course.experience_key === 'unlinked' ? '未连接模块' : course.is_active ? '已启用' : '已停用' }}
            </span>
            <span>{{ experienceLabel(course.experience_key) }}</span>
            <span>{{ course.teacher_count }} 位教师</span>
            <span>{{ course.class_count }} 个班级</span>
          </div>
        </div>
        <div class="actions">
          <RouterLink class="btn secondary" :to="`/admin/courses/${course.id}`">配置课程</RouterLink>
          <button v-if="course.is_active" class="btn danger" :disabled="saving" @click="setActive(course, false)">停用</button>
          <button v-else class="btn primary" :disabled="saving || course.experience_key === 'unlinked'" :title="course.experience_key === 'unlinked' ? '请先连接课程模块' : ''" @click="setActive(course, true)">启用</button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { createAdminCourse, getAdminCourseExperiences, getAdminCourses, updateAdminCourse } from "../api/admin-course";

const router = useRouter();
const courses = ref([]);
const experiences = ref([]);
const loading = ref(false);
const saving = ref(false);
const message = ref("");
const messageType = ref("success");
const form = reactive({ title: "", experience_key: "unlinked" });

function experienceLabel(key) {
  return experiences.value.find(item => item.key === key)?.label || "课程模块待连接";
}

async function loadCourses() {
  loading.value = true;
  try {
    const result = await getAdminCourses({ page: 1, page_size: 100 });
    courses.value = result.items || [];
  } catch (error) {
    message.value = `课程加载失败：${error.message}`;
    messageType.value = "error";
  } finally {
    loading.value = false;
  }
}

async function createCourse() {
  if (!form.title) return;
  saving.value = true;
  message.value = "";
  try {
    const course = await createAdminCourse({ ...form });
    await router.push(`/admin/courses/${course.id}`);
  } catch (error) {
    message.value = `创建失败：${error.message}`;
    messageType.value = "error";
  } finally {
    saving.value = false;
  }
}

async function setActive(course, isActive) {
  saving.value = true;
  message.value = "";
  try {
    await updateAdminCourse(course.id, { is_active: isActive });
    await loadCourses();
    message.value = isActive ? "课程已启用" : "课程已停用";
    messageType.value = "success";
  } catch (error) {
    message.value = `操作失败：${error.message}`;
    messageType.value = "error";
  } finally {
    saving.value = false;
  }
}

onMounted(async () => {
  try {
    experiences.value = await getAdminCourseExperiences();
  } catch (error) {
    message.value = `课程模块加载失败：${error.message}`;
    messageType.value = "error";
  }
  await loadCourses();
});
</script>

<style scoped>
.page, .list { display: grid; gap: 14px; }
.page-head { padding: 6px 0 2px; }
h2, h3 { margin: 0; }
.page-head p { color: var(--text-muted); margin: 8px 0 0; }
.create-row, .course-row { background: var(--surface-1); border: 1px solid var(--border-soft); border-radius: 8px; padding: 18px 20px; display: flex; gap: 14px; align-items: end; }
.field { display: grid; gap: 7px; font-size: 14px; font-weight: 600; color: var(--text-muted); min-width: 0; }
.grow { flex: 1 1 280px; }
.module-field { flex: 0 1 240px; }
input, select { width: 100%; box-sizing: border-box; border: 1px solid var(--border-soft); border-radius: 8px; background: var(--surface-1); color: var(--text-strong); min-height: 42px; padding: 8px 12px; font: inherit; }
.course-row { align-items: center; justify-content: space-between; }
.course-info { min-width: 0; }
.meta { display: flex; flex-wrap: wrap; gap: 9px 16px; margin-top: 10px; color: var(--text-muted); font-size: 14px; }
.state { font-weight: 700; }
.on { color: var(--success-strong); }
.off { color: var(--danger-strong); }
.pending { color: var(--brand-700); }
.actions { display: flex; gap: 8px; flex: 0 0 auto; }
.btn { display: inline-flex; align-items: center; justify-content: center; min-height: 42px; border: 0; border-radius: 8px; padding: 8px 14px; font: inherit; font-weight: 700; text-decoration: none; cursor: pointer; white-space: nowrap; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.primary { background: var(--brand-600); color: var(--surface-1); }
.secondary { background: var(--neutral-btn); color: var(--text-strong); }
.danger { background: var(--danger-soft); color: var(--danger-strong); }
.hint { margin: 0; color: var(--text-muted); font-size: 14px; }
.notice { margin: 0; padding: 14px 18px; background: var(--surface-1); border: 1px solid var(--border-soft); border-radius: 8px; }
.notice.success { color: var(--success-strong); }
.notice.error { background: var(--danger-soft); color: var(--danger-strong); }
@media (max-width: 780px) { .create-row, .course-row { flex-wrap: wrap; align-items: stretch; } .module-field { flex: 1 1 180px; } .actions { width: 100%; } }
</style>
