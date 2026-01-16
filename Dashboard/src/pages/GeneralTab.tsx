import { useQuery } from '@tanstack/react-query';
import { getStats } from '../services/api';
import StatsCard from '../components/Stats/StatsCard';
import {
    Chart as ChartJS,
    ArcElement,
    Tooltip,
    Legend,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    PointElement,
    LineElement,
    Filler
} from 'chart.js';
import { Pie, Bar, Line } from 'react-chartjs-2';

ChartJS.register(
    ArcElement,
    Tooltip,
    Legend,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    PointElement,
    LineElement,
    Filler
);

const GeneralTab = () => {
    const { data: statsData, isLoading } = useQuery({
        queryKey: ['admin-stats'],
        queryFn: async () => {
            const res = await getStats();
            return res.data;
        },
    });

    if (isLoading) return <div className="loading">Cargando estadísticas generales...</div>;

    const stats = statsData || {};
    const gameDist = stats.game_distribution || { memoria: 0, abecedario: 0, paseo: 0, trenes: 0 };
    const activityHistory = stats.activity_history || [];

    const pieData = {
        labels: ['Memoria', 'Abecedario', 'Paseo', 'Trenes'],
        datasets: [
            {
                data: [gameDist.memoria, gameDist.abecedario, gameDist.paseo, gameDist.trenes],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                ],
                borderWidth: 2,
            },
        ],
    };

    const lineData = {
        labels: activityHistory.map((h: any) => h.date),
        datasets: [
            {
                label: 'Sesiones Diarias',
                data: activityHistory.map((h: any) => h.count),
                fill: true,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                tension: 0.4, // Smooth curve
                pointBackgroundColor: 'rgba(75, 192, 192, 1)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgba(75, 192, 192, 1)',
            },
        ],
    };

    const barData = {
        labels: ['Hoy', 'Total Histórico'],
        datasets: [
            {
                label: 'Sesiones',
                data: [stats.sessions_today, stats.total_sessions],
                backgroundColor: [
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)'
                ],
                borderRadius: 5,
            },
        ],
    };

    const chartOptions = {
        maintainAspectRatio: false,
        plugins: {
            legend: { labels: { color: '#ccc' } },
            title: { display: true, color: '#fff', font: { size: 16 } }
        },
        scales: {
            y: { ticks: { color: '#aaa' }, grid: { color: '#333' } },
            x: { ticks: { color: '#aaa' }, grid: { display: false } }
        }
    };

    return (
        <div className="general-tab">
            <div className="stats-grid">
                <StatsCard
                    title="Total Usuarios"
                    value={stats.total_users || 0}
                    trend="👥 Registrados"
                    gradient="gradient-1"
                />
                <StatsCard
                    title="Sesiones Totales"
                    value={stats.total_sessions || 0}
                    trend="🎮 Global"
                    gradient="gradient-2"
                />
                <StatsCard
                    title="Actividad Hoy"
                    value={stats.sessions_today || 0}
                    trend="📅 Sesiones"
                    gradient="gradient-3"
                />
            </div>

            <div className="charts-grid" style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
                gap: '20px',
                marginTop: '20px'
            }}>
                <div className="chart-box" style={{ background: '#1a1b1e', padding: '20px', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }}>
                    <h3 style={{ marginBottom: '15px', color: '#eee' }}>📈 Tendencia de Actividad (7 Días)</h3>
                    <div style={{ height: '300px' }}>
                        <Line
                            data={lineData}
                            options={{
                                ...chartOptions,
                                plugins: { ...chartOptions.plugins, title: { display: false } }
                            }}
                        />
                    </div>
                </div>

                <div className="chart-box" style={{ background: '#1a1b1e', padding: '20px', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }}>
                    <h3 style={{ marginBottom: '15px', color: '#eee' }}>🍰 Distribución de Juegos</h3>
                    <div style={{ height: '300px', display: 'flex', justifyContent: 'center' }}>
                        <Pie
                            data={pieData}
                            options={{
                                maintainAspectRatio: false,
                                plugins: { legend: { position: 'right', labels: { color: '#fff' } } }
                            }}
                        />
                    </div>
                </div>

                <div className="chart-box" style={{ background: '#1a1b1e', padding: '20px', borderRadius: '15px', boxShadow: '0 4px 6px rgba(0,0,0,0.3)' }}>
                    <h3 style={{ marginBottom: '15px', color: '#eee' }}>📊 Volumen de Actividad</h3>
                    <div style={{ height: '300px' }}>
                        <Bar
                            data={barData}
                            options={{
                                ...chartOptions,
                                plugins: { ...chartOptions.plugins, title: { display: false } }
                            }}
                        />
                    </div>
                </div>
            </div>

            <div style={{ marginTop: '30px' }}>
                <h2 style={{ marginBottom: '20px', color: '#eee' }}>🤖 Impacto de Inteligencia Artificial</h2>
                <div className="stats-grid">
                    <StatsCard
                        title="Intervenciones Totales"
                        value={stats.ai_metrics?.total_actions || 0}
                        trend="⚡ Acciones IA"
                        gradient="gradient-1"
                    />
                    <StatsCard
                        title="Ajustes de Dificultad"
                        value={stats.ai_metrics?.memory_adjustments || 0}
                        trend="🧠 Memoria"
                        gradient="gradient-2"
                    />
                    <StatsCard
                        title="Cambios de Nivel"
                        value={stats.ai_metrics?.abecedario_level_changes || 0}
                        trend="🔤 Abecedario"
                        gradient="gradient-3"
                    />
                    <StatsCard
                        title="Recomendaciones"
                        value={stats.ai_metrics?.paseo_recommendations || 0}
                        trend="🚶 Paseo"
                        gradient="gradient-1"
                    />
                </div>
            </div>
        </div>
    );
};

export default GeneralTab;
