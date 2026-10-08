<template>
  <div class="layout">
    <header class="header">
      <div class="header-brand">
        <h1>{{ platformName }}</h1>
        <button v-if="!isLoginPage" type="button" class="mobile-menu-btn" @click.stop="toggleMobileNav">
          {{ mobileNavOpen ? "关闭" : "菜单" }}
        </button>
      </div>
      <div v-if="!isLoginPage" ref="navRef" :class="['header-right', mobileNavOpen ? 'open' : '']">
        <nav class="nav">
          <template v-if="isAdmin">
            <div class="admin-nav-group">
              <RouterLink class="nav-rect-btn" to="/admin" @click="handleNavLinkClick">后台首页</RouterLink>

              <div class="nav-dropdown">
                <button
                  type="button"
                  :class="['nav-drop-trigger', openMenu === 'users' || usersGroupActive ? 'active' : '']"
                  @click.stop="toggleMenu('users')"
                >
                  用户管理
                  <span :class="['caret', openMenu === 'users' ? 'open' : '']">▾</span>
                </button>
                <div v-if="openMenu === 'users'" class="dropdown-menu">
                  <RouterLink to="/admin/users" @click="handleNavLinkClick">全部用户</RouterLink>
                  <RouterLink to="/admin/teachers" @click="handleNavLinkClick">教师管理</RouterLink>
                  <RouterLink to="/admin/admin-users" @click="handleNavLinkClick">管理员管理</RouterLink>
                </div>
              </div>

              <div class="nav-dropdown">
                <button
                  type="button"
                  :class="['nav-drop-trigger', openMenu === 'courses' || coursesGroupActive ? 'active' : '']"
                  @click.stop="toggleMenu('courses')"
                >
                  教学管理
                  <span :class="['caret', openMenu === 'courses' ? 'open' : '']">▾</span>
                </button>
                <div v-if="openMenu === 'courses'" class="dropdown-menu">
                  <RouterLink to="/admin/classes" @click="handleNavLinkClick">班级管理</RouterLink>
                  <RouterLink to="/admin/courses" @click="handleNavLinkClick">课程管理</RouterLink>
                </div>
              </div>

              <div class="nav-dropdown">
                <button
                  type="button"
                  :class="['nav-drop-trigger', openMenu === 'docs' || docsGroupActive ? 'active' : '']"
                  @click.stop="toggleMenu('docs')"
                >
                  文档管理
                  <span :class="['caret', openMenu === 'docs' ? 'open' : '']">▾</span>
                </button>
                <div v-if="openMenu === 'docs'" class="dropdown-menu">
                  <RouterLink to="/admin/docs" @click="handleNavLinkClick">文档管理</RouterLink>
                  <RouterLink to="/docs" @click="handleNavLinkClick">文档浏览</RouterLink>
                </div>
              </div>
            </div>
          </template>

          <template v-else-if="isStudent">
            <RouterLink class="nav-rect-btn" to="/dashboard" @click="handleNavLinkClick">个人主页</RouterLink>
            <RouterLink class="nav-rect-btn" to="/courses" @click="handleNavLinkClick">我的课程</RouterLink>
            <RouterLink class="nav-rect-btn" to="/docs" @click="handleNavLinkClick">文档浏览</RouterLink>
          </template>

          <template v-if="isTeacher">
            <div class="nav-dropdown">
              <button
                type="button"
                :class="['nav-drop-trigger', openMenu === 'teacherCourses' || teacherCoursesGroupActive ? 'active' : '']"
                @click.stop="toggleMenu('teacherCourses')"
              >
                课程管理
                <span :class="['caret', openMenu === 'teacherCourses' ? 'open' : '']">▾</span>
              </button>
              <div v-if="openMenu === 'teacherCourses'" class="dropdown-menu">
                <RouterLink to="/teacher/courses" @click="handleNavLinkClick">课程看板</RouterLink>
                <RouterLink to="/teacher/students" @click="handleNavLinkClick">学生管理</RouterLink>
              </div>
            </div>
            <RouterLink class="nav-rect-btn" to="/docs" @click="handleNavLinkClick">技术文档</RouterLink>
          </template>
        </nav>
        <div v-if="isLoggedIn" class="session-area">
          <div class="account-dropdown">
            <button
              type="button"
              :class="['account-trigger', openMenu === 'account' ? 'active' : '']"
              @click.stop="toggleMenu('account')"
              :aria-expanded="openMenu === 'account' ? 'true' : 'false'"
              aria-haspopup="menu"
            >
              <span class="account-text">{{ userLabel }}</span>
              <span :class="['caret', openMenu === 'account' ? 'open' : '']">▾</span>
            </button>
            <div v-if="openMenu === 'account'" class="account-menu" role="menu">
              <RouterLink to="/profile" role="menuitem" @click="handleNavLinkClick">个人中心</RouterLink>
              <button type="button" role="menuitem" @click="handleLogout">退出登录</button>
            </div>
          </div>
        </div>
      </div>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { getAccessToken, getCurrentUserProfile, getStoredCurrentUser, logout } from "./api/auth";
import { platformConfig } from "./config/platform";

const route = useRoute();
const router = useRouter();
const currentUser = ref(getStoredCurrentUser());
const hasToken = ref(Boolean(getAccessToken()));
const role = computed(() => currentUser.value?.role || "");
const isAdmin = computed(() => role.value === "admin");
const isTeacher = computed(() => role.value === "teacher");
const isStudent = computed(() => role.value === "student");
const isLoggedIn = computed(() => hasToken.value || Boolean(currentUser.value));
const isLoginPage = computed(() => route.path === "/login");
const navRef = ref(null);
const openMenu = ref("");
const mobileNavOpen = ref(false);
const usersGroupActive = computed(() => ["/admin/users", "/admin/teachers", "/admin/admin-users"].includes(route.path));
const docsGroupActive = computed(() => route.path === "/admin/docs" || route.path === "/docs");
const coursesGroupActive = computed(() => route.path.startsWith("/admin/courses") || route.path.startsWith("/admin/classes") || route.path.startsWith("/courses"));
const teacherCoursesGroupActive = computed(() => route.path.startsWith("/teacher/courses") || route.path.startsWith("/teacher/students") || route.path === "/teacher/student-import");
const platformName = platformConfig.platformName;
const userLabel = computed(() => {
  if (!currentUser.value) {
    return "";
  }
  const name = currentUser.value.full_name || currentUser.value.username || "用户";
  const roleText = platformConfig.roleLabels[currentUser.value.role] || currentUser.value.role;
  const mustChangeHint = currentUser.value.must_change_password ? "，需改密" : "";
  return `${name}（${roleText}${mustChangeHint}）`;
});

async function refreshCurrentUser() {
  const token = getAccessToken();
  hasToken.value = Boolean(token);
  if (!token) {
    currentUser.value = null;
    return;
  }
  try {
    currentUser.value = await getCurrentUserProfile();
  } catch (error) {
    currentUser.value = null;
    hasToken.value = Boolean(getAccessToken());
  }
}

async function handleLogout() {
  logout();
  currentUser.value = null;
  hasToken.value = false;
  closeMenus();
  closeMobileNav();
  if (typeof window !== "undefined") {
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }
  if (route.path !== "/login") {
    await router.replace("/login");
  }
}

function closeMenus() {
  openMenu.value = "";
}

function closeMobileNav() {
  mobileNavOpen.value = false;
}

function toggleMobileNav() {
  mobileNavOpen.value = !mobileNavOpen.value;
  if (!mobileNavOpen.value) {
    closeMenus();
  }
}

function toggleMenu(menuName) {
  openMenu.value = openMenu.value === menuName ? "" : menuName;
}

function handleNavLinkClick() {
  closeMenus();
  closeMobileNav();
}

function handleDocumentClick(event) {
  if (!navRef.value) {
    closeMenus();
    return;
  }
  const target = event.target;
  if (!(target instanceof Node) || !navRef.value.contains(target)) {
    closeMenus();
  }
}

watch(
  () => route.fullPath,
  async () => {
    closeMenus();
    closeMobileNav();
    await refreshCurrentUser();
  },
);

onMounted(async () => {
  await refreshCurrentUser();
  document.addEventListener("click", handleDocumentClick);
  window.addEventListener("storage", refreshCurrentUser);
  window.addEventListener("keydown", handleWindowKeydown);
  window.addEventListener("resize", handleWindowResize);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleDocumentClick);
  window.removeEventListener("storage", refreshCurrentUser);
  window.removeEventListener("keydown", handleWindowKeydown);
  window.removeEventListener("resize", handleWindowResize);
});

function handleWindowKeydown(event) {
  if (event.key === "Escape") {
    closeMenus();
    closeMobileNav();
  }
}

function handleWindowResize() {
  if (typeof window !== "undefined" && window.innerWidth > 860) {
    closeMobileNav();
  }
}

</script>

<style scoped>
.layout {
  min-height: 100vh;
  background: transparent;
}

.header {
  position: sticky;
  top: 0;
  z-index: var(--z-header);
  padding: 14px 24px;
  border-bottom: 1px solid var(--border-soft);
  background: var(--surface-1);
  background: color-mix(in srgb, var(--surface-1) 84%, var(--brand-soft) 16%);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.header-brand {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.header h1 {
  margin: 0;
  font-size: clamp(20px, 1.25vw, 24px);
  letter-spacing: 0.01em;
  color: var(--text-strong);
}

.mobile-menu-btn {
  display: none;
  border: 1px solid color-mix(in srgb, var(--brand-border) 74%, var(--border-soft) 26%);
  background: color-mix(in srgb, var(--surface-1) 74%, var(--brand-soft) 26%);
  color: var(--brand-800);
  border-radius: var(--radius-sm);
  height: 38px;
  min-width: 66px;
  padding: 0 12px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.01em;
  box-shadow:
    inset 0 1px 0 color-mix(in srgb, var(--surface-1) 84%, transparent),
    0 7px 12px color-mix(in srgb, var(--brand-700) 14%, transparent);
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease;
}

.mobile-menu-btn:hover {
  border-color: var(--brand-border-strong);
  background: color-mix(in srgb, var(--brand-soft-2) 60%, var(--surface-2) 40%);
  color: var(--brand-800);
  transform: none;
  filter: none;
}

.nav {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.nav > a {
  color: var(--brand-600);
  text-decoration: none;
}

.nav > a.router-link-active {
  font-weight: 600;
}

.admin-nav-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-dropdown {
  position: relative;
}

.nav-rect-btn,
.nav-drop-trigger {
  border: 1px solid color-mix(in srgb, var(--brand-border) 74%, var(--border-soft) 26%);
  background: color-mix(in srgb, var(--surface-1) 74%, var(--brand-soft) 26%);
  color: var(--brand-800);
  min-width: 108px;
  width: auto;
  height: 38px;
  border-radius: var(--radius-sm);
  padding: 0 12px;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: 0.01em;
  text-decoration: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  box-sizing: border-box;
  white-space: nowrap;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  box-shadow:
    inset 0 1px 0 color-mix(in srgb, var(--surface-1) 84%, transparent),
    0 7px 12px color-mix(in srgb, var(--brand-700) 14%, transparent);
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease;
}

.nav-rect-btn {
  display: inline-flex;
}

.nav-rect-btn.router-link-active,
.nav-drop-trigger.active {
  border-color: var(--brand-border-strong);
  background: color-mix(in srgb, var(--brand-soft-2) 72%, var(--surface-2) 28%);
  color: var(--brand-800);
  font-weight: 600;
}

.nav-rect-btn:hover,
.nav-drop-trigger:hover {
  border-color: var(--brand-border-strong);
  background: color-mix(in srgb, var(--brand-soft-2) 60%, var(--surface-2) 40%);
  color: var(--brand-800);
  transform: none;
  filter: none;
}

.caret {
  transition: transform 0.2s ease;
}

.caret.open {
  transform: rotate(180deg);
}

.nav-drop-trigger .caret,
.account-trigger .caret {
  font-size: 12px;
  opacity: 0.9;
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  min-width: 176px;
  z-index: calc(var(--z-header) + 10);
  background: color-mix(in srgb, var(--surface-1) 90%, var(--brand-soft) 10%);
  border: 1px solid color-mix(in srgb, var(--brand-border) 34%, var(--border-soft) 66%);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-elevated);
  padding: 8px;
  display: grid;
  gap: 6px;
}

.dropdown-menu a {
  color: #1d2f4d;
  text-decoration: none;
  padding: 9px 11px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.35;
  letter-spacing: 0.01em;
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  white-space: nowrap;
}

.dropdown-menu a:hover {
  background: color-mix(in srgb, var(--brand-soft) 38%, var(--surface-2) 62%);
  color: #142746;
  transform: none;
  filter: none;
}

.dropdown-menu a.router-link-active {
  font-weight: 600;
  color: var(--brand-700);
  background: color-mix(in srgb, var(--brand-soft) 74%, transparent);
}

.session-area {
  display: flex;
  align-items: center;
  gap: 10px;
}

.account-dropdown {
  position: relative;
  --account-btn-bg: #9f3f4b;
  --account-btn-bg-hover: #903541;
  --account-btn-bg-active: #7d2a36;
  --account-btn-border: #b96570;
  --account-btn-border-hover: #ab5561;
  --account-btn-text: #fff5f6;
  --account-menu-bg: color-mix(in srgb, var(--surface-1) 90%, #f7e8eb 10%);
  --account-menu-border: color-mix(in srgb, var(--account-btn-border) 34%, var(--border-soft) 66%);
  --account-menu-hover: color-mix(in srgb, var(--account-btn-bg) 12%, var(--surface-2) 88%);
  --account-menu-text: #1d2f4d;
  --account-menu-text-hover: #142746;
  --account-menu-logout: #7b2633;
  --account-menu-logout-hover: #651926;
}

.account-trigger {
  border: 1px solid var(--account-btn-border);
  background: var(--account-btn-bg);
  color: var(--account-btn-text);
  border-radius: var(--radius-sm);
  height: 38px;
  min-width: 0;
  width: fit-content;
  max-width: min(44vw, 360px);
  padding: 0 10px 0 12px;
  display: inline-flex;
  align-items: center;
  justify-content: space-between;
  box-sizing: border-box;
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
  gap: 10px;
  letter-spacing: 0.01em;
  box-shadow:
    inset 0 1px 0 color-mix(in srgb, var(--surface-1) 26%, transparent),
    0 8px 14px rgba(86, 18, 32, 0.18);
  cursor: pointer;
  transition:
    background-color 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    color 0.2s ease;
}

.account-trigger:hover {
  border-color: var(--account-btn-border-hover);
  background: var(--account-btn-bg-hover);
}

.account-trigger.active {
  border-color: var(--account-btn-border-hover);
  background: var(--account-btn-bg-active);
  box-shadow:
    inset 0 1px 0 color-mix(in srgb, var(--surface-1) 22%, transparent),
    0 0 0 2px color-mix(in srgb, var(--account-btn-bg) 34%, transparent);
}

.account-text {
  min-width: 0;
  max-width: min(34vw, 280px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.2;
}

.account-trigger .caret {
  margin-left: auto;
  flex: 0 0 auto;
}

.account-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  min-width: 176px;
  z-index: calc(var(--z-header) + 10);
  background: var(--account-menu-bg);
  border: 1px solid var(--account-menu-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-elevated);
  padding: 8px;
  display: grid;
  gap: 6px;
}

.account-menu a,
.account-menu button {
  width: 100%;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: var(--account-menu-text);
  text-decoration: none;
  padding: 9px 11px;
  font-size: 14px;
  font-weight: 600;
  line-height: 1.35;
  letter-spacing: 0.01em;
  min-height: 42px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  text-align: left;
  white-space: nowrap;
  cursor: pointer;
}

.account-menu a:hover,
.account-menu button:hover {
  background: var(--account-menu-hover);
  color: var(--account-menu-text-hover);
  transform: none;
  filter: none;
}

.account-menu button {
  color: var(--account-menu-logout);
}

.account-menu button:hover {
  color: var(--account-menu-logout-hover);
}

.account-menu a.router-link-active {
  background: color-mix(in srgb, var(--brand-soft) 76%, transparent);
  color: var(--brand-700);
}

.mobile-menu-btn:focus-visible,
.nav-rect-btn:focus-visible,
.nav-drop-trigger:focus-visible,
.account-trigger:focus-visible,
.dropdown-menu a:focus-visible,
.account-menu a:focus-visible,
.account-menu button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--focus-ring);
}

.main {
  max-width: 1180px;
  margin: 0 auto;
  padding: clamp(16px, 2.2vw, 28px);
}

@media (max-width: 1024px) {
  .nav {
    gap: 10px;
  }

  .nav-rect-btn,
  .nav-drop-trigger {
    min-width: 100px;
    padding: 0 10px;
    font-size: 13px;
  }
}

@media (max-width: 860px) {
  .header {
    align-items: stretch;
    flex-direction: column;
    padding: 12px 14px;
    gap: 10px;
  }

  .header-brand {
    width: 100%;
  }

  .mobile-menu-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    height: 44px;
    font-size: 14px;
    line-height: 1.2;
  }

  .header-right {
    position: relative;
    z-index: calc(var(--z-header) + 2);
    width: 100%;
    background: color-mix(in srgb, var(--surface-1) 92%, var(--surface-2) 8%);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-elevated);
    padding: 12px;
    display: none;
    max-height: none;
    overflow: visible;
    transform: none;
  }

  .header-right.open {
    display: grid;
    gap: 10px;
  }

  .nav,
  .admin-nav-group,
  .session-area {
    width: 100%;
  }

  .nav,
  .admin-nav-group {
    display: grid;
    gap: 10px;
    align-items: stretch;
  }

  .nav-dropdown {
    width: 100%;
  }

  .nav-rect-btn,
  .nav-drop-trigger,
  .account-trigger {
    width: 100%;
    min-width: 0;
    height: auto;
    min-height: 48px;
    padding: 10px 14px;
    line-height: 1.25;
    font-size: 14px;
  }

  .header-right .nav > a.nav-rect-btn,
  .header-right .nav .nav-drop-trigger,
  .header-right .session-area .account-trigger {
    min-height: 50px;
    padding: 11px 20px;
    line-height: 1.25;
    font-size: 14px;
    letter-spacing: 0.01em;
    display: flex;
    align-items: center;
    box-sizing: border-box;
  }

  .header-right .nav > a.nav-rect-btn {
    justify-content: flex-start;
    text-align: left;
  }

  .header-right .nav .nav-drop-trigger,
  .header-right .session-area .account-trigger {
    justify-content: space-between;
    width: 100%;
    max-width: none;
    min-width: 0;
    padding-right: 18px;
  }

  .account-dropdown {
    width: 100%;
  }

  .account-menu {
    position: static;
    min-width: 0;
    box-shadow: none;
    border-radius: var(--radius-sm);
    border: 1px solid var(--account-menu-border);
    margin-top: 6px;
  }

  .dropdown-menu {
    position: static;
    min-width: 0;
    box-shadow: none;
    border-radius: var(--radius-sm);
    border: 1px solid color-mix(in srgb, var(--brand-border) 34%, var(--border-soft) 66%);
    padding: 6px;
    margin-top: 6px;
  }

  .dropdown-menu a,
  .account-menu a,
  .account-menu button {
    min-height: 46px;
    padding: 11px 18px;
    line-height: 1.3;
    font-size: 14px;
  }

  .session-area {
    display: grid;
    gap: 10px;
  }

  .account-trigger {
    font-size: 14px;
    color: var(--account-btn-text);
    line-height: 1.2;
  }

  .account-text {
    max-width: none;
  }

  .main {
    padding: 12px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .mobile-menu-btn,
  .nav-rect-btn,
  .nav-drop-trigger,
  .account-trigger,
  .caret {
    transition: none !important;
    animation: none !important;
  }
}
</style>
