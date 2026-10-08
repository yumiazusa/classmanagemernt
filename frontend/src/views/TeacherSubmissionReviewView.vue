<template>
  <section class="page">
    <article class="panel">
      <span class="eyebrow">提交批阅</span>
      <h2>正在开发中</h2>
      <p>提交批阅功能正在准备，完成后会在这里开放。</p>
      <RouterLink class="back-link" to="/teacher/courses">返回课程管理</RouterLink>
    </article>
  </section>
</template>

<style scoped>
.page { min-height: 55vh; display: grid; place-items: center; }
.panel { width: min(100%, 520px); padding: 48px 32px; text-align: center; background: var(--surface-1); border: 1px solid var(--border-soft); border-radius: 12px; }
.eyebrow { color: var(--brand-700); font-size: 14px; font-weight: 700; }
h2 { margin: 12px 0; color: var(--text-strong); }
p { margin: 0; color: var(--text-muted); line-height: 1.7; }
.back-link { display: inline-block; margin-top: 24px; padding: 10px 16px; border-radius: 10px; background: var(--brand-soft); color: var(--brand-700); font-weight: 700; text-decoration: none; }
</style>
