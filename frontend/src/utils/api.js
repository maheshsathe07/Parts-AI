import axios from "axios";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:3001";

export const researchPart = async (part) => {
  const response = await axios.post(`${API_BASE}/api/research`, { part });
  return response.data;
};