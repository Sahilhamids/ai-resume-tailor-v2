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
    throw new ApiError("Session expired, please log in again.");
  }
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(body.detail || `Request failed (${res.status})`);
  }

  const contentType = res.headers.get("content-type") || "";
  return contentType.includes("application/json") ? res.json() : res;
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

export async function exportPdf(tailoredResume) {
  return api("/resume/export-pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(tailoredResume),
  });
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
