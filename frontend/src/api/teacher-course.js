import request from "./request";

export async function getTeacherCourses() {
  const { data } = await request.get("/teacher/courses");
  return data;
}

export async function getTeacherClasses(params = {}) {
  const { data } = await request.get("/teacher/classes", { params });
  return data;
}

export async function getTeacherTaskSubmissions(taskId) {
  const { data } = await request.get(`/teacher/tasks/${taskId}/submissions`);
  return data;
}

export async function reviewTeacherSubmission(submissionId, payload) {
  const { data } = await request.post(`/teacher/submissions/${submissionId}/review`, payload);
  return data;
}
