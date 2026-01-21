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
    abecedario: { total_sesiones: number; palabras_completadas: number; tiempo_promedio: number; nivel_alcanzado: string };
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
    const [expandedSessions, setExpandedSessions] = useState<Set<string>>(new Set());
    const [expandedLevels, setExpandedLevels] = useState<Set<string>>(new Set());

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
                case 'abecedario': 
                    res = await getUserAbecedarioSessions(selectedUser);
                    // El backend devuelve 'sesiones' para Abecedario, no 'sessions'
                    return res.data.sesiones || [];
                case 'paseo': 
                    res = await getUserPaseoSessions(selectedUser);
                    // El backend ahora devuelve 'sesiones' agrupadas, no 'sessions'
                    return res.data.sesiones || [];
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
                                    { label: 'Palabras Completadas', value: userStatsData.abecedario.palabras_completadas },
                                    { label: 'Tiempo Promedio', value: `${userStatsData.abecedario.tiempo_promedio.toFixed(1)}s` },
                                    { label: 'Nivel Alcanzado', value: userStatsData.abecedario.nivel_alcanzado.toUpperCase() }
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
                                    selectedGame === 'abecedario' || selectedGame === 'paseo' ? (
                                        // Vista jerárquica para Abecedario y Paseo: Sesión -> Niveles -> Palabras/Partidas
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
                                            {gameSessions.map((sesion: any) => {
                                                const sesionKey = sesion.fecha;
                                                const isSessionExpanded = expandedSessions.has(sesionKey);
                                                const isPaseo = selectedGame === 'paseo';
                                                
                                                return (
                                                    <div key={sesionKey} style={{
                                                        background: '#1a1d2e',
                                                        borderRadius: '12px',
                                                        border: '1px solid #2c2e33',
                                                        overflow: 'hidden'
                                                    }}>
                                                        {/* Header de Sesión */}
                                                        <div
                                                            onClick={() => {
                                                                const newExpanded = new Set(expandedSessions);
                                                                if (isSessionExpanded) {
                                                                    newExpanded.delete(sesionKey);
                                                                } else {
                                                                    newExpanded.add(sesionKey);
                                                                }
                                                                setExpandedSessions(newExpanded);
                                                            }}
                                                            style={{
                                                                padding: '20px',
                                                                cursor: 'pointer',
                                                                background: isSessionExpanded ? `linear-gradient(90deg, ${isPaseo ? 'rgba(252, 196, 25, 0.1)' : 'rgba(51, 154, 240, 0.1)'} 0%, transparent 100%)` : 'transparent',
                                                                borderLeft: isSessionExpanded ? `4px solid ${isPaseo ? '#fcc419' : '#339af0'}` : '4px solid transparent',
                                                                display: 'flex',
                                                                justifyContent: 'space-between',
                                                                alignItems: 'center',
                                                                transition: 'all 0.2s ease'
                                                            }}
                                                        >
                                                            <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flex: 1 }}>
                                                                <div style={{ fontSize: '1.5em' }}>
                                                                    {isSessionExpanded ? '▼' : '▶'}
                                                                </div>
                                                                <div>
                                                                    <div style={{ fontWeight: 'bold', fontSize: '1.2em', color: isPaseo ? '#fcc419' : '#339af0' }}>
                                                                        📅 Sesión: {sesion.fecha}
                                                                    </div>
                                                                    <div style={{ fontSize: '0.9em', color: '#888', marginTop: '5px' }}>
                                                                        {isPaseo ? (
                                                                            <>
                                                                                {sesion.resumen.total_partidas} partidas • {sesion.resumen.victorias} victorias • {sesion.resumen.derrotas} derrotas • {sesion.resumen.precision_promedio.toFixed(1)}% precisión
                                                                            </>
                                                                        ) : (
                                                                            <>
                                                                                {sesion.resumen.total_palabras} palabras • {sesion.resumen.palabras_completadas} completadas • {sesion.resumen.tiempo_total.toFixed(1)}s total
                                                                            </>
                                                                        )}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div style={{
                                                                padding: '8px 15px',
                                                                background: isPaseo ? 'rgba(252, 196, 25, 0.2)' : 'rgba(51, 154, 240, 0.2)',
                                                                borderRadius: '20px',
                                                                fontSize: '0.9em',
                                                                color: isPaseo ? '#fcc419' : '#339af0'
                                                            }}>
                                                                {isPaseo ? (
                                                                    <>🎯 {sesion.resumen.total_aciertos} aciertos</>
                                                                ) : (
                                                                    <>{((sesion.resumen.palabras_completadas / sesion.resumen.total_palabras) * 100).toFixed(0)}% completado</>
                                                                )}
                                                            </div>
                                                        </div>
                                                        
                                                        {/* Niveles (colapsable) */}
                                                        {isSessionExpanded && (
                                                            <div style={{ padding: '10px 20px 20px 60px' }}>
                                                                {sesion.niveles.map((nivel: any) => {
                                                                    const levelKey = `${sesionKey}-${nivel.nivel}`;
                                                                    const isLevelExpanded = expandedLevels.has(levelKey);
                                                                    
                                                                    return (
                                                                        <div key={levelKey} style={{
                                                                            marginBottom: '10px',
                                                                            background: '#232635',
                                                                            borderRadius: '8px',
                                                                            border: '1px solid #2c2e33'
                                                                        }}>
                                                                            {/* Header de Nivel */}
                                                                            <div
                                                                                onClick={() => {
                                                                                    const newExpanded = new Set(expandedLevels);
                                                                                    if (isLevelExpanded) {
                                                                                        newExpanded.delete(levelKey);
                                                                                    } else {
                                                                                        newExpanded.add(levelKey);
                                                                                    }
                                                                                    setExpandedLevels(newExpanded);
                                                                                }}
                                                                                style={{
                                                                                    padding: '15px',
                                                                                    cursor: 'pointer',
                                                                                    display: 'flex',
                                                                                    justifyContent: 'space-between',
                                                                                    alignItems: 'center',
                                                                                    transition: 'all 0.2s ease'
                                                                                }}
                                                                            >
                                                                                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                                                                                    <div style={{ fontSize: '1.2em' }}>
                                                                                        {isLevelExpanded ? '▼' : '▶'}
                                                                                    </div>
                                                                                    <span className="badge" style={{
                                                                                        background: nivel.nivel === 'dificil' ? '#ff6b6b' :
                                                                                                   nivel.nivel === 'intermedio' ? '#ffd93d' : '#51cf66',
                                                                                        padding: '5px 12px',
                                                                                        borderRadius: '5px',
                                                                                        fontWeight: 'bold',
                                                                                        fontSize: '0.9em'
                                                                                    }}>
                                                                                        {nivel.nivel.toUpperCase()}
                                                                                    </span>
                                                                                    <span style={{ color: '#aaa' }}>
                                                                                        {isPaseo ? (
                                                                                            <>{nivel.partidas.length} partida{nivel.partidas.length !== 1 ? 's' : ''}</>
                                                                                        ) : (
                                                                                            <>{nivel.palabras.length} palabra{nivel.palabras.length !== 1 ? 's' : ''}</>
                                                                                        )}
                                                                                    </span>
                                                                                </div>
                                                                                <div style={{ 
                                                                                    fontSize: '0.95em', 
                                                                                    color: isPaseo ? '#fcc419' : '#339af0',
                                                                                    fontWeight: '600',
                                                                                    padding: '5px 12px',
                                                                                    background: isPaseo ? 'rgba(252, 196, 25, 0.15)' : 'rgba(51, 154, 240, 0.15)',
                                                                                    borderRadius: '8px'
                                                                                }}>
                                                                                    {isPaseo ? (
                                                                                        <>⏱️ {nivel.partidas.reduce((sum: number, p: any) => sum + (p.duracion || 0), 0).toFixed(1)}s</>
                                                                                    ) : (
                                                                                        <>⏱️ {nivel.palabras.reduce((sum: number, p: any) => sum + p.tiempo, 0).toFixed(1)}s</>
                                                                                    )}
                                                                                </div>
                                                                            </div>
                                                                            
                                                                            {/* Detalles del nivel */}
                                                                            {isLevelExpanded && (
                                                                                <div style={{ padding: '0 15px 15px 45px' }}>
                                                                                    <table style={{ width: '100%', fontSize: '0.9em' }}>
                                                                                        <thead>
                                                                                            <tr style={{ borderBottom: '1px solid #2c2e33' }}>
                                                                                                {isPaseo ? (
                                                                                                    <>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>ID</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Hora</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Duración</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Aciertos</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Errores</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Precisión</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Resultado</th>
                                                                                                    </>
                                                                                                ) : (
                                                                                                    <>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Palabra</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Hora</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Tiempo</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Errores</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Pistas</th>
                                                                                                        <th style={{ textAlign: 'left', padding: '10px', color: '#888' }}>Estado</th>
                                                                                                    </>
                                                                                                )}
                                                                                            </tr>
                                                                                        </thead>
                                                                                        <tbody>
                                                                                            {isPaseo ? (
                                                                                                nivel.partidas.map((partida: any, idx: number) => (
                                                                                                    <tr key={idx} style={{ borderBottom: '1px solid #1a1d2e' }}>
                                                                                                        <td style={{ padding: '10px' }}>
                                                                                                            <strong>#{partida.id}</strong>
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px', color: '#888' }}>
                                                                                                            {partida.hora}
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px' }}>
                                                                                                            {partida.duracion?.toFixed(1) || '-'}s
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px', color: '#51cf66' }}>
                                                                                                            {partida.aciertos}
                                                                                                        </td>
                                                                                                        <td style={{ 
                                                                                                            padding: '10px',
                                                                                                            color: partida.errores > 5 ? '#ff6b6b' : 'inherit'
                                                                                                        }}>
                                                                                                            {partida.errores}
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px' }}>
                                                                                                            {partida.precision?.toFixed(1) || '-'}%
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px' }}>
                                                                                                            <span style={{ 
                                                                                                                color: partida.resultado === 'victoria' ? '#51cf66' : '#ff6b6b',
                                                                                                                fontWeight: 'bold'
                                                                                                            }}>
                                                                                                                {partida.resultado === 'victoria' ? '✓ Victoria' : `✗ ${partida.razon_derrota || 'Derrota'}`}
                                                                                                            </span>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                ))
                                                                                            ) : (
                                                                                                nivel.palabras.map((palabra: any, idx: number) => (
                                                                                                    <tr key={idx} style={{ borderBottom: '1px solid #1a1d2e' }}>
                                                                                                        <td style={{ padding: '10px' }}>
                                                                                                            <strong>{palabra.palabra}</strong>
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px', color: '#888' }}>
                                                                                                            {palabra.hora}
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px' }}>
                                                                                                            {palabra.tiempo.toFixed(1)}s
                                                                                                        </td>
                                                                                                        <td style={{ 
                                                                                                            padding: '10px',
                                                                                                            color: palabra.errores > 2 ? '#ff6b6b' : 'inherit'
                                                                                                        }}>
                                                                                                            {palabra.errores}
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px' }}>
                                                                                                            {palabra.pistas}
                                                                                                        </td>
                                                                                                        <td style={{ padding: '10px' }}>
                                                                                                            <span style={{ 
                                                                                                                color: palabra.completado ? '#51cf66' : '#aaa'
                                                                                                            }}>
                                                                                                                {palabra.completado ? '✓ Completado' : '✗ Incompleto'}
                                                                                                            </span>
                                                                                                        </td>
                                                                                                    </tr>
                                                                                                ))
                                                                                            )}
                                                                                        </tbody>
                                                                                    </table>
                                                                                </div>
                                                                            )}
                                                                        </div>
                                                                    );
                                                                })}
                                                            </div>
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    ) : (
                                        // Vista de tabla para otros juegos
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
                                                        <tr key={session.id || session.session_id}>
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
                                    )
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
