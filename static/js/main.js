// Trading Signals Pro - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Load initial data
    loadSignals();
    loadStats();
    
    // Set up auto-refresh
    setInterval(loadSignals, 30000); // 30 seconds
    setInterval(loadStats, 60000); // 1 minute
    
    // Initialize event listeners
    initializeEventListeners();
}

function initializeEventListeners() {
    // Filter changes
    document.getElementById('timeframeFilter').addEventListener('change', filterSignals);
    document.getElementById('directionFilter').addEventListener('change', filterSignals);
    document.getElementById('statusFilter').addEventListener('change', filterSignals);
    
    // Search functionality
    document.getElementById('searchInput').addEventListener('input', filterSignals);
}

async function loadSignals() {
    try {
        showLoading('signalsBody');
        
        const response = await fetch('/api/signals');
        if (!response.ok) throw new Error('Network error');
        
        const signals = await response.json();
        renderSignals(signals);
        
    } catch (error) {
        console.error('Error loading signals:', error);
        showError('signalsBody', 'Không thể tải tín hiệu. Vui lòng thử lại.');
    }
}

function renderSignals(signals) {
    const tbody = document.getElementById('signalsBody');
    
    if (signals.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="text-center py-4">
                    <i class="fas fa-moon fs-1 text-muted mb-3"></i>
                    <p class="text-muted">Chưa có tín hiệu nào. Vui lòng quay lại sau.</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = signals.map(signal => `
        <tr class="signal-row ${signal.is_new ? 'new-signal' : ''}" data-signal-id="${signal.id}">
            <td>
                <small class="text-muted">${formatTime(signal.timestamp)}</small>
            </td>
            <td>
                <span class="fw-bold">${signal.coin.replace('USDT', '')}</span>
            </td>
            <td>
                <span class="direction-${signal.direction.toLowerCase()}">
                    ${signal.direction}
                </span>
            </td>
            <td class="fw-bold">${formatPrice(signal.entry)}</td>
            <td class="text-success">${formatPrice(signal.tp)}</td>
            <td class="text-danger">${formatPrice(signal.sl)}</td>
            <td>
                <span class="badge bg-dark">1:${signal.rr}</span>
            </td>
            <td>
                <div class="d-flex align-items-center">
                    <span>${signal.combo_name}</span>
                    <button class="btn btn-sm btn-link text-info p-0 ms-1" 
                            onclick="showComboDetails('${signal.id}')"
                            data-bs-toggle="tooltip" title="Xem chi tiết combo">
                        <i class="fas fa-info-circle"></i>
                    </button>
                    ${signal.created_by ? `<small class="text-muted ms-1">(${signal.created_by})</small>` : ''}
                </div>
            </td>
            <td>
                <div class="vote-buttons" data-signal-id="${signal.id}">
                    ${renderVoteButtons(signal)}
                </div>
            </td>
        </tr>
    `).join('');
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
}

function renderVoteButtons(signal) {
    const hasVoted = getVotedSignals().includes(signal.id);
    
    if (hasVoted) {
        return `
            <div class="text-center">
                <small class="text-success">
                    <i class="fas fa-check me-1"></i>Đã vote
                </small>
                <div class="mt-1">
                    <span class="badge bg-success me-1">${signal.votes_win}</span>
                    <span class="badge bg-danger">${signal.votes_lose}</span>
                </div>
            </div>
        `;
    }
    
    return `
        <div class="btn-group btn-group-sm">
            <button class="btn btn-outline-success" onclick="voteSignal('${signal.id}', 'win')"
                    data-bs-toggle="tooltip" title="Vote Win">
                <i class="fas fa-check"></i> ${signal.votes_win}
            </button>
            <button class="btn btn-outline-danger" onclick="voteSignal('${signal.id}', 'lose')"
                    data-bs-toggle="tooltip" title="Vote Lose">
                <i class="fas fa-times"></i> ${signal.votes_lose}
            </button>
        </div>
    `;
}

async function voteSignal(signalId, voteType) {
    try {
        const response = await fetch(`/api/vote/${signalId}/${voteType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast('success', result.message);
            addVotedSignal(signalId);
            loadSignals(); // Reload signals
            loadStats(); // Reload stats
        } else {
            showToast('error', result.error || 'Lỗi khi vote');
        }
    } catch (error) {
        console.error('Vote error:', error);
        showToast('error', 'Lỗi kết nối khi vote');
    }
}

function showComboDetails(signalId) {
    // Implementation for showing combo details modal
    const modal = new bootstrap.Modal(document.getElementById('comboModal'));
    modal.show();
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('d-none');
    });
    
    // Show selected section
    document.getElementById(`${sectionId}-section`).classList.remove('d-none');
    
    // Update active nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Utility functions
function formatTime(isoString) {
    return new Date(isoString).toLocaleString('vi-VN');
}

function formatPrice(price) {
    return parseFloat(price).toFixed(4);
}

function showToast(type, message) {
    // Implementation for toast notifications
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.getElementById('toastContainer').appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
}

// Voting storage
function getVotedSignals() {
    return JSON.parse(localStorage.getItem('votedSignals') || '[]');
}

function addVotedSignal(signalId) {
    const voted = getVotedSignals();
    if (!voted.includes(signalId)) {
        voted.push(signalId);
        localStorage.setItem('votedSignals', JSON.stringify(voted));
    }
}
