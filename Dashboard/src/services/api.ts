import axios from 'axios';

// En desarrollo, Vite proxy maneja el routing (baseURL vacío)
// En producción, usa la variable de entorno o el proxy de Nginx
const API_BASE = import.meta.env.VITE_API_URL || '';

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
export const createUser = (data: any) => api.post('/users', data);
export const getUserMemorySessions = (userId: number) =>
    api.get(`/admin/user-memory-sessions/${userId}`);
export const getUserAbecedarioSessions = (userId: number) =>
    api.get(`/admin/user-abecedario-sessions/${userId}`);
export const getUserPaseoSessions = (userId: number) =>
    api.get(`/admin/user-paseo-sessions/${userId}`);
export const getUserTrainSessions = (userId: number) =>
    api.get(`/admin/user-train-sessions/${userId}`);
export const getProgressionStats = (userId: number) =>
    api.get(`/admin/progression-stats/${userId}`).then(res => res.data);
export const getGeneralProgressionStats = () =>
    api.get('/admin/general-progression-stats').then(res => res.data);
export const getIndicators = (userId?: number | string) =>
    userId && userId !== 'general'
        ? api.get(`/admin/indicators/${userId}`).then(res => res.data)
        : api.get('/admin/indicators').then(res => res.data);

export default api;
