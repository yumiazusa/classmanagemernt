<template>
  <section class="admin-page">
    <article class="panel head-panel">
      <h2>管理后台首页</h2>
      <p>查看系统核心统计概览（近7天统计已包含在卡片中）。</p>
    </article>

    <article v-if="isLoading" class="panel">正在加载管理员概览...</article>
    <article v-else-if="errorMessage" class="panel error">{{ errorMessage }}</article>

    <template v-else-if="overview">
      <article class="panel cards-panel">
        <div class="cards-grid">
          <div class="stat-card">
            <span>总用户数</span>
            <strong>{{ overview.total_users }}</strong>
          </div>
          <div class="stat-card">
            <span>学生数</span>
            <strong>{{ overview.student_count }}</strong>
          </div>
          <div class="stat-card">
            <span>教师数</span>
            <strong>{{ overview.teacher_count }}</strong>
          </div>
          <div class="stat-card">
            <span>管理员数</span>
            <strong>{{ overview.admin_count }}</strong>
          </div>
          <div class="stat-card">
            <span>课程总数</span>
            <strong>{{ overview.course_count ?? overview.experiment_count }}</strong>
          </div>
          <div class="stat-card good">
            <span>启用账号数</span>
            <strong>{{ overview.enabled_user_count }}</strong>
          </div>
          <div class="stat-card warn">
            <span>停用账号数</span>
            <strong>{{ overview.disabled_user_count }}</strong>
          </div>
          <div class="stat-card soft">
            <span>近7天新增用户</span>
            <strong>{{ overview.recent_created_users_count }}</strong>
          </div>
          <div class="stat-card soft">
            <span>近7天任务提交</span>
            <strong>{{ overview.recent_submission_count }}</strong>
          </div>
        </div>
      </article>
    </template>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";

import { getAdminOverview } from "../api/admin";

const isLoading = ref(false);
const errorMessage = ref("");
const overview = ref(null);

async function loadOverview() {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    overview.value = await getAdminOverview();
  } catch (error) {
    errorMessage.value = error.message || "管理员概览加载失败";
  } finally {
    isLoading.value = false;
  }
}

onMounted(async () => {
  await loadOverview();
});
</script>

<style scoped>
.admin-page {
  display: grid;
  gap: 14px;
}

.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}

.head-panel h2 {
  margin: 0;
}

.head-panel p {
  margin: 8px 0 0;
  color: var(--text-muted);
}

.error {
  border-color: var(--danger-border);
  background: var(--danger-soft);
  color: var(--danger-strong);
}

.cards-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.stat-card {
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 12px;
  display: grid;
  gap: 6px;
}

.stat-card span {
  color: var(--text-subtle);
  font-size: 14px;
}

.stat-card strong {
  color: var(--text-strong);
  font-size: 26px;
  line-height: 1;
}

.stat-card.good {
  border-color: var(--success-border);
  background: var(--success-soft);
}

.stat-card.warn {
  border-color: var(--warn-border);
  background: var(--warn-soft);
}

.stat-card.soft {
  border-color: var(--brand-soft-2);
  background: var(--brand-soft);
}

@media (max-width: 920px) {
  .cards-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
