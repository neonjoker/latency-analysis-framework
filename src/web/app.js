/**
 * 交易链路延时分析 - 前端应用
 */

const API_BASE = 'http://localhost:8000';

// 全局状态
let currentData = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    initializeDates();
    loadCounters();
});

// 初始化日期选择器
function initializeDates() {
    const today = new Date().toISOString().split('T')[0];
    const lastWeek = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    document.getElementById('end-date').value = today;
    document.getElementById('start-date').value = lastWeek;
}

// 加载柜台列表
async function loadCounters() {
    try {
        const response = await fetch(`${API_BASE}/api/counters`);
        const data = await response.json();
        
        const select = document.getElementById('counter-select');
        data.counters.forEach(counter => {
            const option = document.createElement('option');
            option.value = counter;
            option.textContent = counter;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('加载柜台列表失败:', error);
    }
}

// 切换显示区域
function showSection(section) {
    document.getElementById('dashboard-section').classList.add('hidden');
    document.getElementById('data-section').classList.add('hidden');
    document.getElementById('analysis-section').classList.add('hidden');
    
    document.getElementById(`${section}-section`).classList.remove('hidden');
}

// 显示/隐藏加载动画
function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
}

// 加载数据
async function loadData() {
    showLoading(true);
    
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const counter = document.getElementById('counter-select').value;
    
    try {
        const response = await fetch(`${API_BASE}/api/data/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start_date: startDate, end_date: endDate, counters: counter ? [counter] : null })
        });
        
        const result = await response.json();
        
        if (result.success) {
            currentData = result;
            updateDashboard(result);
            updateDataTable(result);
        }
    } catch (error) {
        console.error('加载数据失败:', error);
        alert('加载数据失败：' + error.message);
    } finally {
        showLoading(false);
    }
}

// 更新仪表盘
function updateDashboard(result) {
    document.getElementById('total-rows').textContent = result.row_count.toLocaleString();
    
    // TODO: 计算并更新统计值
    document.getElementById('avg-latency').textContent = '- ms';
    document.getElementById('p95-latency').textContent = '- ms';
    document.getElementById('anomaly-count').textContent = '-';
    
    // 绘制图表
    drawCharts(result.data);
}

// 更新数据表格
function updateDataTable(result) {
    const header = document.getElementById('table-header');
    const body = document.getElementById('table-body');
    
    // 表头
    header.innerHTML = result.columns.slice(0, 10).map(col => 
        `<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">${col}</th>`
    ).join('');
    
    // 表体（限制 100 行）
    body.innerHTML = result.data.slice(0, 100).map(row => 
        `<tr>${result.columns.slice(0, 10).map(col => 
            `<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${row[col] ?? '-'}</td>`
        ).join('')}</tr>`
    ).join('');
}

// 绘制图表
function drawCharts(data) {
    if (!data || data.length === 0) return;
    
    // 延时分布直方图
    const histogramData = data.map(d => d.roundTripTimeMs).filter(v => v !== null);
    Plotly.newPlot('latency-histogram', [{
        x: histogramData,
        type: 'histogram',
        marker: { color: '#3b82f6' }
    }], {
        title: '延时分布',
        xaxis: { title: '延时 (ms)' },
        yaxis: { title: '频数' },
        margin: { t: 40, b: 40, l: 40, r: 20 }
    });
    
    // 时间序列
    const tsData = data.slice(0, 1000);
    Plotly.newPlot('latency-timeseries', [{
        x: tsData.map(d => d.tgwBackTime),
        y: tsData.map(d => d.roundTripTimeMs),
        mode: 'markers',
        type: 'scatter',
        marker: { color: '#10b981', size: 3, opacity: 0.5 }
    }], {
        title: '延时时间序列',
        xaxis: { title: '时间' },
        yaxis: { title: '延时 (ms)' },
        margin: { t: 40, b: 40, l: 40, r: 20 }
    });
    
    // 柜台对比箱线图
    const counters = [...new Set(data.map(d => d.counter).filter(Boolean))];
    const boxData = counters.map(counter => ({
        y: data.filter(d => d.counter === counter).map(d => d.roundTripTimeMs),
        type: 'box',
        name: counter
    }));
    
    Plotly.newPlot('counter-boxplot', boxData, {
        title: '柜台延时对比',
        yaxis: { title: '延时 (ms)' },
        margin: { t: 40, b: 60, l: 40, r: 20 }
    });
    
    // TGW Back vs Out 散点图
    const scatterData = data.slice(0, 1000);
    Plotly.newPlot('back-out-scatter', [{
        x: scatterData.map(d => d.tgwOutTime),
        y: scatterData.map(d => d.tgwBackTime),
        mode: 'markers',
        type: 'scatter',
        marker: { color: '#f59e0b', size: 3, opacity: 0.5 }
    }], {
        title: 'TGW Back vs Out',
        xaxis: { title: 'TGW Out Time' },
        yaxis: { title: 'TGW Back Time' },
        margin: { t: 40, b: 40, l: 40, r: 20 }
    });
}

// 运行异常检测
async function runAnomalyDetection() {
    showLoading(true);
    
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    try {
        const response = await fetch(`${API_BASE}/api/analyze/anomaly`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start_date: startDate, end_date: endDate })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayAnomalyResults(result);
        }
    } catch (error) {
        console.error('异常检测失败:', error);
    } finally {
        showLoading(false);
    }
}

// 显示异常结果
function displayAnomalyResults(result) {
    const container = document.getElementById('anomaly-results');
    const summary = result.summary;
    
    container.innerHTML = `
        <div class="grid grid-cols-4 gap-4">
            <div class="bg-red-50 p-4 rounded">
                <p class="text-sm text-gray-500">总异常数</p>
                <p class="text-2xl font-bold text-red-600">${summary.total_anomalies}</p>
            </div>
            <div class="bg-orange-50 p-4 rounded">
                <p class="text-sm text-gray-500">糖葫芦现象</p>
                <p class="text-2xl font-bold text-orange-600">${summary.by_type.tanghulu || 0}</p>
            </div>
            <div class="bg-yellow-50 p-4 rounded">
                <p class="text-sm text-gray-500">Microburst</p>
                <p class="text-2xl font-bold text-yellow-600">${summary.by_type.microburst || 0}</p>
            </div>
            <div class="bg-purple-50 p-4 rounded">
                <p class="text-sm text-gray-500">链路阻塞</p>
                <p class="text-2xl font-bold text-purple-600">${summary.by_type.link_blockage || 0}</p>
            </div>
        </div>
    `;
}

// 运行聚类分析
async function runClustering() {
    showLoading(true);
    
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    try {
        const response = await fetch(`${API_BASE}/api/analyze/clustering`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start_date: startDate, end_date: endDate })
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayClusterResults(result);
        }
    } catch (error) {
        console.error('聚类分析失败:', error);
    } finally {
        showLoading(false);
    }
}

// 显示聚类结果
function displayClusterResults(result) {
    const container = document.getElementById('cluster-results');
    
    container.innerHTML = `
        <div class="space-y-4">
            <p class="text-lg font-semibold">发现 ${result.clusters.length} 个高延时聚集区</p>
            <p class="text-lg font-semibold">相似链路组：${result.similar_links.length} 组</p>
            ${result.clusters.slice(0, 5).map(c => `
                <div class="bg-blue-50 p-4 rounded">
                    <p class="font-semibold">聚集区 #${c.cluster_id}</p>
                    <p>链路：${c.link_ids.join(', ')}</p>
                    <p>高延时点数：${c.high_latency_count}</p>
                    <p>平均延时：${c.avg_latency_ms.toFixed(2)} ms</p>
                </div>
            `).join('')}
        </div>
    `;
}
