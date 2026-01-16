const API_BASE = 'http://localhost:5000';
let charts = {};
let currentUserId = null;
let currentUserName = null;

// ========== NAVIGATION ==========
function switchTab(tabName) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.textContent.toLowerCase().includes(tabName) ||
            (tabName === 'train' && item.textContent.includes('Trenes'))) {
            item.classList.add('active');
        }
    });

    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    const tab = document.getElementById(`tab-${tabName}`);
    if (tab) tab.classList.add('active');

    const titles = {
        'general': 'Dashboard General',
        'memory': 'Memory Game Stats',
        'abecedario': 'Abecedario Stats',
        'paseo': 'Paseo Stats',
        'train': 'Trenes Stats',
        'usuarios': 'Estadísticas por Usuario'
    };
    document.getElementById('pageTitle').textContent = titles[tabName] || 'Dashboard';
}

// ========== API HELPER ==========
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`);
        return await response.json();
    } catch (error) {
        console.error(`Error fetching ${endpoint}:`, error);
        return null;
    }
}

// ========== LOAD ALL DATA ==========
async function loadAllData() {
    await Promise.all([
        loadGeneralStats(),
        loadMemoryData(),
        loadAbecedarioData(),
        loadPaseoData(),
        loadTrainData(),
        loadUsersDropdown()
    ]);
    initCharts();
}

// ========== GENERAL STATS ==========
async function loadGeneralStats() {
    const usersData = await fetchAPI('/users');
    if (usersData && usersData.users) {
        document.getElementById('totalUsers').textContent = usersData.users.length;
        const tbody = document.querySelector('#usersTable tbody');
        tbody.innerHTML = usersData.users.slice(0, 5).map(u => `
            <tr>
                <td>#${u.id}</td>
                <td>${u.nombre}</td>
                <td>${u.edad}</td>
                <td>${u.genero}</td>
            </tr>
        `).join('');
    }

    const statsData = await fetchAPI('/admin/stats');
    if (statsData) {
        document.getElementById('totalGames').textContent = statsData.total_sessions || 0;
        document.getElementById('gamesToday').textContent = statsData.sessions_today || 0;
        const el = document.getElementById('memAvgAccuracy');
        if (el) el.textContent = (statsData.average_accuracy ? statsData.average_accuracy.toFixed(1) : 0) + '%';
    }
}

// ========== MEMORY DATA ==========
async function loadMemoryData() {
    const sessionsData = await fetchAPI('/admin/memory-sessions');
    if (sessionsData && sessionsData.sessions) {
        const tbody = document.querySelector('#memoryTable tbody');
        if (tbody) {
            tbody.innerHTML = sessionsData.sessions.map(s => `
                <tr>
                    <td>#${s.session_id}</td>
                    <td>${s.user_name || 'User ' + s.user_id}</td>
                    <td><span class="badge badge-info">${s.difficulty_level}</span></td>
                    <td>${s.pairs_found}/${s.total_pairs}</td>
                    <td>${s.accuracy ? s.accuracy.toFixed(1) : 0}%</td>
                    <td>${s.elapsed_time ? s.elapsed_time.toFixed(1) : 0}s</td>
                    <td><span class="badge ${s.completion_status === 'completed' ? 'badge-success' : 'badge-danger'}">${s.completion_status}</span></td>
                </tr>
            `).join('');
        }
    }

    const configsData = await fetchAPI('/admin/memory-configs');
    if (configsData && configsData.configs) {
        const tbody = document.querySelector('#configTable tbody');
        if (tbody) {
            tbody.innerHTML = configsData.configs.map(c => `
                <tr>
                    <td>User ${c.user_id}</td>
                    <td><span class="badge badge-warning">${c.difficulty_label}</span></td>
                    <td>${c.grid_size}</td>
                    <td>${c.time_limit}s</td>
                </tr>
            `).join('');
        }
    }
}

// ========== ABECEDARIO DATA ==========
async function loadAbecedarioData() {
    const data = await fetchAPI('/admin/abecedario-sessions');
    if (data && data.sessions) {
        const el = document.getElementById('abcCompleted');
        if (el) el.textContent = data.sessions.length;

        const tbody = document.querySelector('#abecedarioTable tbody');
        if (tbody) {
            tbody.innerHTML = data.sessions.map(s => `
                <tr>
                    <td>#${s.id}</td>
                    <td>${s.user_name || 'User ' + s.user_id}</td>
                    <td style="color: var(--accent-cyan); font-weight: bold;">${s.palabra_objetivo}</td>
                    <td>${s.tiempo_resolucion}s</td>
                    <td>${s.cantidad_errores}</td>
                    <td>${s.pistas_usadas}</td>
                    <td><span class="badge ${s.completado ? 'badge-success' : 'badge-danger'}">${s.completado ? 'Completado' : 'Incompleto'}</span></td>
                </tr>
            `).join('');
        }
    }
}

// ========== PASEO DATA ==========
async function loadPaseoData() {
    const data = await fetchAPI('/admin/paseo-sessions');
    if (data && data.sessions) {
        const victorias = data.sessions.filter(s => s.resultado === 'victoria').length;
        const precisionPromedio = data.sessions.length > 0
            ? data.sessions.reduce((sum, s) => sum + (s.precision || 0), 0) / data.sessions.length
            : 0;

        const elTotal = document.getElementById('paseoTotal');
        const elVic = document.getElementById('paseoVictorias');
        const elPrec = document.getElementById('paseoPrecision');

        if (elTotal) elTotal.textContent = data.sessions.length;
        if (elVic) elVic.textContent = victorias;
        if (elPrec) elPrec.textContent = precisionPromedio.toFixed(1) + '%';

        const tbody = document.querySelector('#paseoTable tbody');
        if (tbody) {
            tbody.innerHTML = data.sessions.map(s => `
                <tr>
                    <td>#${s.id}</td>
                    <td>${s.user_name || 'User ' + s.user_id}</td>
                    <td><span class="badge badge-info">${s.nivel_dificultad}</span></td>
                    <td>${s.esferas_rojas_atrapadas}</td>
                    <td>${s.meta_aciertos}</td>
                    <td>${(s.precision || 0).toFixed(1)}%</td>
                    <td><span class="badge ${s.resultado === 'victoria' ? 'badge-success' : 'badge-danger'}">${s.resultado}</span></td>
                </tr>
            `).join('');
        }
    }
}

// ========== TRAIN DATA ==========
async function loadTrainData() {
    const data = await fetchAPI('/admin/train-sessions');
    if (data && data.sessions) {
        const totalCorrect = data.sessions.reduce((sum, s) => sum + (s.correct_routing || 0), 0);
        const totalWrong = data.sessions.reduce((sum, s) => sum + (s.wrong_routing || 0), 0);
        const totalAttempts = totalCorrect + totalWrong;
        const avgAccuracy = totalAttempts > 0 ? (totalCorrect / totalAttempts * 100) : 0;

        const elTotal = document.getElementById('trainTotal');
        const elAcc = document.getElementById('trainAccuracy');

        if (elTotal) elTotal.textContent = data.sessions.length;
        if (elAcc) elAcc.textContent = avgAccuracy.toFixed(1) + '%';

        const tbody = document.querySelector('#trainTable tbody');
        if (tbody) {
            tbody.innerHTML = data.sessions.map(s => `
                <tr>
                    <td>#${s.session_id}</td>
                    <td>${s.user_name || 'User ' + s.user_id}</td>
                    <td>${s.train_speed}</td>
                    <td>${s.color_count}</td>
                    <td>${s.correct_routing}</td>
                    <td>${s.wrong_routing}</td>
                    <td>${formatDate(s.finished_at || s.started_at)}</td>
                </tr>
            `).join('');
        }
    }
}

// ========== USER DROPDOWN ==========
async function loadUsersDropdown() {
    const usersData = await fetchAPI('/users');
    if (usersData && usersData.users) {
        const select = document.getElementById('userSelect');
        if (select) {
            select.innerHTML = '<option value="">-- Seleccione un usuario --</option>';
            usersData.users.forEach(user => {
                const option = document.createElement('option');
                option.value = user.id;
                option.textContent = `${user.nombre} (${user.edad} años, ${user.genero})`;
                select.appendChild(option);
            });
        }
    }
}

// ========== USER SELECTION ==========
async function onUserSelected() {
    const select = document.getElementById('userSelect');
    const userId = select.value;

    if (!userId) {
        document.getElementById('emptyState').style.display = 'block';
        document.getElementById('gameCardsContainer').style.display = 'none';
        hideAllDetails();
        return;
    }

    currentUserId = userId;
    const selectedOption = select.options[select.selectedIndex];
    currentUserName = selectedOption.textContent.split(' (')[0];

    document.getElementById('emptyState').style.display = 'none';
    document.getElementById('gameCardsContainer').style.display = 'block';
    document.getElementById('selectedUserTitle').textContent = `📊 Estadísticas de ${currentUserName}`;

    await loadUserGameStats(userId);
    hideAllDetails();
}

// ========== USER GAME STATS ==========
async function loadUserGameStats(userId) {
    const data = await fetchAPI(`/admin/user-stats/${userId}`);
    if (data && data.success) {
        // Memoria
        setTextContent('memoriaTotalSessions', data.stats.memoria.total_sesiones);
        setTextContent('memoriaAccuracy', data.stats.memoria.promedio_accuracy.toFixed(1) + '%');
        setTextContent('memoriaCompleted', data.stats.memoria.sesiones_completadas);

        // Abecedario
        setTextContent('abecedarioTotalSessions', data.stats.abecedario.total_sesiones);
        setTextContent('abecedarioCompleted', data.stats.abecedario.palabras_completadas);
        setTextContent('abecedarioAvgTime', data.stats.abecedario.tiempo_promedio.toFixed(1) + 's');

        // Paseo
        setTextContent('paseoTotalSessions', data.stats.paseo.total_sesiones);
        setTextContent('paseoVictoriasStats', data.stats.paseo.victorias);
        setTextContent('paseoPrecisionStats', data.stats.paseo.precision_promedio.toFixed(1) + '%');

        // Trenes
        setTextContent('trainTotalSessions', data.stats.trenes.total_sesiones);
        setTextContent('trainTotalCorrect', data.stats.trenes.total_aciertos);
        setTextContent('trainPrecisionStats', data.stats.trenes.precision_promedio.toFixed(1) + '%');
    }
}

// ========== GAME DETAILS ==========
async function showGameDetails(gameName) {
    if (!currentUserId) return;

    const gameCards = document.querySelector('#gameCardsContainer .game-cards');
    if (gameCards) gameCards.style.display = 'none';
    hideAllDetails();

    const detailView = document.getElementById(`detailed${capitalize(gameName)}`);
    if (detailView) {
        detailView.classList.add('active');
        detailView.style.display = 'block';
    }

    if (gameName === 'memoria') await loadMemoriaDetails(currentUserId);
    else if (gameName === 'abecedario') await loadAbecedarioDetails(currentUserId);
    else if (gameName === 'paseo') await loadPaseoDetails(currentUserId);
    else if (gameName === 'train') await loadTrainDetails(currentUserId);
}

function hideGameDetails() {
    hideAllDetails();
    const gameCards = document.querySelector('#gameCardsContainer .game-cards');
    if (gameCards) gameCards.style.display = 'grid';
}

function hideAllDetails() {
    document.querySelectorAll('.detailed-view').forEach(view => {
        view.classList.remove('active');
        view.style.display = 'none';
    });
}

// ========== DETAIL LOADERS ==========
async function loadMemoriaDetails(userId) {
    const data = await fetchAPI(`/admin/user-memory-sessions/${userId}`);
    if (data && data.sessions) {
        const tbody = document.querySelector('#memoriaDetailTable tbody');
        if (!tbody) return;
        if (data.sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px;">No hay sesiones</td></tr>';
            return;
        }
        tbody.innerHTML = data.sessions.map(s => `
            <tr>
                <td>#${s.session_id}</td>
                <td>${formatDate(s.finished_at || s.started_at)}</td>
                <td><span class="badge badge-info">${s.difficulty_level}</span></td>
                <td>${s.pairs_found}/${s.total_pairs}</td>
                <td>${(s.accuracy || 0).toFixed(1)}%</td>
                <td>${(s.elapsed_time || 0).toFixed(1)}s</td>
                <td><span class="badge ${s.completion_status === 'completed' ? 'badge-success' : 'badge-danger'}">${s.completion_status}</span></td>
            </tr>
        `).join('');
    }
}

async function loadAbecedarioDetails(userId) {
    const data = await fetchAPI(`/admin/user-abecedario-sessions/${userId}`);
    if (data && data.sessions) {
        const tbody = document.querySelector('#abecedarioDetailTable tbody');
        if (!tbody) return;
        if (data.sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px;">No hay sesiones</td></tr>';
            return;
        }
        tbody.innerHTML = data.sessions.map(s => `
            <tr>
                <td>#${s.id}</td>
                <td>${formatDate(s.created_at)}</td>
                <td style="color: var(--accent-cyan);">${s.palabra_objetivo}</td>
                <td>${s.tiempo_resolucion.toFixed(1)}s</td>
                <td>${s.cantidad_errores}</td>
                <td>${s.pistas_usadas}</td>
                <td><span class="badge ${s.completado ? 'badge-success' : 'badge-danger'}">${s.completado ? 'Completado' : 'Incompleto'}</span></td>
            </tr>
        `).join('');
    }
}

async function loadPaseoDetails(userId) {
    const data = await fetchAPI(`/admin/user-paseo-sessions/${userId}`);
    if (data && data.sessions) {
        const tbody = document.querySelector('#paseoDetailTable tbody');
        if (!tbody) return;
        if (data.sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px;">No hay sesiones</td></tr>';
            return;
        }
        tbody.innerHTML = data.sessions.map(s => `
            <tr>
                <td>#${s.id}</td>
                <td>${formatDate(s.created_at)}</td>
                <td><span class="badge badge-info">${s.nivel_dificultad}</span></td>
                <td>${s.esferas_rojas_atrapadas}</td>
                <td>${s.meta_aciertos}</td>
                <td>${(s.precision || 0).toFixed(1)}%</td>
                <td><span class="badge ${s.resultado === 'victoria' ? 'badge-success' : 'badge-danger'}">${s.resultado}</span></td>
            </tr>
        `).join('');
    }
}

async function loadTrainDetails(userId) {
    const data = await fetchAPI(`/admin/user-train-sessions/${userId}`);
    if (data && data.sessions) {
        const tbody = document.querySelector('#trainDetailTable tbody');
        if (!tbody) return;
        if (data.sessions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px;">No hay sesiones</td></tr>';
            return;
        }
        tbody.innerHTML = data.sessions.map(s => `
            <tr>
                <td>#${s.session_id}</td>
                <td>${formatDate(s.finished_at || s.started_at)}</td>
                <td>${s.train_speed}</td>
                <td>${s.color_count}</td>
                <td>${s.correct_routing}</td>
                <td>${s.wrong_routing}</td>
                <td><span class="badge ${s.completion_status === 'completed' ? 'badge-success' : 'badge-warning'}">${s.completion_status}</span></td>
            </tr>
        `).join('');
    }
}

// ========== CHARTS ==========
function initCharts() {
    const ctxActivity = document.getElementById('activityChart');
    if (ctxActivity) {
        if (charts.activity) charts.activity.destroy();
        charts.activity = new Chart(ctxActivity.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'],
                datasets: [{
                    label: 'Sesiones',
                    data: [12, 19, 3, 5, 2, 3, 10],
                    borderColor: '#bb86fc',
                    backgroundColor: 'rgba(187, 134, 252, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    const ctxGender = document.getElementById('genderChart');
    if (ctxGender) {
        if (charts.gender) charts.gender.destroy();
        charts.gender = new Chart(ctxGender.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: ['M', 'F'],
                datasets: [{
                    data: [65, 35],
                    backgroundColor: ['#03dac6', '#ff79c6'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'bottom', labels: { color: '#fff' } } }
            }
        });
    }
}

// ========== UTILITIES ==========
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function setTextContent(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
    setInterval(loadAllData, 30000);
});
