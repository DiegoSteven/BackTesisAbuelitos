import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getUsers } from '../services/api';
import api from '../services/api'; // Direct import for dynamic query
import StatsCard from '../components/Stats/StatsCard';

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

const UsersTab = () => {
    const [selectedUser, setSelectedUser] = useState<number | null>(null);
    const [searchTerm, setSearchTerm] = useState('');

    const { data: usersData, isLoading: usersLoading } = useQuery({
        queryKey: ['users'],
        queryFn: async () => {
            const res = await getUsers();
            return res.data.users as User[];
        },
    });

    const { data: userStatsData, isLoading: statsLoading } = useQuery({
        queryKey: ['user-stats', selectedUser],
        queryFn: async () => {
            if (!selectedUser) return null;
            const res = await api.get(`/admin/user-stats/${selectedUser}`);
            return res.data.stats as UserStats;
        },
        enabled: !!selectedUser,
    });

    const users = usersData || [];
    const filteredUsers = users.filter(user =>
        user.nombre.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.id.toString().includes(searchTerm)
    );

    return (
        <div className="users-tab" style={{ display: 'grid', gridTemplateColumns: '300px 1fr', gap: '20px', height: 'calc(100vh - 100px)' }}>
            <div className="users-list-container" style={{ display: 'flex', flexDirection: 'column', background: '#1a1b1e', padding: '20px', borderRadius: '10px' }}>
                <h3 style={{ marginBottom: '15px' }}>👥 Usuarios ({users.length})</h3>
                <input
                    type="text"
                    placeholder="🔍 Buscar por nombre o ID..."
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
                        <div style={{ textAlign: 'center', padding: '20px', color: '#888' }}>Cargando usuarios...</div>
                    ) : filteredUsers.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '20px', color: '#888' }}>
                            {searchTerm ? 'No se encontraron usuarios.' : 'No hay usuarios registrados.'}
                        </div>
                    ) : (
                        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                            {filteredUsers.map(user => (
                                <li
                                    key={user.id}
                                    onClick={() => setSelectedUser(user.id)}
                                    style={{
                                        padding: '15px',
                                        borderBottom: '1px solid #333',
                                        cursor: 'pointer',
                                        background: selectedUser === user.id ? 'linear-gradient(90deg, rgba(81, 207, 102, 0.2) 0%, transparent 100%)' : 'transparent',
                                        borderLeft: selectedUser === user.id ? '4px solid #51cf66' : '4px solid transparent',
                                        borderRadius: '4px',
                                        marginBottom: '5px',
                                        transition: 'all 0.2s ease'
                                    }}
                                >
                                    <div style={{ fontWeight: 'bold', fontSize: '1.1em', color: selectedUser === user.id ? '#51cf66' : '#eee' }}>{user.nombre}</div>
                                    <div style={{ fontSize: '0.85em', color: '#888', marginTop: '4px' }}>
                                        ID: {user.id} • {user.edad} años • {user.genero}
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
            </div>

            <div className="user-details" style={{ overflowY: 'auto', paddingRight: '10px' }}>
                {!selectedUser ? (
                    <div style={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        height: '100%',
                        color: '#666',
                        background: '#1a1b1e',
                        borderRadius: '10px',
                        border: '2px dashed #333'
                    }}>
                        <div style={{ fontSize: '3em', marginBottom: '20px', opacity: 0.5 }}>👈</div>
                        <h3>Selecciona un usuario</h3>
                        <p>Haz clic en un usuario de la lista para ver sus estadísticas completas.</p>
                    </div>
                ) : statsLoading ? (
                    <div className="loading">Cargando estadísticas detalladas...</div>
                ) : userStatsData ? (
                    <div>
                        <div style={{
                            background: 'linear-gradient(135deg, #2c2e33 0%, #1a1b1e 100%)',
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

                        <h3 style={{ color: '#51cf66', borderBottom: '1px solid #333', paddingBottom: '10px', marginBottom: '20px' }}>🧠 Memoria</h3>
                        <div className="stats-grid" style={{ marginBottom: '30px' }}>
                            <StatsCard title="Sesiones" value={userStatsData.memoria.total_sesiones} trend="Total" gradient="gradient-1" />
                            <StatsCard title="Precisión" value={`${userStatsData.memoria.promedio_accuracy.toFixed(1)}%`} trend="Promedio" gradient="gradient-2" />
                            <StatsCard title="Completadas" value={userStatsData.memoria.sesiones_completadas} trend="Sesiones" gradient="gradient-3" />
                        </div>

                        <h3 style={{ color: '#339af0', borderBottom: '1px solid #333', paddingBottom: '10px', marginBottom: '20px' }}>🔤 Abecedario</h3>
                        <div className="stats-grid" style={{ marginBottom: '30px' }}>
                            <StatsCard title="Sesiones" value={userStatsData.abecedario.total_sesiones} trend="Total" gradient="gradient-1" />
                            <StatsCard title="Palabras" value={userStatsData.abecedario.palabras_completadas} trend="Completadas" gradient="gradient-2" />
                            <StatsCard title="Tiempo" value={`${userStatsData.abecedario.tiempo_promedio.toFixed(1)}s`} trend="Promedio" gradient="gradient-3" />
                        </div>

                        <h3 style={{ color: '#fcc419', borderBottom: '1px solid #333', paddingBottom: '10px', marginBottom: '20px' }}>🚶 Paseo</h3>
                        <div className="stats-grid" style={{ marginBottom: '30px' }}>
                            <StatsCard title="Sesiones" value={userStatsData.paseo.total_sesiones} trend="Total" gradient="gradient-1" />
                            <StatsCard title="Victorias" value={userStatsData.paseo.victorias} trend="Ganadas" gradient="gradient-2" />
                            <StatsCard title="Precisión" value={`${userStatsData.paseo.precision_promedio.toFixed(1)}%`} trend="Promedio" gradient="gradient-3" />
                        </div>

                        <h3 style={{ color: '#ff6b6b', borderBottom: '1px solid #333', paddingBottom: '10px', marginBottom: '20px' }}>🚂 Trenes</h3>
                        <div className="stats-grid" style={{ marginBottom: '30px' }}>
                            <StatsCard title="Sesiones" value={userStatsData.trenes.total_sesiones} trend="Total" gradient="gradient-1" />
                            <StatsCard title="Aciertos" value={userStatsData.trenes.total_aciertos} trend="Total" gradient="gradient-2" />
                            <StatsCard title="Precisión" value={`${userStatsData.trenes.precision_promedio.toFixed(1)}%`} trend="Global" gradient="gradient-3" />
                        </div>
                    </div>
                ) : (
                    <div>No hay datos disponibles.</div>
                )}
            </div>
        </div>
    );
};

export default UsersTab;
