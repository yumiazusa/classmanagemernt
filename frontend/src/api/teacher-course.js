import request from "./request";

export async function getTeacherCourses() {
  const { data } = await request.get("/teacher/courses");
  return data;
}

export async function getTeacherCourse(courseId) {
  const { data } = await request.get(`/teacher/courses/${courseId}`);
  return data;
}

export async function getTeacherClasses(params = {}) {
  const { data } = await request.get("/teacher/classes", { params });
  return data;
}
