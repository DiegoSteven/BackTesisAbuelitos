import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
} from 'chart.js';
import { getUsers, getProgressionStats, getGeneralProgressionStats, getIndicators } from '../services/api';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale
);

const ProgressionTab = () => {
    const [selectedUserId, setSelectedUserId] = useState<number | string>('general');
    const [activeGameTab, setActiveGameTab] = useState('abecedario');
    const [isDarkTheme, setIsDarkTheme] = useState(true);

    const { data: usersData } = useQuery({
        queryKey: ['users'],
        queryFn: getUsers
    });

    const { data: progressionData, isLoading } = useQuery({
        queryKey: ['progression', selectedUserId],
        queryFn: () => {
            if (selectedUserId === 'general') {
                return getGeneralProgressionStats();
            }
            return getProgressionStats(Number(selectedUserId));
        },
        enabled: !!selectedUserId
    });

    const { data: indicatorsData } = useQuery({
        queryKey: ['indicators', selectedUserId],
        queryFn: () => getIndicators(selectedUserId),
        enabled: !!selectedUserId
    });

    if (!usersData) return <div className="loading">Cargando usuarios...</div>;

    const users = usersData.data.users;

    // Colores según tema
    const theme = {
        text: isDarkTheme ? '#e2e8f0' : '#1e293b',
        textSecondary: isDarkTheme ? '#94a3b8' : '#475569',
        grid: isDarkTheme ? '#334155' : '#e2e8f0',
        bg: isDarkTheme ? '#1e293b' : '#ffffff',
        bgSecondary: isDarkTheme ? '#334155' : '#f1f5f9',
        border: isDarkTheme ? '#475569' : '#cbd5e1'
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top' as const,
                labels: { color: theme.text, font: { size: 16, weight: 500 } }
            },
            title: {
                display: true,
                color: theme.text,
                font: { size: 20, weight: 'bold' as const },
                padding: { bottom: 20 }
            }
        },
        scales: {
            y: {
                ticks: { color: theme.textSecondary, font: { size: 14 }, stepSize: 0.5 },
                grid: { color: theme.grid }
            },
            x: {
                ticks: { color: theme.textSecondary, font: { size: 14 }, maxRotation: 45, minRotation: 45 },
                grid: { color: theme.grid }
            }
        }
    };

    const createChartData = (label: string, data: any[], color: string) => {
        return {
            labels: data.map(d => d.date),
            datasets: [
                {
                    label,
                    data: data.map(d => d.level_value),
                    borderColor: color,
                    backgroundColor: color,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderWidth: 3
                }
            ]
        };
    };

    const gameTabs = [
        { id: 'abecedario', label: 'Abecedario', color: '#3b82f6' },
        { id: 'memoria', label: 'Memoria', color: '#10b981' },
        { id: 'paseo', label: 'Paseo', color: '#f59e0b' },
        { id: 'trenes', label: 'Trenes', color: '#ef4444' }
    ];

    const renderActiveChart = () => {
        if (!progressionData) return null;

        const commonOptions = {
            ...chartOptions,
            maintainAspectRatio: false,
        };

        switch (activeGameTab) {
            case 'abecedario':
                return (
                    <Line
                        options={{
                            ...commonOptions,
                            plugins: { ...commonOptions.plugins, title: { ...commonOptions.plugins.title, text: 'Progresión en Abecedario' } },
                            scales: {
                                ...commonOptions.scales,
                                y: {
                                    ...commonOptions.scales.y,
                                    min: 0,
                                    max: 2.5,
                                    ticks: {
                                        stepSize: 0.5,
                                        callback: function (value) {
                                            const labels: Record<number, string> = { 0: 'Fácil', 1: 'Intermedio', 2: 'Difícil' };
                                            return labels[Number(value)] ?? value;
                                        },
                                        color: '#94a3b8'
                                    }
                                }
                            }
                        }}
                        data={createChartData('Nivel de Dificultad', progressionData.progression.abecedario, '#3b82f6')}
                    />
                );
            case 'memoria':
                return (
                    <Line
                        options={{
                            ...commonOptions,
                            plugins: { ...commonOptions.plugins, title: { ...commonOptions.plugins.title, text: 'Progresión en Memoria' } },
                            scales: {
                                ...commonOptions.scales,
                                y: {
                                    ...commonOptions.scales.y,
                                    min: 0,
                                    max: 3.5,
                                    ticks: {
                                        stepSize: 0.5,
                                        callback: function (value) {
                                            const labels: Record<number, string> = { 0: 'Tutorial', 1: 'Fácil', 2: 'Medio', 3: 'Difícil' };
                                            return labels[Number(value)] ?? value;
                                        },
                                        color: '#94a3b8'
                                    }
                                }
                            }
                        }}
                        data={createChartData('Nivel de Dificultad', progressionData.progression.memoria, '#10b981')}
                    />
                );
            case 'paseo':
                return (
                    <Line
                        options={{
                            ...commonOptions,
                            plugins: { ...commonOptions.plugins, title: { ...commonOptions.plugins.title, text: 'Progresión en Paseo' } },
                            scales: {
                                ...commonOptions.scales,
                                y: {
                                    ...commonOptions.scales.y,
                                    min: 0,
                                    max: 2.5,
                                    ticks: {
                                        stepSize: 0.5,
                                        callback: function (value) {
                                            const labels: Record<number, string> = { 0: 'Fácil', 1: 'Intermedio', 2: 'Difícil' };
                                            return labels[Number(value)] ?? value;
                                        },
                                        color: '#94a3b8'
                                    }
                                }
                            }
                        }}
                        data={createChartData('Nivel de Dificultad', progressionData.progression.paseo, '#f59e0b')}
                    />
                );
            case 'trenes':
                return (
                    <Line
                        options={{
                            ...commonOptions,
                            plugins: { ...commonOptions.plugins, title: { ...commonOptions.plugins.title, text: 'Progresión en Trenes' } },
                            scales: {
                                ...commonOptions.scales,
                                y: {
                                    ...commonOptions.scales.y,
                                    min: 0,
                                    max: 2.5,
                                    ticks: {
                                        stepSize: 0.5,
                                        callback: function (value) {
                                            const labels: Record<number, string> = { 0: 'Fácil', 1: 'Medio', 2: 'Difícil' };
                                            return labels[Number(value)] ?? value;
                                        },
                                        color: '#94a3b8'
                                    }
                                }
                            }
                        }}
                        data={createChartData('Nivel de Dificultad', progressionData.progression.trenes, '#ef4444')}
                    />
                );
            default: return null;
        }
    };

    return (
        <div className={`tab-content ${isDarkTheme ? 'theme-dark' : 'theme-light'}`}>
            <div className="header-controls" style={{ background: theme.bg }}>
                <div className="user-selector-container">
                    <label style={{ color: theme.text }}>Seleccionar Usuario:</label>
                    <select
                        value={selectedUserId}
                        onChange={(e) => setSelectedUserId(e.target.value)}
                        className="user-select"
                        style={{ background: theme.bgSecondary, color: theme.text, borderColor: theme.border }}
                    >
                        <option value="general">📊 General (Promedio Todos)</option>
                        {users.map((u: any) => (
                            <option key={u.id} value={u.id}>{u.nombre}</option>
                        ))}
                    </select>
                </div>
                <button
                    className="theme-toggle-btn"
                    onClick={() => setIsDarkTheme(!isDarkTheme)}
                    style={{ background: theme.bgSecondary, color: theme.text, borderColor: theme.border }}
                >
                    {isDarkTheme ? '☀️ Tema Claro' : '🌙 Tema Oscuro'}
                </button>
            </div>

            <div className="game-tabs" style={{ borderBottomColor: theme.border }}>
                {gameTabs.map(tab => (
                    <button
                        key={tab.id}
                        className={`game-tab ${activeGameTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveGameTab(tab.id)}
                        style={{
                            borderBottomColor: activeGameTab === tab.id ? tab.color : 'transparent',
                            color: activeGameTab === tab.id ? theme.text : theme.textSecondary,
                            background: activeGameTab === tab.id ? theme.bg : 'transparent'
                        }}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="chart-display-area" style={{ background: theme.bg }}>
                {isLoading && <div className="loading" style={{ color: theme.textSecondary }}>Cargando progresión...</div>}

                {!isLoading && progressionData && (
                    <div className="chart-wrapper">
                        {renderActiveChart()}
                    </div>
                )}
            </div>

            {/* Tabla de Indicadores */}
            <div style={{ background: theme.bg, borderRadius: 12, padding: 20 }}>
                <h3 style={{ color: theme.text, fontSize: 18, fontWeight: 600, margin: '0 0 15px 0' }}>Indicadores del Juego</h3>
                {indicatorsData?.indicators?.[activeGameTab] && (
                    <table className="indicators-table" style={{ background: theme.bg }}>
                        <thead>
                            <tr>
                                {[
                                    { key: 'total_sesiones', label: 'Sesiones Totales' },
                                    { key: 'aciertos', label: 'Aciertos' },
                                    { key: 'precision', label: 'Precisión (%)' },
                                    { key: 'tiempo_promedio', label: 'Tiempo Prom. (s)' },
                                    { key: 'tiempo_total', label: 'Tiempo Total (min)' },
                                    { key: 'nivel_maximo', label: 'Nivel Máximo' },
                                    { key: 'sesiones_completadas', label: 'Completadas' }
                                ].map(col => (
                                    <th key={col.key} style={{ background: theme.bgSecondary, color: theme.textSecondary }}>{col.label}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                {['total_sesiones', 'aciertos', 'precision', 'tiempo_promedio', 'tiempo_total', 'nivel_maximo', 'sesiones_completadas'].map(key => {
                                    const val = indicatorsData.indicators[activeGameTab]?.[key];
                                    return <td key={key} style={{ color: theme.text, borderColor: theme.border }}>{val ?? '-'}</td>;
                                })}
                            </tr>
                        </tbody>
                    </table>
                )}
            </div>

            <style>{`
        .tab-content {
            display: flex;
            flex-direction: column;
            gap: 20px;
            padding-bottom: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            text-rendering: optimizeLegibility;
        }
        .header-controls {
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .user-selector-container {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .user-selector-container label {
            font-weight: 600;
            font-size: 16px;
        }
        .user-select {
            padding: 12px 18px;
            border-radius: 8px;
            border: 1px solid;
            min-width: 280px;
            font-size: 15px;
            font-weight: 500;
            outline: none;
            cursor: pointer;
        }
        .user-select:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }
        .theme-toggle-btn {
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .theme-toggle-btn:hover {
            opacity: 0.85;
        }
        
        .game-tabs {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid;
            padding-bottom: 0;
        }
        .game-tab {
            background: transparent;
            border: none;
            padding: 14px 28px;
            font-size: 17px;
            font-weight: 600;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.2s ease;
            border-radius: 8px 8px 0 0;
        }
        .game-tab:hover {
            opacity: 0.8;
        }

        .chart-display-area {
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            height: 450px;
            box-sizing: border-box;
            display: block;
            overflow: hidden;
        }
        .chart-wrapper {
            width: 100%;
            height: 100%;
            position: relative;
        }
        .loading {
            text-align: center;
            padding: 40px;
            font-size: 18px;
            font-weight: 500;
        }

        /* Tabla de Indicadores */
        .indicators-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 15px;
        }
        .indicators-table th {
            font-weight: 600;
            text-align: center;
            padding: 14px 10px;
            border-bottom: 2px solid;
            white-space: nowrap;
        }
        .indicators-table td {
            text-align: center;
            padding: 16px 10px;
            border-bottom: 1px solid;
            font-weight: 500;
            font-size: 15px;
        }
      `}</style>
        </div>
    );
};

export default ProgressionTab;
