/**
 * api.js — Axios instance with JWT interceptor.
 * All API calls go through this instance so the token is always attached.
 */

import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

// Attach JWT from localStorage to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
