import axios from 'axios';

const API_BASE = '';  // Empty because Vite proxy will handle routing

const api = axios.create({
    baseURL: API_BASE,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Stats
export const getStats = () => api.get('/admin/stats');

// Memory Game
export const getMemorySessions = () => api.get('/admin/memory-sessions');
export const getMemoryConfigs = () => api.get('/admin/memory-configs');

// Abecedario
export const getAbecedarioSessions = () => api.get('/admin/abecedario-sessions');

// Paseo
export const getPaseoSessions = () => api.get('/admin/paseo-sessions');

// Train
export const getTrainSessions = () => api.get('/admin/train-sessions');
export const getTrainConfigs = () => api.get('/admin/train-configs');

// Users
export const getUsers = () => api.get('/users');
export const getUserMemorySessions = (userId: number) =>
    api.get(`/admin/user-memory-sessions/${userId}`);
export const getUserAbecedarioSessions = (userId: number) =>
    api.get(`/admin/user-abecedario-sessions/${userId}`);
export const getUserPaseoSessions = (userId: number) =>
    api.get(`/admin/user-paseo-sessions/${userId}`);
export const getUserTrainSessions = (userId: number) =>
    api.get(`/admin/user-train-sessions/${userId}`);

export default api;
