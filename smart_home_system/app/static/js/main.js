// 通用函数
function formatDate(date) {
    return new Date(date).toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatNumber(num) {
    return new Intl.NumberFormat('zh-CN').format(num);
}

// 图表配置
const chartConfig = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            text: '数据统计'
        }
    }
};

// 颜色配置
const chartColors = [
    'rgba(54, 162, 235, 0.5)',
    'rgba(255, 99, 132, 0.5)',
    'rgba(75, 192, 192, 0.5)',
    'rgba(255, 159, 64, 0.5)',
    'rgba(153, 102, 255, 0.5)',
    'rgba(255, 205, 86, 0.5)',
    'rgba(201, 203, 207, 0.5)'
];

// 错误处理
function handleError(error) {
    console.error('Error:', error);
    alert('发生错误，请查看控制台获取详细信息');
} 