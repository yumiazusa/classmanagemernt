import request from "./request";

export async function importTeacherStudents(file, courseId) {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await request.post("/teacher/students/import", formData, {
    params: { course_id: courseId },
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

export async function createTeacherStudent(payload, courseId) {
  const { data } = await request.post("/teacher/students", payload, { params: { course_id: courseId } });
  return data;
}

export async function getTeacherStudentClassOptions(courseId) {
  const { data } = await request.get("/teacher/students/class-options", { params: { course_id: courseId } });
  return data;
}

export async function batchResetTeacherStudentPasswords(payload, courseId) {
  const { data } = await request.post("/teacher/students/batch-reset-password", payload, { params: { course_id: courseId } });
  return data;
}

export async function enableTeacherStudent(userId, courseId) {
  const { data } = await request.post(`/teacher/students/${userId}/enable`, null, { params: { course_id: courseId } });
  return data;
}

export async function disableTeacherStudent(userId, courseId) {
  const { data } = await request.post(`/teacher/students/${userId}/disable`, null, { params: { course_id: courseId } });
  return data;
}

export async function resetTeacherStudentPassword(userId, payload, courseId) {
  const { data } = await request.post(`/teacher/students/${userId}/reset-password`, payload, { params: { course_id: courseId } });
  return data;
}

export async function batchEnableTeacherStudents(payload, courseId) {
  const { data } = await request.post("/teacher/students/batch-enable", payload, { params: { course_id: courseId } });
  return data;
}

export async function batchDisableTeacherStudents(payload, courseId) {
  const { data } = await request.post("/teacher/students/batch-disable", payload, { params: { course_id: courseId } });
  return data;
}

export async function exportTeacherStudents(params = {}) {
  const response = await request.get("/teacher/students/export", {
    params,
    responseType: "blob",
  });
  return response.data;
}
