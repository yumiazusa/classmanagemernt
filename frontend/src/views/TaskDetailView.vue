<template>
  <section class="page">
    <article v-if="task" class="panel">
      <RouterLink class="back-link" :to="`/courses/${task.course_id}/experience`">返回课程</RouterLink>
      <div class="task-head">
        <div>
          <h2>{{ task.title }}</h2>
          <p>{{ task.summary || "完成任务后提交你的学习成果。" }}</p>
        </div>
        <span>{{ taskTypeLabels[task.task_type] || task.task_type }}</span>
      </div>
      <div class="instruction">{{ task.instruction_content || "暂无详细说明。" }}</div>
      <a v-if="task.external_url" class="external-link" :href="task.external_url" target="_blank" rel="noreferrer">打开外部链接</a>
    </article>

    <article v-if="isLoading" class="panel">正在加载任务...</article>
    <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>

    <article v-if="task" class="panel submit-panel">
      <h3>提交入口</h3>
      <label class="field">
        <span>文本内容</span>
        <textarea v-model="form.content" rows="7" placeholder="输入你的回答、学习记录或说明"></textarea>
      </label>
      <label class="field">
        <span>附件或外部成果链接</span>
        <input v-model.trim="form.attachment_url" type="url" placeholder="https://..." />
      </label>
      <div class="actions">
        <button type="button" class="btn plain" :disabled="isSubmitting" @click="submit('draft')">保存草稿</button>
        <button type="button" class="btn primary" :disabled="isSubmitting" @click="submit('submitted')">
          {{ isSubmitting ? "提交中..." : "提交任务" }}
        </button>
      </div>
      <p v-if="actionMessage" :class="['message', actionError ? 'bad' : 'good']">{{ actionMessage }}</p>
    </article>
  </section>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";

import { getTaskById, submitTask } from "../api/course";
import { platformConfig } from "../config/platform";

const route = useRoute();
const task = ref(null);
const isLoading = ref(false);
const isSubmitting = ref(false);
const errorMessage = ref("");
const actionMessage = ref("");
const actionError = ref(false);
const { taskTypeLabels } = platformConfig;
const form = reactive({ content: "", attachment_url: "" });

async function loadTask() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    task.value = await getTaskById(route.params.id);
  } catch (error) {
    errorMessage.value = `任务加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

async function submit(status) {
  actionMessage.value = "";
  actionError.value = false;
  if (!form.content.trim() && !form.attachment_url.trim()) {
    actionMessage.value = "请填写文本内容或成果链接";
    actionError.value = true;
    return;
  }
  isSubmitting.value = true;
  try {
    await submitTask(task.value.id, {
      content: form.content.trim() || null,
      attachment_url: form.attachment_url.trim() || null,
      status,
    });
    actionMessage.value = status === "draft" ? "草稿已保存" : "任务已提交";
    await loadTask();
  } catch (error) {
    actionMessage.value = `提交失败：${error.message}`;
    actionError.value = true;
  } finally {
    isSubmitting.value = false;
  }
}

onMounted(loadTask);
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
.task-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}
h2,
h3 {
  margin: 0;
}
p {
  margin: 8px 0 0;
  color: var(--text-muted);
}
.back-link,
.external-link {
  display: inline-flex;
  margin-bottom: 12px;
  color: var(--brand-700);
  text-decoration: none;
  font-weight: 700;
}
.task-head span {
  border-radius: 999px;
  padding: 5px 10px;
  background: var(--brand-soft);
  color: var(--brand-700);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
  align-self: flex-start;
}
.instruction {
  margin-top: 16px;
  color: var(--text-body);
  line-height: 1.7;
  white-space: pre-wrap;
}
.field {
  display: grid;
  gap: 8px;
  margin-top: 14px;
}
.field span {
  font-weight: 700;
  color: var(--text-strong);
}
textarea,
input {
  width: 100%;
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 14px;
}
.btn {
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}
.primary {
  background: var(--brand-600);
  color: var(--surface-1);
}
.plain {
  background: var(--surface-2);
  color: var(--text-strong);
}
.message.good {
  color: var(--success-strong);
}
.message.bad,
.error {
  color: var(--danger-strong);
}
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
}
@media (max-width: 680px) {
  .task-head,
  .actions {
    flex-direction: column;
  }
}
</style>
