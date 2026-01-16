import { useQuery } from '@tanstack/react-query';
import { getAbecedarioSessions } from '../services/api';
import StatsCard from '../components/Stats/StatsCard';

interface AbecedarioSession {
    id: number;
    user_id: number;
    palabra_objetivo: string;
    tiempo_resolucion: number;
    cantidad_errores: number;
    pistas_usadas: number;
    completado: boolean;
    timestamp: string;
    nivel_jugado?: string;
    cambio_nivel?: boolean;
}

const AbecedarioTab = () => {
    const { data: sessionsData, isLoading } = useQuery({
        queryKey: ['abecedario-sessions'],
        queryFn: async () => {
            const res = await getAbecedarioSessions();
            return res.data.sessions as AbecedarioSession[];
        },
    });

    const sessions = sessionsData || [];
    const completedCount = sessions.filter(s => s.completado).length;
    const avgErrors = sessions.reduce((sum, s) => sum + s.cantidad_errores, 0) / (sessions.length || 1);

    // Calculate Efficiency: (Length / (Length + Errors + Hints)) * 100 roughly, or just Time/Word Length
    // Let's use Time per Character as a speed metric
    const avgTimePerChar = sessions.reduce((sum, s) => {
        const len = s.palabra_objetivo?.length || 5;
        return sum + ((s.tiempo_resolucion || 0) / len);
    }, 0) / (sessions.length || 1);

    return (
        <div>
            <div className="stats-grid">
                <StatsCard
                    title="Palabras Completadas"
                    value={completedCount}
                    trend="🔤 Total"
                    gradient="gradient-3"
                />
                <StatsCard
                    title="Promedio Errores"
                    value={avgErrors.toFixed(1)}
                    trend="❌ Por sesión"
                    gradient="gradient-2"
                />
                <StatsCard
                    title="Velocidad Media"
                    value={`${avgTimePerChar.toFixed(1)}s`}
                    trend="⚡ Segundos/Letra"
                    gradient="gradient-1"
                />
            </div>

            <div className="table-container">
                <h3>🔤 Últimas Sesiones (Abecedario)</h3>
                <div className="info-banner">
                    <strong>💡 Progresión:</strong> Las filas resaltadas indican un cambio de nivel automático por la IA.
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
                                <th>Palabra</th>
                                <th>Tiempo</th>
                                <th>Errores</th>
                                <th>Pistas</th>
                                <th>Estado</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sessions.map(session => (
                                <tr key={session.id} style={{
                                    backgroundColor: session.cambio_nivel ? 'rgba(81, 207, 102, 0.1)' : 'transparent',
                                    borderLeft: session.cambio_nivel ? '4px solid #51cf66' : 'none'
                                }}>
                                    <td>{session.id}</td>
                                    <td>{session.user_id}</td>
                                    <td>
                                        <span className="badge">{session.nivel_jugado || 'facil'}</span>
                                        {session.cambio_nivel && <span style={{ marginLeft: '5px', fontSize: '0.8em' }}>🆙</span>}
                                    </td>
                                    <td><strong>{session.palabra_objetivo}</strong></td>
                                    <td>{session.tiempo_resolucion?.toFixed(1) || '0.0'}s</td>
                                    <td style={{ color: session.cantidad_errores > 2 ? '#ff6b6b' : 'inherit' }}>{session.cantidad_errores}</td>
                                    <td>{session.pistas_usadas}</td>
                                    <td>
                                        <span style={{ color: session.completado ? '#51cf66' : '#aaa' }}>
                                            {session.completado ? 'Completado' : 'Incompleto'}
                                        </span>
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

export default AbecedarioTab;
