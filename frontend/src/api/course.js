import request from "./request";

export async function getCourses() {
  const { data } = await request.get("/courses");
  return data;
}

export async function getCourseById(courseId) {
  const { data } = await request.get(`/courses/${courseId}`);
  return data;
}

export async function getCourseModules(courseId) {
  const { data } = await request.get(`/courses/${courseId}/modules`);
  return data;
}

export async function getCourseTasks(courseId) {
  const { data } = await request.get(`/courses/${courseId}/tasks`);
  return data;
}

export async function getTaskById(taskId) {
  const { data } = await request.get(`/tasks/${taskId}`);
  return data;
}

export async function submitTask(taskId, payload) {
  const { data } = await request.post(`/tasks/${taskId}/submissions`, payload);
  return data;
}
