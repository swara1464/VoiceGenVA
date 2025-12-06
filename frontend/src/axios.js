import axios from "axios";

axios.defaults.withCredentials = false;
axios.defaults.baseURL = "https://vocalagentapi.onrender.com";

// Automatically attach JWT from localStorage to every request
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem("session_token");
  if (token) {
    config.headers["Authorization"] = `Bearer ${token}`;
  }
  return config;
});

export default axios;

