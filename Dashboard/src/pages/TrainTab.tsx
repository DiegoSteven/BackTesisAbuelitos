import { useQuery } from '@tanstack/react-query';
import { getTrainSessions, getTrainConfigs } from '../services/api';
import StatsCard from '../components/Stats/StatsCard';

interface TrainSession {
    id: number;
    user_id: number;
    train_speed: number;
    color_count: number;
    correct_routing: number;
    wrong_routing: number;
    crash_count?: number;
    completion_status: string;
    timestamp: string;
}

interface TrainConfig {
    user_id: number;
    train_speed: number;
    spawn_rate: number;
    total_trains: number;
    color_count: number;
    difficulty_label: string;
}

const TrainTab = () => {
    const { data: sessionsData, isLoading: sessionsLoading } = useQuery({
        queryKey: ['train-sessions'],
        queryFn: async () => {
            const res = await getTrainSessions();
            return res.data.sessions as TrainSession[];
        },
    });

    const { data: configsData } = useQuery({
        queryKey: ['train-configs'],
        queryFn: async () => {
            const res = await getTrainConfigs();
            return res.data.configs as TrainConfig[];
        },
    });

    const sessions = sessionsData || [];
    const configs = configsData || [];

    const totalCorrect = sessions.reduce((sum, s) => sum + (s.correct_routing || 0), 0);
    const totalIncorrect = sessions.reduce((sum, s) => sum + (s.wrong_routing || 0), 0);
    const totalCrashes = sessions.reduce((sum, s) => sum + (s.crash_count || 0), 0);
    const accuracy = (totalCorrect / (totalCorrect + totalIncorrect || 1)) * 100;

    return (
        <div>
            <div className="stats-grid">
                <StatsCard
                    title="Total Sesiones"
                    value={sessions.length}
                    trend="🚂 Trenes"
                    gradient="gradient-1"
                />
                <StatsCard
                    title="Choques Totales"
                    value={totalCrashes}
                    trend="⚠️ Alertas"
                    gradient="gradient-2"
                />
                <StatsCard
                    title="Precisión Global"
                    value={`${isNaN(accuracy) ? '0.0' : accuracy.toFixed(1)}%`}
                    trend="🎯 Accuracy"
                    gradient="gradient-3"
                />
            </div>

            <div className="table-container">
                <h3>🚂 Últimas Sesiones (Trenes)</h3>
                <div className="info-banner">
                    <strong>💡 Métricas Clave:</strong> Velocidad (m/s), Colores (Complejidad), Choques (Atención)
                </div>
                {sessionsLoading ? (
                    <div className="loading">Cargando...</div>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Usuario</th>
                                <th>Velocidad</th>
                                <th>Colores</th>
                                <th>Aciertos</th>
                                <th>Errores</th>
                                <th>Choques</th>
                                <th>Estado</th>
                                <th>Precisión</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sessions.map(session => {
                                const totalAttempts = (session.correct_routing || 0) + (session.wrong_routing || 0);
                                const sessionAccuracy = totalAttempts > 0
                                    ? (session.correct_routing / totalAttempts) * 100
                                    : 0;

                                return (
                                    <tr key={session.id}>
                                        <td>{session.id}</td>
                                        <td>{session.user_id}</td>
                                        <td>{session.train_speed?.toFixed(1) || '0.0'}</td>
                                        <td>{session.color_count}</td>
                                        <td>{session.correct_routing || 0}</td>
                                        <td>{session.wrong_routing || 0}</td>
                                        <td style={{ color: (session.crash_count || 0) > 0 ? '#ff6b6b' : 'inherit', fontWeight: (session.crash_count || 0) > 0 ? 'bold' : 'normal' }}>
                                            {session.crash_count || 0}
                                        </td>
                                        <td><span className={`badge`}>{session.completion_status}</span></td>
                                        <td>{sessionAccuracy.toFixed(1)}%</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>

            <div className="table-container">
                <h3>⚙️ Configuraciones Actuales (Trenes)</h3>
                <div className="info-banner">
                    <strong>🎯 Adaptación:</strong> La velocidad y tasa de aparición se ajustan según el desempeño.
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Usuario</th>
                            <th>Dificultad</th>
                            <th>Velocidad</th>
                            <th>Spawn Rate</th>
                            <th>Total Trenes</th>
                            <th>Colores</th>
                        </tr>
                    </thead>
                    <tbody>
                        {configs.map(config => (
                            <tr key={config.user_id}>
                                <td>{config.user_id}</td>
                                <td><span className="badge">{config.difficulty_label}</span></td>
                                <td>{config.train_speed.toFixed(1)}</td>
                                <td>{config.spawn_rate.toFixed(1)}</td>
                                <td>{config.total_trains}</td>
                                <td>{config.color_count}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TrainTab;
