import request from "./request";

export async function importTeacherStudents(file) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await request.post("/teacher/students/import", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return data;
}

export async function downloadTeacherStudentImportTemplate() {
  const response = await request.get("/teacher/students/import-template", {
    responseType: "blob",
  });
  return response.data;
}

export async function getTeacherStudents(params = {}) {
  const { data } = await request.get("/teacher/students", { params });
  return data;
}

export async function createTeacherStudent(payload) {
  const { data } = await request.post("/teacher/students", payload);
  return data;
}

export async function getTeacherStudentClassOptions() {
  const { data } = await request.get("/teacher/students/class-options");
  return data;
}

export async function batchResetTeacherStudentPasswords(payload) {
  const { data } = await request.post("/teacher/students/batch-reset-password", payload);
  return data;
}

export async function enableTeacherStudent(userId) {
  const { data } = await request.post(`/teacher/students/${userId}/enable`);
  return data;
}

export async function disableTeacherStudent(userId) {
  const { data } = await request.post(`/teacher/students/${userId}/disable`);
  return data;
}

export async function resetTeacherStudentPassword(userId, payload) {
  const { data } = await request.post(`/teacher/students/${userId}/reset-password`, payload);
  return data;
}

export async function batchEnableTeacherStudents(payload) {
  const { data } = await request.post("/teacher/students/batch-enable", payload);
  return data;
}

export async function batchDisableTeacherStudents(payload) {
  const { data } = await request.post("/teacher/students/batch-disable", payload);
  return data;
}

export async function exportTeacherStudents(params = {}) {
  const response = await request.get("/teacher/students/export", {
    params,
    responseType: "blob",
  });
  return response.data;
}
