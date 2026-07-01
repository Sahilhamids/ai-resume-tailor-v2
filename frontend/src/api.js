const TOKEN_KEY = "token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {}

export async function api(path, options = {}) {
  options.headers = options.headers || {};
  const token = getToken();
  if (token) options.headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(path, options);

  if (res.status === 401) {
    clearToken();
    throw new ApiError("Session expired. Refresh the page to start a new session.");
  }
  if (res.status === 429) {
    throw new ApiError("Too many requests — please wait a moment and try again.");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(body.detail || `Request failed (${res.status})`);
  }

  const contentType = res.headers.get("content-type") || "";
  return contentType.includes("application/json") ? res.json() : res;
}

export async function createAnonymousSession() {
  return api("/auth/anonymous", { method: "POST" });
}

export async function signup(email, password) {
  return api("/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email, password) {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  return api("/auth/login", { method: "POST", body: form });
}

export async function getAccountStatus() {
  return api("/auth/me");
}

export async function linkAccount(email, password) {
  return api("/auth/link-account", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function deleteAccount() {
  return api("/account", { method: "DELETE" });
}

export async function getProfile() {
  return api("/profile");
}

export async function updateProfile(data) {
  return api("/profile", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function onboardFromPdf(file) {
  const formData = new FormData();
  formData.append("resume_file", file);
  return api("/profile/onboard-from-pdf", { method: "POST", body: formData });
}

export async function addSkill(skillName) {
  return api("/profile/skills", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ skill_name: skillName }),
  });
}

export async function deleteSkill(id) {
  return api(`/profile/skills/${id}`, { method: "DELETE" });
}

export async function addEmployment(data) {
  return api("/profile/employment", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function deleteEmployment(id) {
  return api(`/profile/employment/${id}`, { method: "DELETE" });
}

export async function addEducation(data) {
  return api("/profile/education", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function deleteEducation(id) {
  return api(`/profile/education/${id}`, { method: "DELETE" });
}

export async function addProject(data) {
  return api("/profile/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function deleteProject(id) {
  return api(`/profile/projects/${id}`, { method: "DELETE" });
}

export async function addCustomSection(data) {
  return api("/profile/custom-sections", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function deleteCustomSection(id) {
  return api(`/profile/custom-sections/${id}`, { method: "DELETE" });
}

export async function buildResume(jobDescription) {
  return api("/resume/build", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_description: jobDescription }),
  });
}

export async function getResumeTemplates() {
  return api("/resume/templates");
}

export async function previewResume(tailoredResume, template) {
  return api("/resume/preview", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tailored_resume: tailoredResume, template }),
  }).then((res) => res.text());
}

export async function exportPdf(tailoredResume, template) {
  return api("/resume/export-pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tailored_resume: tailoredResume, template }),
  });
}

export async function exportDocx(tailoredResume, template) {
  return api("/resume/export-docx", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tailored_resume: tailoredResume, template }),
  });
}

export async function saveResume(title, jobDescription, template, result) {
  return api("/resume/saved", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, job_description: jobDescription, template, result }),
  });
}

export async function listSavedResumes() {
  return api("/resume/saved");
}

export async function getSavedResume(id) {
  return api(`/resume/saved/${id}`);
}

export async function deleteSavedResume(id) {
  return api(`/resume/saved/${id}`, { method: "DELETE" });
}

export async function generateCoverLetter(jobDescription, companyName) {
  return api("/cover-letter/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_description: jobDescription, company_name: companyName }),
  });
}

export async function saveCoverLetter(title, companyName, content, savedResumeId) {
  return api("/cover-letter/saved", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, company_name: companyName, content, saved_resume_id: savedResumeId }),
  });
}

export async function listCoverLetters() {
  return api("/cover-letter/saved");
}

export async function deleteCoverLetter(id) {
  return api(`/cover-letter/saved/${id}`, { method: "DELETE" });
}

export async function createJobApplication(data) {
  return api("/jobs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function listJobApplications() {
  return api("/jobs");
}

export async function updateJobStatus(id, status) {
  return api(`/jobs/${id}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

export async function updateJobApplication(id, data) {
  return api(`/jobs/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function deleteJobApplication(id) {
  return api(`/jobs/${id}`, { method: "DELETE" });
}

export async function auditResume(file, jobDescription, role) {
  const formData = new FormData();
  formData.append("resume_file", file);
  formData.append("job_description", jobDescription);
  formData.append("role", role);
  return api("/resume/audit", { method: "POST", body: formData });
}

export async function getHistory() {
  return api("/resume/history");
}
