import request from "./request";

export async function getAdminOverview() {
  const { data } = await request.get("/admin/overview");
  return data;
}

export async function getAdminAdminUsers(params = {}) {
  const { data } = await request.get("/admin/admin-users", { params });
  return data;
}

export async function createAdminAdminUser(payload) {
  const { data } = await request.post("/admin/admin-users", payload);
  return data;
}

export async function enableAdminAdminUser(userId) {
  const { data } = await request.post(`/admin/admin-users/${userId}/enable`);
  return data;
}

export async function disableAdminAdminUser(userId) {
  const { data } = await request.post(`/admin/admin-users/${userId}/disable`);
  return data;
}

export async function resetAdminAdminUserPassword(userId, payload) {
  const { data } = await request.post(`/admin/admin-users/${userId}/reset-password`, payload);
  return data;
}

export async function getAdminUsers(params = {}) {
  const { data } = await request.get("/admin/users", { params });
  return data;
}

export async function getAdminUserClassOptions() {
  const { data } = await request.get("/admin/users/class-options");
  return data;
}

export async function createAdminTeacher(payload) {
  const { data } = await request.post("/admin/teachers", payload);
  return data;
}

export async function enableAdminUser(userId) {
  const { data } = await request.post(`/admin/users/${userId}/enable`);
  return data;
}

export async function disableAdminUser(userId) {
  const { data } = await request.post(`/admin/users/${userId}/disable`);
  return data;
}

export async function resetAdminUserPassword(userId, payload) {
  const { data } = await request.post(`/admin/users/${userId}/reset-password`, payload);
  return data;
}

export async function setAdminUserRole(userId, payload) {
  const { data } = await request.post(`/admin/users/${userId}/set-role`, payload);
  return data;
}

export async function updateAdminUserInfo(userId, payload) {
  const { data } = await request.post(`/admin/users/${userId}/update-info`, payload);
  return data;
}

export async function deleteAdminUser(userId) {
  const { data } = await request.post(`/admin/users/${userId}/delete`);
  return data;
}

export async function batchDeleteAdminUsers(payload) {
  const { data } = await request.post("/admin/users/batch-delete", payload);
  return data;
}

export async function batchEnableAdminUsers(payload) {
  const { data } = await request.post("/admin/users/batch-enable", payload);
  return data;
}

export async function batchDisableAdminUsers(payload) {
  const { data } = await request.post("/admin/users/batch-disable", payload);
  return data;
}

export async function batchResetAdminUserPasswords(payload) {
  const { data } = await request.post("/admin/users/batch-reset-password", payload);
  return data;
}

export async function getAdminDocs(params = {}) {
  const { data } = await request.get("/admin/docs", { params });
  return data;
}

export async function getAdminDocCategories() {
  const { data } = await request.get("/admin/docs/categories");
  return data;
}

export async function createAdminDoc(payload) {
  const { data } = await request.post("/admin/docs", payload);
  return data;
}

export async function updateAdminDoc(docId, payload) {
  const { data } = await request.put(`/admin/docs/${docId}`, payload);
  return data;
}

export async function deleteAdminDoc(docId) {
  const { data } = await request.delete(`/admin/docs/${docId}`);
  return data;
}
