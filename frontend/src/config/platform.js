export const platformConfig = {
  platformName: "LETS课程管理系统",
  defaultHomeByRole: {
    student: "/dashboard",
    teacher: "/teacher/courses",
    admin: "/admin",
  },
  roleLabels: {
    student: "学生",
    teacher: "教师",
    admin: "管理员",
  },
  taskTypeLabels: {
    reading: "阅读",
    assignment: "作业",
    quiz: "测验",
    file_upload: "文件上传",
    text_response: "文本回答",
    external_link: "外部链接",
    custom: "自定义",
  },
  courseStatusLabels: {
    draft: "草稿",
    published: "已发布",
    archived: "已归档",
  },
};
