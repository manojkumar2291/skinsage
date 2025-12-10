import axios from "axios";

const API = axios.create({
  baseURL: "https://1k7bh55m-8000.inc1.devtunnels.ms/api",
});

// attach token automatically
API.interceptors.request.use((req) => {
  const token = localStorage.getItem("access_token");
  if (token) req.headers.Authorization = `Bearer ${token}`;
  return req;
});

export default API;
