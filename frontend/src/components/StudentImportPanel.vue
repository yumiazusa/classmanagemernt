<template>
  <article class="panel import-panel">
    <div class="panel-heading">
      <h3>{{ title }}</h3>
      <p>{{ hint }}</p>
    </div>

    <form v-if="api.createOne" class="single-form" @submit.prevent="handleCreateOne">
      <label>
        <span>学号</span>
        <input v-model.trim="singleForm.student_no" type="text" placeholder="请输入学号" :disabled="isCreating" />
      </label>
      <label>
        <span>姓名</span>
        <input v-model.trim="singleForm.full_name" type="text" placeholder="请输入姓名" :disabled="isCreating" />
      </label>
      <label v-if="showClassInput">
        <span>班级</span>
        <select v-model="singleForm.class_name" :disabled="isCreating || isClassOptionsLoading">
          <option value="">请选择班级</option>
          <option v-for="name in classOptions" :key="name" :value="name">{{ name }}</option>
        </select>
      </label>
      <label>
        <span>初始密码</span>
        <input v-model.trim="singleForm.password" type="text" placeholder="默认 123456" :disabled="isCreating" />
      </label>
      <button type="submit" class="btn upload" :disabled="isCreating">
        {{ isCreating ? "添加中..." : "添加学生" }}
      </button>
    </form>

    <div class="divider"></div>

    <div class="uploader">
      <input ref="fileInputRef" type="file" accept=".xlsx" @change="handleSelectFile" />
      <button type="button" class="btn download" :disabled="isDownloadingTemplate" @click="handleDownloadTemplate">
        {{ isDownloadingTemplate ? "下载中..." : "下载模板" }}
      </button>
      <button type="button" class="btn upload" :disabled="isUploading || !selectedFile" @click="handleImport">
        {{ isUploading ? "导入中..." : "开始导入" }}
      </button>
    </div>
    <p class="file-hint">当前文件：{{ selectedFile ? selectedFile.name : "未选择文件" }}</p>
    <p v-if="message" :class="['message', messageIsError ? 'bad' : 'good']">{{ message }}</p>
    <div v-if="importResult" class="result-grid">
      <span>总行数 {{ importResult.total_rows }}</span>
      <span>新建 {{ importResult.created_count }}</span>
      <span>更新 {{ importResult.updated_count }}</span>
      <span>跳过 {{ importResult.skipped_count }}</span>
      <span>错误 {{ importResult.failed_items.length }}</span>
    </div>
  </article>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";

const props = defineProps({
  api: { type: Object, required: true },
  title: { type: String, default: "添加学生" },
  hint: { type: String, default: "支持 .xlsx。模板至少包含学号、姓名；如有班级列，将按当前页面规则处理。" },
  filename: { type: String, default: "学生名单导入模板.xlsx" },
  showClassInput: { type: Boolean, default: true },
});

const emit = defineEmits(["imported"]);

const selectedFile = ref(null);
const fileInputRef = ref(null);
const isCreating = ref(false);
const isUploading = ref(false);
const isDownloadingTemplate = ref(false);
const isClassOptionsLoading = ref(false);
const importResult = ref(null);
const message = ref("");
const messageIsError = ref(false);
const classOptions = ref([]);
const singleForm = reactive({
  student_no: "",
  full_name: "",
  class_name: "",
  password: "123456",
});

function handleSelectFile(event) {
  selectedFile.value = event?.target?.files?.[0] || null;
  importResult.value = null;
  message.value = "";
  messageIsError.value = false;
}

function triggerFileDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

async function handleDownloadTemplate() {
  isDownloadingTemplate.value = true;
  message.value = "";
  try {
    const blob = await props.api.downloadTemplate();
    triggerFileDownload(blob, props.filename);
  } catch (error) {
    message.value = `模板下载失败：${error.message}`;
    messageIsError.value = true;
  } finally {
    isDownloadingTemplate.value = false;
  }
}

async function loadClassOptions() {
  if (!props.showClassInput || !props.api.classOptions) return;
  isClassOptionsLoading.value = true;
  try {
    const options = await props.api.classOptions();
    classOptions.value = Array.isArray(options) ? options : [];
  } catch (error) {
    message.value = `班级选项加载失败：${error.message}`;
    messageIsError.value = true;
  } finally {
    isClassOptionsLoading.value = false;
  }
}

async function handleCreateOne() {
  if (!props.api.createOne) return;
  message.value = "";
  messageIsError.value = false;
  const payload = {
    student_no: singleForm.student_no,
    full_name: singleForm.full_name,
    password: singleForm.password || "123456",
  };
  if (props.showClassInput) {
    payload.class_name = singleForm.class_name;
  }
  if (!payload.student_no || !payload.full_name || (props.showClassInput && !payload.class_name)) {
    message.value = props.showClassInput ? "请填写学号、姓名和班级" : "请填写学号和姓名";
    messageIsError.value = true;
    return;
  }
  isCreating.value = true;
  try {
    await props.api.createOne(payload);
    message.value = "学生已添加";
    singleForm.student_no = "";
    singleForm.full_name = "";
    singleForm.password = "123456";
    emit("imported");
  } catch (error) {
    message.value = `添加失败：${error.message}`;
    messageIsError.value = true;
  } finally {
    isCreating.value = false;
  }
}

async function handleImport() {
  if (!selectedFile.value) {
    message.value = "请先选择 .xlsx 文件";
    messageIsError.value = true;
    return;
  }
  if (!selectedFile.value.name.toLowerCase().endsWith(".xlsx")) {
    message.value = "仅支持 .xlsx 文件";
    messageIsError.value = true;
    return;
  }
  isUploading.value = true;
  message.value = "";
  messageIsError.value = false;
  importResult.value = null;
  try {
    const result = await props.api.importFile(selectedFile.value);
    importResult.value = result;
    message.value = result.message || "导入完成";
    if (fileInputRef.value) {
      fileInputRef.value.value = "";
    }
    selectedFile.value = null;
    emit("imported", result);
  } catch (error) {
    message.value = `导入失败：${error.message}`;
    messageIsError.value = true;
  } finally {
    isUploading.value = false;
  }
}

onMounted(loadClassOptions);
</script>

<style scoped>
.panel {
  background: var(--surface-1);
  border: 1px solid var(--border-soft);
  border-radius: 12px;
  padding: 18px;
}
.import-panel {
  display: grid;
  gap: 12px;
}
.panel-heading {
  display: grid;
  gap: 6px;
}
h3,
p {
  margin: 0;
}
p,
.file-hint {
  color: var(--text-muted);
}
.uploader,
.result-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.single-form {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr)) auto;
  gap: 10px;
  align-items: end;
}
.single-form label {
  display: grid;
  gap: 6px;
  color: var(--text-muted);
}
.single-form input,
.single-form select {
  min-width: 0;
  border: 1px solid var(--border-soft);
  border-radius: 10px;
  padding: 10px 12px;
  font: inherit;
  color: var(--text-strong);
}
.divider {
  height: 1px;
  background: var(--border-soft);
}
.btn {
  border: 0;
  border-radius: 10px;
  padding: 10px 14px;
  font-weight: 700;
  cursor: pointer;
}
.download {
  background: var(--surface-2);
  color: var(--text-strong);
}
.upload {
  background: var(--brand-600);
  color: var(--surface-1);
}
.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
.message.good {
  color: var(--success-strong);
}
.message.bad {
  color: var(--danger-strong);
}
.result-grid span {
  border-radius: 999px;
  background: var(--brand-soft);
  color: var(--brand-700);
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 700;
}
@media (max-width: 980px) {
  .single-form {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 640px) {
  .single-form {
    grid-template-columns: 1fr;
  }
}
</style>
