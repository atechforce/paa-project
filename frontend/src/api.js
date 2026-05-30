import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/api",
  headers: {
    "Content-Type": "application/json"
  }
});

export const getLocations = () => api.get("/locations");
export const solveTsp = (payload) => api.post("/tsp/solve", payload);

export default api;
