const response = await fetch(`${API_BASE_URL}/summary`);

document.addEventListener('DOMContentLoaded', loadDashboardData);

async function loadDashboardData() {
    try {
        await Promise.all([
            loadStats(),
            loadCharts()
        ]);
        console.log('Dashboard loaded successfully');
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Failed to load dashboard data');
    }
}

async function loadStats() {
    const response = await fetch(`${API_BASE_URL}/summary`);
    const stats = await response.json();

    updateStatCard(1, stats.total_balance, stats.balance_change);
    updateStatCard(2, stats.total_income, stats.income_change);
    updateStatCard(3, stats.total_expense, stats.expense_change);
}

function updateStatCard(cardIndex, value, change) {
    const card = document.querySelector(`.stat-card:nth-child(${cardIndex})`);
    card.querySelector('.stat-value').textContent = `$${value.toLocaleString()}`;

    const changeElement = card.querySelector('.stat-change');
    changeElement.querySelector('span:first-child').textContent =
        `${change > 0 ? '+' : ''}${change}%`;
    changeElement.className = `stat-change ${change >= 0 ? 'positive' : 'negative'}`;
}

async function loadCharts() {
    const chartLoaders = [
        { id: 'revenueOverviewChart', loader: loadRecentTransactions },
        { id: 'salesByCategoryChart', loader: loadTransactionTypes },
        { id: 'trendsChart', loader: loadMonthlyTrends },
        { id: 'volumeChart', loader: loadVolumeChart }
    ];

    await Promise.all(
        chartLoaders.map(({ id, loader }) =>
            document.getElementById(id) ? loader() : Promise.resolve()
        )
    );
}

async function loadRecentTransactions() {
    const response = await fetch(`${API_BASE_URL}/recent-transactions`);
    const transactions = await response.json();

    const ctx = document.getElementById('revenueOverviewChart').getContext('2d');
    const labels = transactions.map(t => `${t.date} ${t.time.substring(0,5)}`).reverse();

    new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Transaction Amount',
                    data: transactions.map(t => t.amount).reverse(),
                    borderColor: '#4F46E5',
                    backgroundColor: 'rgba(79, 70, 229, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Account Balance',
                    data: transactions.map(t => t.balance).reverse(),
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: getChartOptions('currency')
    });
}

async function loadTransactionTypes() {
    const response = await fetch(`${API_BASE_URL}/transaction-types`);
    const types = await response.json();

    const ctx = document.getElementById('salesByCategoryChart').getContext('2d');

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: types.map(t => t.type.charAt(0).toUpperCase() + t.type.slice(1)),
            datasets: [{
                data: types.map(t => t.total_amount),
                backgroundColor: getChartColors(types.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: getChartOptions('default')
    });
}

async function loadMonthlyTrends() {
    const response = await fetch(`${API_BASE_URL}/monthly-trends`);
    const trends = await response.json();

    const ctx = document.getElementById('trendsChart').getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trends.months,
            datasets: [
                {
                    label: 'Payments',
                    data: trends.payments,
                    backgroundColor: '#EF4444',
                    borderColor: '#DC2626',
                    borderWidth: 1
                },
                {
                    label: 'Deposits',
                    data: trends.deposits,
                    backgroundColor: '#10B981',
                    borderColor: '#059669',
                    borderWidth: 1
                }
            ]
        },
        options: getChartOptions('currency')
    });
}

async function loadVolumeChart() {
    const response = await fetch(`${API_BASE_URL}/volume-by-type`);
    const volume = await response.json();

    const ctx = document.getElementById('volumeChart').getContext('2d');

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: volume.labels,
            datasets: [{
                data: volume.data,
                backgroundColor: getChartColors(volume.labels.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: getChartOptions('default')
    });
}

function getChartOptions(type) {
    const baseOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: 'bottom' } }
    };

    if (type === 'currency') {
        baseOptions.scales = {
            y: {
                beginAtZero: type === 'bar',
                ticks: {
                    callback: value => '$' + value.toLocaleString()
                }
            }
        };
    }

    return baseOptions;
}

function getChartColors(count) {
    const colors = ['#4F46E5', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4', '#84CC16', '#F97316'];
    return colors.slice(0, count);
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">×</button>
    `;

    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 5000);
}

const refreshDashboard = loadDashboardData;
