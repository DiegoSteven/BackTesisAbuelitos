import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
    getUsers,
    getUserMemorySessions,
    getUserAbecedarioSessions,
    getUserPaseoSessions,
    getUserTrainSessions
} from '../services/api';
import api from '../services/api';

interface User {
    id: number;
    nombre: string;
    edad: number;
    genero: string;
}

interface UserStats {
    memoria: { total_sesiones: number; promedio_accuracy: number; sesiones_completadas: number };
    abecedario: { total_sesiones: number; palabras_completadas: number; tiempo_promedio: number };
    paseo: { total_sesiones: number; victorias: number; precision_promedio: number };
    trenes: { total_sesiones: number; total_aciertos: number; precision_promedio: number };
}

// Helper functions from MemoryGameTab
const formatMetricBadge = (metric?: string) => {
    if (!metric) return '-';
    const colors: Record<string, string> = {
        low: '#ff6b6b',
        medium: '#ffd93d',
        high: '#51cf66',
    };
    return (
        <span style={{ color: colors[metric] || '#fff', fontWeight: 'bold', fontSize: '0.9em' }}>
            ● {metric}
        </span>
    );
};

const formatDecision = (decision?: string) => {
    if (decision === 'increase') return <span style={{ color: '#51cf66', fontSize: '1.2em', fontWeight: 'bold' }}>↑ Subir</span>;
    if (decision === 'decrease') return <span style={{ color: '#ff6b6b', fontSize: '1.2em', fontWeight: 'bold' }}>↓ Bajar</span>;
    return <span style={{ color: '#ffd93d', fontSize: '1.2em', fontWeight: 'bold' }}>═ Mantener</span>;
};

const UsersTab = () => {
    const [selectedUser, setSelectedUser] = useState<number | null>(null);
    const [selectedGame, setSelectedGame] = useState<string | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);

    // Fetch Users
    const { data: usersData, isLoading: usersLoading } = useQuery({
        queryKey: ['users'],
        queryFn: async () => {
            const res = await getUsers();
            return res.data.users as User[];
        },
    });

    // Fetch Aggregated Stats for Selected User
    const { data: userStatsData, isLoading: statsLoading } = useQuery({
        queryKey: ['user-stats', selectedUser],
        queryFn: async () => {
            if (!selectedUser) return null;
            const res = await api.get(`/admin/user-stats/${selectedUser}`);
            return res.data.stats as UserStats;
        },
        enabled: !!selectedUser,
    });

    // Fetch Detailed Sessions when a Game is Selected
    const { data: gameSessions, isLoading: sessionsLoading } = useQuery({
        queryKey: ['user-game-sessions', selectedUser, selectedGame],
        queryFn: async () => {
            if (!selectedUser || !selectedGame) return [];
            let res;
            switch (selectedGame) {
                case 'memoria': res = await getUserMemorySessions(selectedUser); break;
                case 'abecedario': res = await getUserAbecedarioSessions(selectedUser); break;
                case 'paseo': res = await getUserPaseoSessions(selectedUser); break;
                case 'trenes': res = await getUserTrainSessions(selectedUser); break;
                default: return [];
            }
            return res.data.sessions;
        },
        enabled: !!selectedUser && !!selectedGame,
    });

    const users = usersData || [];
    const filteredUsers = users.filter(user =>
        user.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.id.toString().includes(searchTerm)
    );

    const handleUserSelect = (id: number) => {
        setSelectedUser(id);
        setSelectedGame(null);
    };

    const GameSummaryCard = ({ title, icon, stats, color, id }: { title: string, icon: any, stats: { label: string, value: string | number }[], color: string, id: string }) => {
        const [isHovered, setIsHovered] = useState(false);

        return (
            <div
                onClick={() => setSelectedGame(selectedGame === id ? null : id)}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                style={{
                    background: '#151722',
                    padding: '20px',
                    borderRadius: '16px',
                    cursor: 'pointer',
                    border: `2px solid ${selectedGame === id || isHovered ? color : '#2c2e33'}`,
                    boxShadow: selectedGame === id || isHovered ? `0 0 20px ${color}20` : 'none',
                    transform: isHovered ? 'translateX(5px)' : 'none',
                    transition: 'all 0.3s ease',
                    display: 'flex',
                    flexDirection: 'row',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    marginBottom: '15px',
                    width: '100%'
                }}
            >
                <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flex: 1 }}>
                    <div style={{
                        fontSize: '2.5em',
                        background: `${color}15`,
                        padding: '15px',
                        borderRadius: '12px',
                        color: color,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        width: '80px',
                        height: '80px',
                        flexShrink: 0
                    }}>
                        {icon}
                    </div>
                    <div style={{ flex: 1 }}>
                        <h3 style={{ margin: '0 0 10px 0', color: '#fff', fontSize: '1.4em', fontWeight: '600' }}>{title}</h3>
                        <div style={{ display: 'flex', gap: '30px', color: '#888', flexWrap: 'wrap' }}>
                            {stats.map((stat, index) => (
                                <div key={index} style={{ display: 'flex', flexDirection: 'column' }}>
                                    <span style={{ fontSize: '0.8em', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{stat.label}</span>
                                    <span style={{ color: '#eee', fontWeight: '500', fontSize: '1.1em' }}>{stat.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div style={{
                    color: color,
                    fontSize: '1.5em',
                    opacity: isHovered || selectedGame === id ? 1 : 0.3,
                    transition: 'all 0.3s ease',
                    transform: selectedGame === id ? 'rotate(180deg)' : 'rotate(0deg)'
                }}>
                    ▼
                </div>
            </div>
        );
    };

    return (
        <div className="users-tab" style={{
            display: 'grid',
            gridTemplateColumns: isSidebarOpen ? '300px 1fr' : '60px 1fr',
            gap: '20px',
            height: 'calc(100vh - 100px)',
            transition: 'grid-template-columns 0.3s ease'
        }}>
            {/* Users List Sidebar */}
            <div className="users-list-container" style={{
                display: 'flex',
                flexDirection: 'column',
                background: '#151722',
                borderRadius: '10px',
                position: 'relative',
                transition: 'all 0.3s ease',
                overflow: 'hidden'
            }}>
                <div style={{
                    padding: '20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    borderBottom: isSidebarOpen ? '1px solid #2c2e33' : 'none'
                }}>
                    {isSidebarOpen && <h3 style={{ margin: 0, whiteSpace: 'nowrap' }}>👥 Usuarios ({users.length})</h3>}
                    <button
                        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                        style={{
                            background: 'transparent',
                            border: 'none',
                            color: '#888',
                            cursor: 'pointer',
                            fontSize: '1.2em',
                            padding: '5px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            width: '100%'
                        }}
                    >
                        {isSidebarOpen ? '◀' : '▶'}
                    </button>
                </div>

                {isSidebarOpen && (
                    <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                        <input
                            type="text"
                            placeholder="🔍 Buscar..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px',
                                marginBottom: '15px',
                                borderRadius: '8px',
                                border: '1px solid #444',
                                background: '#2c2e33',
                                color: '#fff',
                                fontSize: '14px'
                            }}
                        />

                        <div className="users-list" style={{ flex: 1, overflowY: 'auto' }}>
                            {usersLoading ? (
                                <div style={{ textAlign: 'center', padding: '20px', color: '#888' }}>Cargando...</div>
                            ) : filteredUsers.length === 0 ? (
                                <div style={{ textAlign: 'center', padding: '20px', color: '#888' }}>
                                    {searchTerm ? 'No encontrado.' : 'Sin usuarios.'}
                                </div>
                            ) : (
                                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                                    {filteredUsers.map(user => (
                                        <li
                                            key={user.id}
                                            onClick={() => handleUserSelect(user.id)}
                                            style={{
                                                padding: '15px',
                                                borderBottom: '1px solid #333',
                                                cursor: 'pointer',
                                                background: selectedUser === user.id ? 'linear-gradient(90deg, rgba(81, 207, 102, 0.1) 0%, transparent 100%)' : 'transparent',
                                                borderLeft: selectedUser === user.id ? '4px solid #51cf66' : '4px solid transparent',
                                                borderRadius: '4px',
                                                marginBottom: '5px',
                                                transition: 'all 0.2s ease'
                                            }}
                                        >
                                            <div style={{ fontWeight: 'bold', fontSize: '1.1em', color: selectedUser === user.id ? '#51cf66' : '#eee' }}>{user.nombre}</div>
                                            <div style={{ fontSize: '0.85em', color: '#888', marginTop: '4px' }}>
                                                ID: {user.id} • {user.edad} años
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Main Content Area */}
            <div className="user-details" style={{ overflowY: 'auto', paddingRight: '10px' }}>
                {!selectedUser ? (
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        height: '100%',
                        color: '#666',
                        background: '#151722',
                        borderRadius: '10px',
                        border: '2px dashed #333'
                    }}>
                        <div style={{ fontSize: '3em', marginBottom: '20px', opacity: 0.5 }}>👈</div>
                        <h3>Selecciona un usuario</h3>
                        <p>Haz clic en un usuario de la lista para ver sus estadísticas.</p>
                    </div>
                ) : statsLoading ? (
                    <div className="loading">Cargando estadísticas detalladas...</div>
                ) : userStatsData ? (
                    <div>
                        {/* User Header */}
                        <div style={{
                            background: 'linear-gradient(135deg, #2c2e33 0%, #151722 100%)',
                            padding: '25px',
                            borderRadius: '15px',
                            marginBottom: '30px',
                            borderLeft: '5px solid #51cf66',
                            boxShadow: '0 4px 15px rgba(0,0,0,0.2)'
                        }}>
                            <h2 style={{ margin: 0, fontSize: '2em' }}>{users.find(u => u.id === selectedUser)?.nombre}</h2>
                            <div style={{ marginTop: '10px', color: '#aaa' }}>
                                ID: {selectedUser} • Edad: {users.find(u => u.id === selectedUser)?.edad} • Género: {users.find(u => u.id === selectedUser)?.genero}
                            </div>
                        </div>

                        {/* Game Summary Cards List (Vertical) */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '30px' }}>
                            <GameSummaryCard
                                id="memoria"
                                title="Juego de Memoria"
                                icon="🧠"
                                color="#51cf66"
                                stats={[
                                    { label: 'Total Sesiones', value: userStatsData.memoria.total_sesiones },
                                    { label: 'Accuracy Promedio', value: `${userStatsData.memoria.promedio_accuracy.toFixed(1)}%` },
                                    { label: 'Completadas', value: userStatsData.memoria.sesiones_completadas }
                                ]}
                            />
                            <GameSummaryCard
                                id="abecedario"
                                title="Abecedario"
                                icon="🔤"
                                color="#339af0"
                                stats={[
                                    { label: 'Total Sesiones', value: userStatsData.abecedario.total_sesiones },
                                    { label: 'Completadas', value: userStatsData.abecedario.palabras_completadas },
                                    { label: 'Tiempo Promedio', value: `${userStatsData.abecedario.tiempo_promedio.toFixed(1)}s` }
                                ]}
                            />
                            <GameSummaryCard
                                id="trenes"
                                title="Trenes"
                                icon="🚂"
                                color="#ff6b6b"
                                stats={[
                                    { label: 'Total Sesiones', value: userStatsData.trenes.total_sesiones },
                                    { label: 'Aciertos Total', value: userStatsData.trenes.total_aciertos },
                                    { label: 'Precisión', value: `${userStatsData.trenes.precision_promedio.toFixed(1)}%` }
                                ]}
                            />
                            <GameSummaryCard
                                id="paseo"
                                title="Paseo"
                                icon="🚶"
                                color="#fcc419"
                                stats={[
                                    { label: 'Total Sesiones', value: userStatsData.paseo.total_sesiones },
                                    { label: 'Victorias', value: userStatsData.paseo.victorias },
                                    { label: 'Precisión Promedio', value: `${userStatsData.paseo.precision_promedio.toFixed(1)}%` }
                                ]}
                            />
                        </div>

                        {/* Detailed Session View */}
                        {selectedGame && (
                            <div className="game-details-section fade-in" style={{ background: '#151722', padding: '20px', borderRadius: '15px', marginBottom: '30px' }}>
                                <h3 style={{
                                    color: selectedGame === 'memoria' ? '#51cf66' :
                                        selectedGame === 'abecedario' ? '#339af0' :
                                            selectedGame === 'paseo' ? '#fcc419' : '#ff6b6b',
                                    borderBottom: '1px solid #333',
                                    paddingBottom: '15px',
                                    marginBottom: '20px',
                                    textTransform: 'capitalize'
                                }}>
                                    Historial de Sesiones: {selectedGame}
                                </h3>

                                {sessionsLoading ? (
                                    <div className="loading">Cargando sesiones...</div>
                                ) : gameSessions && gameSessions.length > 0 ? (
                                    <div className="table-container">
                                        <table>
                                            <thead>
                                                {selectedGame === 'memoria' && (
                                                    <tr>
                                                        <th>ID</th>
                                                        <th>Dificultad</th>
                                                        <th>Grid</th>
                                                        <th>Accuracy</th>
                                                        <th>Tiempo</th>
                                                        <th>Estado</th>
                                                        <th>Score IA</th>
                                                        <th>Decisión</th>
                                                        <th>Métricas</th>
                                                    </tr>
                                                )}
                                                {selectedGame === 'abecedario' && (
                                                    <tr>
                                                        <th>ID</th>
                                                        <th>Nivel</th>
                                                        <th>Palabra</th>
                                                        <th>Tiempo</th>
                                                        <th>Errores</th>
                                                        <th>Pistas</th>
                                                        <th>Estado</th>
                                                    </tr>
                                                )}
                                                {selectedGame === 'paseo' && (
                                                    <tr>
                                                        <th>ID</th>
                                                        <th>Nivel</th>
                                                        <th>Aciertos</th>
                                                        <th>Precisión</th>
                                                        <th>Resultado</th>
                                                    </tr>
                                                )}
                                                {selectedGame === 'trenes' && (
                                                    <tr>
                                                        <th>ID</th>
                                                        <th>Velocidad</th>
                                                        <th>Colores</th>
                                                        <th>Aciertos</th>
                                                        <th>Choques</th>
                                                        <th>Estado</th>
                                                    </tr>
                                                )}
                                            </thead>
                                            <tbody>
                                                {gameSessions.map((session: any) => (
                                                    <tr key={session.id || session.session_id} style={
                                                        selectedGame === 'abecedario' && session.cambio_nivel ? {
                                                            backgroundColor: 'rgba(81, 207, 102, 0.1)',
                                                            borderLeft: '4px solid #51cf66'
                                                        } : {}
                                                    }>
                                                        {selectedGame === 'memoria' && (
                                                            <>
                                                                <td>{session.session_id}</td>
                                                                <td><span className="badge">{session.difficulty_level}</span></td>
                                                                <td>{session.grid_size}</td>
                                                                <td>{session.accuracy?.toFixed(1)}%</td>
                                                                <td>{session.elapsed_time?.toFixed(1)}s</td>
                                                                <td>{session.completion_status}</td>
                                                                <td><strong>{session.ai_metrics?.overall_score || '-'}</strong>/10</td>
                                                                <td>{formatDecision(session.ai_metrics?.adjustment_decision)}</td>
                                                                <td>
                                                                    <div style={{ display: 'flex', gap: '5px', fontSize: '0.8em' }}>
                                                                        {formatMetricBadge(session.ai_metrics?.memory)}
                                                                        {formatMetricBadge(session.ai_metrics?.speed)}
                                                                    </div>
                                                                </td>
                                                            </>
                                                        )}
                                                        {selectedGame === 'abecedario' && (
                                                            <>
                                                                <td>{session.id}</td>
                                                                <td>
                                                                    <span className="badge">{session.nivel_jugado || 'facil'}</span>
                                                                    {session.cambio_nivel && <span style={{ marginLeft: '5px' }}>🆙</span>}
                                                                </td>
                                                                <td><strong>{session.palabra_objetivo}</strong></td>
                                                                <td>{session.tiempo_resolucion?.toFixed(1)}s</td>
                                                                <td style={{ color: session.cantidad_errores > 2 ? '#ff6b6b' : 'inherit' }}>{session.cantidad_errores}</td>
                                                                <td>{session.pistas_usadas}</td>
                                                                <td>
                                                                    <span style={{ color: session.completado ? '#51cf66' : '#aaa' }}>
                                                                        {session.completado ? 'Completado' : 'Incompleto'}
                                                                    </span>
                                                                </td>
                                                            </>
                                                        )}
                                                        {selectedGame === 'paseo' && (
                                                            <>
                                                                <td>{session.id}</td>
                                                                <td><span className="badge">{session.nivel_dificultad}</span></td>
                                                                <td>{session.esferas_rojas_atrapadas}</td>
                                                                <td>{session.precision?.toFixed(1)}%</td>
                                                                <td>
                                                                    <span style={{ color: session.resultado === 'victoria' ? '#51cf66' : '#ff6b6b', fontWeight: 'bold' }}>
                                                                        {session.resultado === 'victoria' ? '✓ Victoria' : '✗ Derrota'}
                                                                    </span>
                                                                </td>
                                                                <td style={{ fontSize: '0.9em', color: '#aaa' }}>{session.recomendacion_siguiente || '-'}</td>
                                                            </>
                                                        )}
                                                        {selectedGame === 'trenes' && (
                                                            <>
                                                                <td>{session.id}</td>
                                                                <td>{session.train_speed?.toFixed(1)}</td>
                                                                <td>{session.color_count}</td>
                                                                <td>{session.correct_routing}</td>
                                                                <td style={{ color: (session.crash_count || 0) > 0 ? '#ff6b6b' : 'inherit', fontWeight: (session.crash_count || 0) > 0 ? 'bold' : 'normal' }}>
                                                                    {session.crash_count || 0}
                                                                </td>
                                                                <td><span className="badge">{session.completion_status}</span></td>
                                                            </>
                                                        )}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                ) : (
                                    <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                                        No hay sesiones registradas para este juego.
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                ) : (
                    <div>No hay datos disponibles.</div>
                )}
            </div>
        </div>
    );
};

export default UsersTab;
