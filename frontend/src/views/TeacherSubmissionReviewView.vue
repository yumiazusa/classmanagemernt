<template>
  <section class="page">
    <article class="panel hero">
      <div>
        <h2>提交批阅</h2>
        <p>输入任务 ID 查看学生提交，完成评分与反馈。</p>
      </div>
      <div class="lookup">
        <input v-model.trim="taskId" type="number" min="1" placeholder="任务 ID" />
        <button class="btn primary" type="button" @click="loadSubmissions">查询</button>
      </div>
    </article>

    <article v-if="errorMessage" class="panel error">{{ errorMessage }}</article>
    <article v-if="isLoading" class="panel">正在加载提交...</article>
    <article v-else-if="hasLoaded && submissions.length === 0" class="panel">当前任务暂无提交</article>

    <div v-else class="list">
      <article v-for="item in submissions" :key="item.id" class="panel item">
        <div class="item-head">
          <div>
            <h3>{{ item.full_name || item.username }}</h3>
            <p>{{ item.course_title }} / {{ item.task_title }} · 第 {{ item.version }} 版</p>
          </div>
          <span>{{ reviewLabel(item.review_status) }}</span>
        </div>
        <div class="content">{{ item.content || item.attachment_url || "无提交内容" }}</div>
        <div class="review-row">
          <select v-model="item._review_status">
            <option value="pending">待批阅</option>
            <option value="reviewed">已批阅</option>
            <option value="returned">已退回</option>
            <option value="passed">通过</option>
            <option value="failed">未通过</option>
          </select>
          <input v-model.number="item._score" type="number" min="0" placeholder="分数" />
          <input v-model.trim="item._comment" type="text" placeholder="反馈意见" />
          <button class="btn primary" type="button" @click="saveReview(item)">保存</button>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
import { ref } from "vue";

import { getTeacherTaskSubmissions, reviewTeacherSubmission } from "../api/teacher-course";

const taskId = ref("");
const submissions = ref([]);
const isLoading = ref(false);
const hasLoaded = ref(false);
const errorMessage = ref("");

function reviewLabel(status) {
  return { pending: "待批阅", reviewed: "已批阅", returned: "已退回", passed: "通过", failed: "未通过" }[status] || status;
}

async function loadSubmissions() {
  errorMessage.value = "";
  if (!taskId.value) {
    errorMessage.value = "请输入任务 ID";
    return;
  }
  isLoading.value = true;
  try {
    const data = await getTeacherTaskSubmissions(taskId.value);
    submissions.value = data.map((item) => ({
      ...item,
      _review_status: item.review_status || "pending",
      _score: item.score,
      _comment: item.review_comment || "",
    }));
    hasLoaded.value = true;
  } catch (error) {
    errorMessage.value = `提交加载失败：${error.message}`;
  } finally {
    isLoading.value = false;
  }
}

async function saveReview(item) {
  errorMessage.value = "";
  try {
    await reviewTeacherSubmission(item.id, {
      review_status: item._review_status,
      score: item._score || null,
      review_comment: item._comment || null,
    });
    await loadSubmissions();
  } catch (error) {
    errorMessage.value = `保存批阅失败：${error.message}`;
  }
}
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
.hero,
.item-head,
.review-row {
  display: flex;
  gap: 12px;
  justify-content: space-between;
}
h2,
h3 {
  margin: 0;
}
p {
  margin: 8px 0 0;
  color: var(--text-muted);
}
.lookup,
.review-row {
  display: flex;
  gap: 10px;
}
input,
select {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
}
.item-head span {
  border-radius: 999px;
  background: var(--brand-soft);
  color: var(--brand-700);
  padding: 5px 10px;
  font-size: 13px;
  font-weight: 700;
  align-self: flex-start;
}
.content {
  white-space: pre-wrap;
  line-height: 1.65;
  color: var(--text-body);
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
.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}
@media (max-width: 760px) {
  .hero,
  .item-head,
  .review-row,
  .lookup {
    flex-direction: column;
  }
}
</style>
