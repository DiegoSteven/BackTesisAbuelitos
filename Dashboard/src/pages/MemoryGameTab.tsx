import { useQuery } from '@tanstack/react-query';
import { getMemorySessions, getMemoryConfigs } from '../services/api';
import StatsCard from '../components/Stats/StatsCard';

interface AIMetrics {
    overall_score?: number;
    adjustment_decision?: string;
    memory?: string;
    speed?: string;
    accuracy?: string;
}

interface MemorySession {
    session_id: number;
    user_id: number;
    difficulty_level: string;
    grid_size: string;
    total_pairs: number;
    accuracy?: number;
    elapsed_time?: number;
    completion_status: string;
    ai_metrics?: AIMetrics;
}

interface MemoryConfig {
    user_id: number;
    difficulty_label: string;
    grid_size: string;
    total_pairs: number;
    time_limit: number;
    memorization_time: number;
    consecutive_maintains?: number;
}

const formatMetricBadge = (metric?: string) => {
    if (!metric) return '-';
    const colors: Record<string, string> = {
        low: '#ff6b6b',
        medium: '#ffd93d',
        high: '#51cf66',
    };
    return (
        <span style={{ color: colors[metric], fontWeight: 'bold' }}>
            ● {metric}
        </span>
    );
};

const formatDecision = (decision?: string) => {
    if (decision === 'increase') return <span style={{ color: '#51cf66', fontSize: '1.2em' }}>↑</span>;
    if (decision === 'decrease') return <span style={{ color: '#ff6b6b', fontSize: '1.2em' }}>↓</span>;
    return <span style={{ color: '#ffd93d', fontSize: '1.2em' }}>═</span>;
};

const MemoryGameTab = () => {
    const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
        queryKey: ['memory-sessions'],
        queryFn: async () => {
            const res = await getMemorySessions();
            return res.data.sessions as MemorySession[];
        },
    });

    const { data: configsData } = useQuery({
        queryKey: ['memory-configs'],
        queryFn: async () => {
            const res = await getMemoryConfigs();
            return res.data.configs as MemoryConfig[];
        },
    });

    // Calculate stats
    const sessions = sessionsData || [];
    const configs = configsData || [];

    const avgAIScore = sessions.reduce((sum, s) => {
        return sum + (s.ai_metrics?.overall_score || 0);
    }, 0) / (sessions.length || 1);

    const avgAccuracy = sessions.reduce((sum, s) => {
        return sum + (s.accuracy || 0);
    }, 0) / (sessions.length || 1);

    return (
        <div>
            <div className="stats-grid">
                <StatsCard
                    title="Total Sesiones"
                    value={sessions.length || 0}
                    trend="🧠 Juegos Completados"
                    gradient="gradient-2"
                />
                <StatsCard
                    title="Accuracy Promedio"
                    value={`${avgAccuracy.toFixed(1)}%`}
                    trend="🎯 Precisión Global"
                    gradient="gradient-1"
                />
                <StatsCard
                    title="Score IA Promedio"
                    value={`${avgAIScore.toFixed(1)}/10`}
                    trend="⭐ Evaluación"
                    gradient="gradient-3"
                />
            </div>

            <div className="table-container">
                <h3>🧠 Últimas Sesiones - Con Métricas de IA</h3>
                <div className="info-banner">
                    <strong>💡 Métricas de IA:</strong> Score (0-10), Decisión (↑ Subir, ═ Mantener, ↓ Bajar), Memoria/Velocidad/Precisión (Low/Medium/High)
                </div>
                {sessionsLoading ? (
                    <div className="loading">Cargando...</div>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Usuario</th>
                                <th>Dificultad</th>
                                <th>Grid</th>
                                <th>Accuracy</th>
                                <th>Tiempo</th>
                                <th>Estado</th>
                                <th>Score IA</th>
                                <th>Decisión</th>
                                <th>Memoria</th>
                                <th>Velocidad</th>
                                <th>Precisión</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sessions.map(session => {
                                const ai = session.ai_metrics || {};
                                return (
                                    <tr key={session.session_id}>
                                        <td>{session.session_id}</td>
                                        <td>{session.user_id}</td>
                                        <td><span className="badge">{session.difficulty_level}</span></td>
                                        <td>{session.grid_size}</td>
                                        <td>{session.accuracy?.toFixed(1) || '0.0'}%</td>
                                        <td>{session.elapsed_time?.toFixed(1) || '0.0'}s</td>
                                        <td>{session.completion_status}</td>
                                        <td><strong>{ai.overall_score || '-'}</strong>/10</td>
                                        <td>{formatDecision(ai.adjustment_decision)}</td>
                                        <td>{formatMetricBadge(ai.memory)}</td>
                                        <td>{formatMetricBadge(ai.speed)}</td>
                                        <td>{formatMetricBadge(ai.accuracy)}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="table-container">
                <h3>⚙️ Configuraciones Actuales - Con Ajustes Progresivos</h3>
                <div className="info-banner">
                    <strong>🎯 Consecutive Maintains:</strong> Número de sesiones seguidas en el mismo nivel (activa micro-ajustes a partir de 3)
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Usuario</th>
                            <th>Dificultad</th>
                            <th>Grid</th>
                            <th>Pares</th>
                            <th>Tiempo Límite</th>
                            <th>Tiempo Memoria</th>
                            <th>Consecutive Maintains</th>
                        </tr>
                    </thead>
                    <tbody>
                        {configs.map(config => {
                            const maintainsColor =
                                (config.consecutive_maintains || 0) >= 3 ? '#ff6b6b' :
                                    (config.consecutive_maintains || 0) >= 2 ? '#ffd93d' : '#888';

                            return (
                                <tr key={config.user_id}>
                                    <td>{config.user_id}</td>
                                    <td><span className="badge">{config.difficulty_label}</span></td>
                                    <td>{config.grid_size}</td>
                                    <td>{config.total_pairs}</td>
                                    <td>{config.time_limit}s</td>
                                    <td>{config.memorization_time}s</td>
                                    <td style={{ color: maintainsColor, fontWeight: 'bold' }}>
                                        {config.consecutive_maintains || 0}
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default MemoryGameTab;
