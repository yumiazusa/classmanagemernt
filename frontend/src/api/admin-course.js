import request from "./request";

export async function getAdminCourses(params = {}) {
  const { data } = await request.get("/admin/courses", { params });
  return data;
}

export async function getAdminCourseExperiences() {
  const { data } = await request.get("/admin/course-experiences");
  return data;
}

export async function getAdminCourseWorkspace(courseId) {
  const { data } = await request.get(`/admin/courses/${courseId}/workspace`);
  return data;
}

export async function getAdminCourseDocs(courseId) {
  const { data } = await request.get(`/admin/courses/${courseId}/docs`);
  return data;
}

export async function createAdminCourseDoc(courseId, payload) {
  const { data } = await request.post(`/admin/courses/${courseId}/docs`, payload);
  return data;
}

export async function updateAdminCourseDoc(courseId, docId, payload) {
  const { data } = await request.put(`/admin/courses/${courseId}/docs/${docId}`, payload);
  return data;
}

export async function deleteAdminCourseDoc(courseId, docId) {
  const { data } = await request.delete(`/admin/courses/${courseId}/docs/${docId}`);
  return data;
}

export async function createAdminCourse(payload) {
  const { data } = await request.post("/admin/courses", payload);
  return data;
}

export async function updateAdminCourse(courseId, payload) {
  const { data } = await request.put(`/admin/courses/${courseId}`, payload);
  return data;
}

export async function deleteAdminCourse(courseId) {
  const { data } = await request.delete(`/admin/courses/${courseId}`);
  return data;
}

export async function createAdminModule(courseId, payload) {
  const { data } = await request.post(`/admin/courses/${courseId}/modules`, payload);
  return data;
}

export async function createAdminTask(courseId, payload) {
  const { data } = await request.post(`/admin/courses/${courseId}/tasks`, payload);
  return data;
}

export async function getAdminClasses(params = {}) {
  const { data } = await request.get("/admin/classes", { params });
  return data;
}

export async function getAdminClassById(classId) {
  const { data } = await request.get(`/admin/classes/${classId}`);
  return data;
}

export async function createAdminClass(payload) {
  const { data } = await request.post("/admin/classes", payload);
  return data;
}

export async function getAdminClassStudents(classId, params = {}) {
  const { data } = await request.get(`/admin/classes/${classId}/students`, { params });
  return data;
}

export async function createAdminClassStudent(classId, payload) {
  const { data } = await request.post(`/admin/classes/${classId}/students`, payload);
  return data;
}

export async function importAdminClassStudents(classId, file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await request.post(`/admin/classes/${classId}/students/import`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function downloadAdminClassStudentImportTemplate(classId) {
  const response = await request.get(`/admin/classes/${classId}/students/import-template`, { responseType: "blob" });
  return response.data;
}

export async function exportAdminClassStudents(classId, params = {}) {
  const response = await request.get(`/admin/classes/${classId}/students/export`, {
    params,
    responseType: "blob",
  });
  return response.data;
}

export async function enableAdminClassStudent(classId, userId) {
  const { data } = await request.post(`/admin/classes/${classId}/students/${userId}/enable`);
  return data;
}

export async function disableAdminClassStudent(classId, userId) {
  const { data } = await request.post(`/admin/classes/${classId}/students/${userId}/disable`);
  return data;
}

export async function resetAdminClassStudentPassword(classId, userId, payload) {
  const { data } = await request.post(`/admin/classes/${classId}/students/${userId}/reset-password`, payload);
  return data;
}

export async function batchEnableAdminClassStudents(classId, payload) {
  const { data } = await request.post(`/admin/classes/${classId}/students/batch-enable`, payload);
  return data;
}

export async function batchDisableAdminClassStudents(classId, payload) {
  const { data } = await request.post(`/admin/classes/${classId}/students/batch-disable`, payload);
  return data;
}

export async function batchResetAdminClassStudentPasswords(classId, payload) {
  const { data } = await request.post(`/admin/classes/${classId}/students/batch-reset-password`, payload);
  return data;
}
