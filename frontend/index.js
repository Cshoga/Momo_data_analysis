const response = await fetch(`${API_BASE_URL}/summary`);

let modal;
let closeModal;

document.addEventListener('DOMContentLoaded', function() {
    modal = document.getElementById('transactionModal');
    closeModal = document.querySelector('.close-modal');
    
    if (closeModal) {
        closeModal.onclick = closeTransactionModal;
    }
    
    window.onclick = function(event) {
        if (event.target === modal) {
            closeTransactionModal();
        }
    };
});

function formatCurrency(number) {
    if (number === null || number === undefined) return 'N/A';
    return new Intl.NumberFormat('en-RW', {
        style: 'currency',
        currency: 'RWF',
        currencyDisplay: 'code'
    }).format(number).replace('RWF', 'RFW');
}

function formatNumber(number) {
    return new Intl.NumberFormat('en-US').format(number);
}

function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showError(error.message);
        throw error;
    }
}

function showError(message = "Unable to connect to the serever. Please make sure your Flask backend is running on http://localhost:5000") {
    document.getElementById('loadingSpinner').style.display = 'none';
    const errorMessageElement = document.getElementById('errorMessage');
    if (errorMessageElement) {
        errorMessageElement.style.display = 'block';
        const errorTextElement = errorMessageElement.querySelector('p');
        if (errorTextElement) {
            errorTextElement.textContent = message;
        }
    }
}

function hideError() {
    const errorMessageElement = document.getElementById('errorMessage');
    if (errorMessageElement) {
        errorMessageElement.style.display = 'none';
    }
}

function showLoading() {
    document.getElementById('loadingSpinner').style.display = 'flex';
    hideError();
}

function hideLoading() {
    document.getElementById('loadingSpinner').style.display = 'none';
}

function updateTrend(elementId, trendValue) {
    const element = document.getElementById(elementId);
    if (!element) return;
    const icon = element.querySelector('i');
    const span = element.querySelector('span');
    
    const isPositive = trendValue >= 0;
    
    element.className = `stat-change ${isPositive ? 'positive' : 'negative'}`;
    if (icon) icon.className = `fas fa-arrow-${isPositive ? 'up' : 'down'}`;
    if (span) span.textContent = `${Math.abs(trendValue).toFixed(1)}%`;
}

function closeTransactionModal() {
    modal.style.display = 'none';
}

function getCategoryClass(category) {
    const categoryMap = {
        'Incoming Money': 'incoming',
        'Bank Deposits': 'incoming',
        'Transfers to Mobile Numbers': 'transfer',
        'Payments to Code Holders': 'transfer',
        'Airtime Bill Payments': 'outgoing',
        'Cash Power Bill Payments': 'outgoing',
        'Internet and Voice Bundle Purchases': 'outgoing',
        'Withdrawals from Agents': 'outgoing',
        'Bank Transfers': 'transfer'
    };
    return categoryMap[category] || 'transfer';
}

function updateTransactionsTable(transactions) {
    const tbody = document.getElementById('transactionsTableBody');
    if (!tbody) return;
    
    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">No transactions found</td></tr>';
        return;
    }
    
    tbody.innerHTML = transactions.map(transaction => {
        const categoryClass = getCategoryClass(transaction.category);
        const counterpartyLabel = transaction.counterparty_type === 'sender' ? 'From' : 'To';
        const safeTransaction = JSON.stringify(transaction).replace(/"/g, '&quot;');
        let counterpartyName = transaction.counterparty_name || 'N/A';
        if (counterpartyName !== 'N/A') {
            counterpartyName = counterpartyName.split('(')[0].trim();
        }
        
        return `
            <tr class="transaction-row" onclick="showTransactionDetails(${safeTransaction})">
                <td class="transaction-id">#${transaction.transaction_id}</td>
                <td class="transaction-date">${new Date(transaction.date).toLocaleDateString()}</td>
                <td class="transaction-amount">${formatCurrency(transaction.amount)}</td>
                <td><span class="status-badge ${categoryClass}">${transaction.category || 'N/A'}</span></td>
                <td class="transaction-counterparty">${counterpartyLabel}: ${counterpartyName}</td>
            </tr>
        `;
    }).join('');
}

function showTransactionDetails(transaction) {
    const modal = document.getElementById('transactionModal');
    if (!modal) return;
    
    document.getElementById('modalTransactionId').textContent = `#${transaction.transaction_id}`;
    document.getElementById('modalDate').textContent = new Date(transaction.date).toLocaleString();
    document.getElementById('modalAmount').textContent = formatCurrency(transaction.amount);
    document.getElementById('modalCategory').textContent = transaction.category || 'N/A';
    let counterpartyName = transaction.counterparty_name || 'N/A';
    if (counterpartyName !== 'N/A') {
        counterpartyName = counterpartyName.split('(')[0].trim();
    }
    document.getElementById('modalCounterparty').textContent = counterpartyName;
    document.getElementById('modalType').textContent = transaction.counterparty_type === 'sender' ? 'Money Received' : 'Money Sent';
    document.getElementById('modalCurrency').textContent = transaction.currency || 'RFW';
    document.getElementById('modalSource').textContent = transaction.source || 'Mobile';
    
    modal.style.display = 'block';
}

let currentPage = 1;
let totalPages = 1;
let currentSort = { column: 'date', order: 'desc' };
let currentPeriod = 'daily';
let currentCategory = null;
let transactionsPerPage = 10;
let timeAnalysisChart;
let categoryChart;

function updatePagination(pagination) {
    totalPages = pagination.total_pages;
    currentPage = pagination.page;
    
    const paginationInfo = document.getElementById('paginationInfo');
    const prevPageBtn = document.getElementById('prevPage');
    const nextPageBtn = document.getElementById('nextPage');
    const pageNumbers = document.getElementById('pageNumbers');

    if (paginationInfo) {
        paginationInfo.textContent = 
            `Showing ${((pagination.page - 1) * pagination.per_page) + 1}-${Math.min(pagination.page * pagination.per_page, pagination.total)} of ${pagination.total} transactions`;
    }
    
    if (prevPageBtn) prevPageBtn.disabled = currentPage <= 1;
    if (nextPageBtn) nextPageBtn.disabled = currentPage >= totalPages;
    
    if (pageNumbers) pageNumbers.innerHTML = `Page ${currentPage} of ${totalPages}`;
}

function updateFilterInfo(category) {
    currentCategory = category; 
    const filterInfo = document.getElementById('filterInfo');
    const filterInfoText = document.getElementById('filterInfoText');
    
    if (!filterInfo || !filterInfoText) return;

    if (currentCategory) {
        filterInfo.classList.remove('hidden');
        filterInfoText.textContent = `Showing transactions in '${currentCategory}'`;
    } else {
        filterInfo.classList.add('hidden');
    }
}

function updateCategoryFilterDropdown(categories) {
    const categoryFilter = document.getElementById('categoryFilter');
    if (!categoryFilter) return;

    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(category => {
        const option = document.createElement('option');
        option.value = category.category;
        option.textContent = category.category;
        if (currentCategory === category.category) {
            option.selected = true;
        }
        categoryFilter.appendChild(option);
    });
}

function updateCategoryLegend(data, colors) {
    const legend = document.getElementById('categoryLegend');
    if (!legend) return;
    legend.innerHTML = '';
    
    data.forEach((item, index) => {
        const legendItem = document.createElement('div');
        legendItem.className = 'legend-item';
        legendItem.innerHTML = `
            <div class="legend-color" style="background-color: ${colors[index]}"></div>
            <span>${item.category}</span>
        `;
        legend.appendChild(legendItem);
    });
}

function updateCategorySummary(data) {
    const summaryList = document.getElementById('categorySummary');
    if (!summaryList) return;
    
    if (data.length === 0) {
        summaryList.innerHTML = '<li class="category-item"><div class="category-info"><h4>No data available</h4></div></li>';
        return;
    }
    
    summaryList.innerHTML = data.map(item => `
        <li class="category-item">
            <div class="category-info">
                <h4>${item.category}</h4>
            </div>
            <div class="category-stats">
                <div class="category-amount">${formatCurrency(item.total_amount)}</div>
            </div>
        </li>
    `).join('');
}
function createCategoryChart(data) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    const colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#06b6d4', '#84cc16', '#f97316', '#ec4899', '#6366f1'
    ];
    
    categoryChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.map(item => item.category),
            datasets: [{
                data: data.map(item => item.total_amount),
                backgroundColor: colors.slice(0, data.length),
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = formatCurrency(context.parsed);
                            const percentage = ((context.parsed / data.reduce((sum, item) => sum + item.total_amount, 0)) * 100).toFixed(1);
                            return `${context.label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
    
    updateCategoryLegend(data, colors);
}

function createTimeAnalysisChart(data) {
    const ctx = document.getElementById('timeAnalysisChart').getContext('2d');
    
    if (timeAnalysisChart) {
        timeAnalysisChart.destroy();
    }
    
    const reversedData = [...data].reverse();
    
    timeAnalysisChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: reversedData.map(item => {
                if (currentPeriod === 'daily') {
                    return new Date(item.date).toLocaleDateString();
                } else {
                    return item.month;
                }
            }),
            datasets: [
                {
                    label: 'Transaction Count',
                    data: reversedData.map(item => item.transaction_count),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    yAxisID: 'y'
                },
                {
                    label: 'Total Amount',
                    data: reversedData.map(item => item.total_amount),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: currentPeriod === 'daily' ? 'Date' : 'Month'
                    }
                },
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Transaction Count'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Amount (RFW)'
                    },
                    grid: {
                        drawOnChartArea: false
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            if (context.datasetIndex === 1) {
                                return 'Amount: ' + formatCurrency(context.parsed.y);
                            }
                        }
                    }
                }
            }
        }
    });
}

async function loadOverviewData() {
    try {
        const data = await fetchAPI('/overview');
        
        document.getElementById('totalTransactions').textContent = formatNumber(data.total_transactions);
        document.getElementById('totalVolume').textContent = formatCurrency(data.total_volume);
        document.getElementById('incomingMoney').textContent = formatCurrency(data.incoming_money);
        document.getElementById('outgoingMoney').textContent = formatCurrency(data.outgoing_money);
        
        updateTrend('transactionsTrend', data.trends.transactions);
        updateTrend('volumeTrend', data.trends.volume);
        
        hideLoading();
    } catch (error) {
        console.error('Failed to load overview data:', error);
    }
}

async function loadCategoryDistribution() {
    try {
        const data = await fetchAPI('/category-distribution');
        updateCategoryFilterDropdown(data);
        createCategoryChart(data);
    } catch (error) {
        console.error('Failed to load category distribution:', error);
    }
}

async function loadTimeAnalysis() {
    try {
        const data = await fetchAPI(`/time-analysis?period=${currentPeriod}`);
        createTimeAnalysisChart(data);
    } catch (error) {
        console.error('Failed to load time analysis:', error);
    }
}

async function loadTransactions(category = null) {
    const tbody = document.getElementById('transactionsTableBody');
    if (!tbody) return;

    try {
        showLoading();
        tbody.innerHTML = '<tr><td colspan="5" class="loading-cell">Loading transactions...</td></tr>';
        
        const params = new URLSearchParams({
            page: currentPage,
            per_page: transactionsPerPage,
            sort_by: currentSort.column,
            sort_order: currentSort.order
        });
        
        if (category) {
            params.append('category', encodeURIComponent(category));
        }
        
        const response = await fetch(`${API_BASE_URL}/transactions?${params}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (!data || !data.transactions) {
            throw new Error('Invalid response format from server');
        }
        
        updateTransactionsTable(data.transactions);
        updatePagination(data.pagination);
        updateFilterInfo(category);
        
    } catch (error) {
        console.error('Failed to load transactions:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="loading-cell error">
            <i class="fas fa-exclamation-circle"></i>
            Failed to load transactions: ${error.message}
            <button onclick="loadTransactions(${category ? `'${category}'` : 'null'})" class="retry-btn">
                <i class="fas fa-sync-alt"></i> Retry
            </button>
        </td></tr>`;
    } finally {
        hideLoading();
    }
}

async function loadCategorySummary() {
    try {
        const data = await fetchAPI('/category-distribution'); 
        updateCategorySummary(data);
    } catch (error) {
        console.error('Failed to load category summary:', error);
    }
}

function initializeCategoryFilter() {
    const categoryFilter = document.getElementById('categoryFilter');
    if (!categoryFilter) return;

    fetchAPI('/category-distribution')
        .then(categories => {
    
            while (categoryFilter.options.length > 1) {
                categoryFilter.remove(1);
            }
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.category;
                option.textContent = `${category.category} (${category.transaction_count})`;
                categoryFilter.appendChild(option);
            });
            if (currentCategory) {
                categoryFilter.value = currentCategory;
            }
        })
        .catch(error => {
            console.error('Failed to load categories for filter:', error);
            const categoryFilter = document.getElementById('categoryFilter');
            if (categoryFilter) {
                categoryFilter.innerHTML = '<option value="">Error loading categories</option>';
            }
        });
}

function filterTransactions() {
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        currentCategory = categoryFilter.value;
        console.log("Selected category from dropdown:", currentCategory);
    }
    currentPage = 1; 
    loadTransactions(currentCategory);
}

function clearCategoryFilter() {
    currentCategory = null;
    currentPage = 1;
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.value = ""; 
    }
    loadTransactions();
}

function sortTable(column) {
    if (currentSort.column === column) {
        currentSort.order = currentSort.order === 'asc' ? 'desc' : 'asc';
    } else {
        currentSort.column = column;
        currentSort.order = 'desc';
    }
    
    currentPage = 1; 
    loadTransactions(currentCategory);
}

function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        loadTransactions(currentCategory);
    }
}

function togglePeriod() {
    currentPeriod = currentPeriod === 'daily' ? 'monthly' : 'daily';
    loadTimeAnalysis();
}

function handleNavigation(event) {
    event.preventDefault();
    const targetId = event.target.closest('.nav-item').id;
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.getElementById(targetId).classList.add('active');

}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
}

function toggleSidebar() {
    document.querySelector('.sidebar').classList.toggle('minimized');
    document.querySelector('.main-content').classList.toggle('full-width');
}

function refreshData() {
    loadOverviewData();
    loadCategoryDistribution();
    loadTimeAnalysis();
    loadTransactions(currentCategory);
    loadCategorySummary();
}

function refreshCategoryData() {
    loadCategoryDistribution();
}

function refreshTransactions() {
    loadTransactions(currentCategory);
}

function refreshCategorySummary() {
    loadCategorySummary();
}

function initializeDashboard() {
    loadOverviewData();
    loadCategoryDistribution();
    loadTimeAnalysis();
    loadTransactions();
    loadCategorySummary();
}

function handleSearch(event) {
    const searchTerm = event.target.value.trim().toLowerCase();
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const minAmount = document.getElementById('minAmount').value;
    const maxAmount = document.getElementById('maxAmount').value;
    
    const tbody = document.querySelector('.transactions-table tbody');
    const rows = tbody.getElementsByTagName('tr');

    for (let row of rows) {
        const text = row.textContent.toLowerCase();
        const dateCell = row.querySelector('.transaction-date');
        const amountCell = row.querySelector('.transaction-amount');
        
        const rowDate = new Date(dateCell.textContent);
        const rowAmount = parseFloat(amountCell.textContent.replace(/[^0-9.-]+/g, ''));
        
        const matchesSearch = text.includes(searchTerm);
        const matchesDateRange = (!startDate || rowDate >= new Date(startDate)) && 
                                (!endDate || rowDate <= new Date(endDate));
        const matchesAmountRange = (!minAmount || rowAmount >= parseFloat(minAmount)) && 
                                  (!maxAmount || rowAmount <= parseFloat(maxAmount));
        
        row.style.display = matchesSearch && matchesDateRange && matchesAmountRange ? '' : 'none';
    }
}

function setupEventListeners() {
    document.querySelectorAll('.nav-item a').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
    
    const searchInput = document.querySelector('.search-container input');
    const startDateInput = document.getElementById('startDate');
    const endDateInput = document.getElementById('endDate');
    const minAmountInput = document.getElementById('minAmount');
    const maxAmountInput = document.getElementById('maxAmount');
    
    if (searchInput) {
        searchInput.addEventListener('input', handleSearch);
    }
    if (startDateInput) {
        startDateInput.addEventListener('change', handleSearch);
    }
    if (endDateInput) {
        endDateInput.addEventListener('change', handleSearch);
    }
    if (minAmountInput) {
        minAmountInput.addEventListener('input', handleSearch);
    }
    if (maxAmountInput) {
        maxAmountInput.addEventListener('input', handleSearch);
    }
    
    document.querySelector('.theme-toggle').addEventListener('click', toggleTheme);
    
    document.querySelector('.sidebar-toggle').addEventListener('click', toggleSidebar);

       const refreshTransactionsBtn = document.querySelector('#recentTransactionsRefreshBtn');
    if (refreshTransactionsBtn) {
        refreshTransactionsBtn.addEventListener('click', () => loadTransactions(currentCategory));
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    initializeCategoryFilter();
});