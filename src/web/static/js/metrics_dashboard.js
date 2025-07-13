/**
 * 性能监控仪表板
 */
class MetricsDashboard {
    constructor() {
        this.charts = {};
        this.updateInterval = 5000; // 5秒更新一次
    }
    
    init() {
        this.createCharts();
        this.startUpdating();
    }
    
    createCharts() {
        // CPU使用率图表
        this.charts.cpu = new Chart(document.getElementById('cpuChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU使用率 (%)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // 内存使用率图表
        this.charts.memory = new Chart(document.getElementById('memoryChart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '内存使用率 (%)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
        
        // 请求响应时间图表
        this.charts.responseTime = new Chart(document.getElementById('responseTimeChart'), {
            type: 'bar',
            data: {
                labels: ['p50', 'p90', 'p95', 'p99'],
                datasets: [{
                    label: '响应时间 (ms)',
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(255, 206, 86, 0.2)',
                        'rgba(255, 159, 64, 0.2)',
                        'rgba(255, 99, 132, 0.2)'
                    ],
                    borderColor: [
                        'rgba(75, 192, 192, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(255, 99, 132, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    async updateMetrics() {
        try {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            
            // 更新图表数据
            const now = new Date().toLocaleTimeString();
            
            // CPU图表
            this.addDataPoint(this.charts.cpu, now, data.cpu);
            
            // 内存图表
            this.addDataPoint(this.charts.memory, now, data.memory);
            
            // 响应时间
            if (data.responseTime) {
                this.charts.responseTime.data.datasets[0].data = [
                    data.responseTime.p50,
                    data.responseTime.p90,
                    data.responseTime.p95,
                    data.responseTime.p99
                ];
                this.charts.responseTime.update();
            }
            
        } catch (error) {
            console.error('Failed to update metrics:', error);
        }
    }
    
    addDataPoint(chart, label, value) {
        const maxDataPoints = 20;
        
        chart.data.labels.push(label);
        chart.data.datasets[0].data.push(value);
        
        // 保持最多20个数据点
        if (chart.data.labels.length > maxDataPoints) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }
        
        chart.update();
    }
    
    startUpdating() {
        this.updateMetrics();
        setInterval(() => this.updateMetrics(), this.updateInterval);
    }
}

// 初始化仪表板
document.addEventListener('DOMContentLoaded', () => {
    const dashboard = new MetricsDashboard();
    dashboard.init();
});
