import { useQuery } from '@tanstack/react-query';
import { getPaseoSessions } from '../services/api';
import StatsCard from '../components/Stats/StatsCard';

interface PaseoSession {
    id: number;
    user_id: number;
    nivel_dificultad: string;
    esferas_rojas_atrapadas: number;
    meta_aciertos: number;
    precision: number;
    resultado: string;
    timestamp: string;
    recomendacion_siguiente?: string;
    tiempo_reaccion_promedio?: number;
    velocidad_esferas?: number;
}

const PaseoTab = () => {
    const { data: sessionsData, isLoading } = useQuery({
        queryKey: ['paseo-sessions'],
        queryFn: async () => {
            const res = await getPaseoSessions();
            return res.data.sessions as PaseoSession[];
        },
    });

    const sessions = sessionsData || [];
    const victories = sessions.filter(s => s.resultado === 'victoria').length;
    const avgPrecision = sessions.reduce((sum, s) => sum + (s.precision || 0), 0) / (sessions.length || 1);
    const avgReactionTime = sessions.reduce((sum, s) => sum + (s.tiempo_reaccion_promedio || 0), 0) / (sessions.length || 1);

    return (
        <div>
            <div className="stats-grid">
                <StatsCard
                    title="Victorias Totales"
                    value={victories}
                    trend="🏆 Logros"
                    gradient="gradient-1"
                />
                <StatsCard
                    title="Precisión Promedio"
                    value={`${avgPrecision.toFixed(1)}%`}
                    trend="🎯 Puntería"
                    gradient="gradient-2"
                />
                <StatsCard
                    title="Tiempo Reacción"
                    value={`${avgReactionTime.toFixed(2)}s`}
                    trend="⚡ Velocidad"
                    gradient="gradient-3"
                />
            </div>

            <div className="table-container">
                <h3>🚶 Últimas Sesiones (Paseo)</h3>
                <div className="info-banner">
                    <strong>💡 Análisis IA:</strong> La columna "Recomendación" muestra el plan de la IA para la siguiente sesión basado en el desempeño.
                </div>
                {isLoading ? (
                    <div className="loading">Cargando...</div>
                ) : (
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Usuario</th>
                                <th>Nivel</th>
                                <th>Velocidad</th>
                                <th>Aciertos/Meta</th>
                                <th>Precisión</th>
                                <th>T. Reacción</th>
                                <th>Resultado</th>
                                <th>Recomendación IA</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sessions.map(session => (
                                <tr key={session.id}>
                                    <td>{session.id}</td>
                                    <td>{session.user_id}</td>
                                    <td><span className="badge">{session.nivel_dificultad || '-'}</span></td>
                                    <td>{session.velocidad_esferas?.toFixed(1) || '-'}</td>
                                    <td>{session.esferas_rojas_atrapadas} / {session.meta_aciertos}</td>
                                    <td>{session.precision?.toFixed(1)}%</td>
                                    <td>{session.tiempo_reaccion_promedio?.toFixed(2) || '-'}s</td>
                                    <td>
                                        <span style={{
                                            color: session.resultado === 'victoria' ? '#51cf66' : '#ff6b6b',
                                            fontWeight: 'bold'
                                        }}>
                                            {session.resultado === 'victoria' ? '✓ Victoria' : '✗ Derrota'}
                                        </span>
                                    </td>
                                    <td style={{ fontSize: '0.9em', color: '#aaa' }}>
                                        {session.recomendacion_siguiente || '-'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
};

export default PaseoTab;
