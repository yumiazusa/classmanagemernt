<template>
  <section class="workspace">
    <header class="page-head">
      <div>
        <RouterLink class="back-link" to="/admin/courses">返回课程管理</RouterLink>
        <h2>{{ workspace?.course.title || "课程配置" }}</h2>
      </div>
      <RouterLink v-if="workspace && moduleIsInstalled && workspace.course.is_active" class="btn secondary" :to="`/courses/${courseId}/experience`">进入课程模块</RouterLink>
    </header>

    <p v-if="loading" class="notice">正在加载课程...</p>
    <p v-if="error" class="notice error" role="alert">{{ error }}</p>
    <p v-if="message" class="notice success" role="status">{{ message }}</p>

    <form v-if="workspace" class="settings" @submit.prevent="saveCourse">
      <section class="section">
        <h3>课程信息</h3>
        <div class="form-grid">
          <label class="field"><span>课程名称</span><input v-model.trim="form.title" required maxlength="200" /></label>
          <label class="field"><span>课程模块</span>
            <select v-model="form.experience_key">
              <option value="unlinked">暂不连接</option>
              <option v-for="item in experiences" :key="item.key" :value="item.key">{{ item.label }}</option>
            </select>
          </label>
        </div>
        <p v-if="!experiences.length" class="hint">尚无已接入模块。课程可先保存，接入模块后再启用。</p>
        <label class="switch-row"><input v-model="form.is_active" type="checkbox" :disabled="!moduleIsInstalled" /><span>启用课程</span></label>
      </section>

      <section class="section">
        <div class="section-head"><h3>授课范围</h3><span>{{ form.teacher_ids.length }} 位教师 · {{ form.class_group_ids.length }} 个班级</span></div>
        <div class="choice-grid">
          <fieldset><legend>授课教师</legend><label v-for="teacher in teachers" :key="teacher.user_id" class="choice"><input v-model="form.teacher_ids" type="checkbox" :value="teacher.user_id" />{{ teacher.full_name || teacher.username }}</label><p v-if="!teachers.length" class="hint">暂无教师账号</p></fieldset>
          <fieldset><legend>授课班级</legend><label v-for="group in classes" :key="group.id" class="choice"><input v-model="form.class_group_ids" type="checkbox" :value="group.id" />{{ group.name }}</label><p v-if="!classes.length" class="hint">暂无班级</p></fieldset>
        </div>
      </section>

      <div class="footer">
        <button class="btn primary" type="submit" :disabled="saving">{{ saving ? "保存中..." : "保存配置" }}</button>
        <RouterLink class="btn secondary" :to="`/admin/courses/${courseId}/docs`">编辑课程文档</RouterLink>
        <RouterLink class="btn secondary" to="/admin/courses">返回课程管理</RouterLink>
      </div>
    </form>
  </section>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { getAdminUsers } from "../api/admin";
import { getAdminClasses, getAdminCourseExperiences, getAdminCourseWorkspace, updateAdminCourse } from "../api/admin-course";

const route = useRoute();
const courseId = computed(() => Number(route.params.id));
const workspace = ref(null);
const experiences = ref([]);
const teachers = ref([]);
const classes = ref([]);
const loading = ref(false);
const saving = ref(false);
const error = ref("");
const message = ref("");
const form = reactive({ title: "", experience_key: "unlinked", is_active: false, teacher_ids: [], class_group_ids: [] });
const moduleIsInstalled = computed(() => experiences.value.some(item => item.key === form.experience_key));

async function getAllOptions(fetchPage) {
  const items = [];
  let page = 1;
  let totalPages = 1;
  while (page <= totalPages) {
    const result = await fetchPage({ page, page_size: 100 });
    items.push(...(result.items || []));
    totalPages = result.total_pages || 0;
    page += 1;
  }
  return items;
}

async function loadWorkspace() {
  const data = await getAdminCourseWorkspace(courseId.value);
  workspace.value = data;
  Object.assign(form, {
    title: data.course.title,
    experience_key: data.course.experience_key,
    is_active: data.course.is_active && data.course.experience_key !== "unlinked",
    teacher_ids: data.teacher_ids,
    class_group_ids: data.class_group_ids,
  });
}

watch(courseId, async () => {
  loading.value = true;
  error.value = "";
  workspace.value = null;
  try {
    const [moduleOptions, teacherItems, classItems] = await Promise.all([
      getAdminCourseExperiences(),
      getAllOptions(params => getAdminUsers({ ...params, role: "teacher" })),
      getAllOptions(getAdminClasses),
    ]);
    experiences.value = moduleOptions;
    teachers.value = teacherItems;
    classes.value = classItems;
    await loadWorkspace();
  } catch (cause) {
    error.value = `课程配置加载失败：${cause.message}`;
  } finally {
    loading.value = false;
  }
}, { immediate: true });

async function saveCourse() {
  if (!form.title) { error.value = "课程名称不能为空"; return; }
  saving.value = true;
  error.value = "";
  message.value = "";
  try {
    await updateAdminCourse(courseId.value, { ...form, is_active: moduleIsInstalled.value && form.is_active });
    await loadWorkspace();
    message.value = "课程配置已保存";
  } catch (cause) {
    error.value = `保存失败：${cause.message}`;
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.workspace { display: grid; gap: 18px; }
.settings { display: grid; gap: 18px; }
.page-head { display: flex; align-items: end; justify-content: space-between; gap: 18px; padding: 5px 0 16px; border-bottom: 1px solid var(--border-soft); }
.back-link { color: var(--brand-700); font-size: 14px; font-weight: 700; text-decoration: none; }
h2 { font-size: 26px; margin: 12px 0 0; }
h3 { margin: 0; font-size: 18px; }
.section { background: var(--surface-1); border: 1px solid var(--border-soft); border-radius: 8px; padding: 20px 24px; display: grid; gap: 18px; }
.section-head { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; }
.section-head span, .hint { color: var(--text-muted); font-size: 14px; }
.form-grid, .choice-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.field { display: grid; gap: 7px; color: var(--text-muted); font-size: 14px; font-weight: 600; }
.field input, .field select { min-width: 0; width: 100%; box-sizing: border-box; min-height: 42px; border: 1px solid var(--border-soft); background: var(--surface-1); color: var(--text-strong); border-radius: 8px; padding: 8px 12px; font: inherit; }
.switch-row, .choice { display: flex; align-items: center; gap: 9px; }
.switch-row { font-weight: 700; }
.switch-row input, .choice input { width: 17px; height: 17px; accent-color: var(--brand-600); }
fieldset { min-width: 0; border: 1px solid var(--border-soft); border-radius: 8px; padding: 12px 16px; }
legend { padding: 0 6px; font-weight: 700; }
.choice { padding: 5px 0; }
.hint { margin: 0; }
.footer { display: flex; justify-content: flex-end; gap: 14px; margin-top: 6px; }
.btn { display: inline-flex; align-items: center; justify-content: center; min-height: 42px; border: 0; border-radius: 8px; padding: 8px 16px; font: inherit; font-weight: 700; text-decoration: none; cursor: pointer; }
.btn:disabled { opacity: .55; cursor: not-allowed; }
.primary { background: var(--brand-600); color: var(--surface-1); }
.secondary { background: var(--surface-1); border: 1px solid var(--brand-600); color: var(--brand-700); }
.notice { margin: 0; padding: 14px 18px; border-radius: 8px; background: var(--surface-1); }
.error { color: var(--danger-strong); background: var(--danger-soft); }
.success { color: var(--success-strong); background: var(--success-soft); }
@media (max-width: 700px) { .page-head { align-items: start; flex-direction: column; } .form-grid, .choice-grid { grid-template-columns: 1fr; } .section { padding: 16px; } }
</style>
