import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

export const api = axios.create({
  baseURL: BASE_URL,
});

// Attach the right bearer token depending on which portal is making the call.
// Each portal (patient / doctor / admin) stores its own token under its own key,
// since a person could theoretically be logged into more than one role's flow
// in different tabs.
export function withAuth(role) {
  const token = localStorage.getItem(`mediconnect_${role}_token`);
  return token ? { headers: { Authorization: `Bearer ${token}` } } : {};
}

export function getStoredToken(role) {
  return localStorage.getItem(`mediconnect_${role}_token`);
}

export function storeToken(role, token) {
  localStorage.setItem(`mediconnect_${role}_token`, token);
}

export function clearToken(role) {
  localStorage.removeItem(`mediconnect_${role}_token`);
}

export function extractErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (!detail) return "Something went wrong. Please try again.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || JSON.stringify(d)).join(" ");
  }
  return "Something went wrong. Please try again.";
}
