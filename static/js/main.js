/**
 * 主界面JavaScript - 修复输入框bug
 */

document.addEventListener('DOMContentLoaded', function() {
    // 修复输入框事件处理
    const commandInput = document.querySelector('#command-input');
    
    if (commandInput) {
        // 移除所有旧的事件监听器
        const newInput = commandInput.cloneNode(true);
        commandInput.parentNode.replaceChild(newInput, commandInput);
        
        // 添加新的事件监听器
        newInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendCommand();
            }
        });
        
        // 确保输入框始终可以获得焦点
        newInput.addEventListener('blur', function() {
            // 不自动清空输入框
        });
    }
});

// 发送命令函数
async function sendCommand() {
    const input = document.querySelector('#command-input');
    const command = input.value.trim();
    
    if (!command) return;
    
    try {
        const response = await fetch('/command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        });
        
        if (response.ok) {
            // 清空输入框
            input.value = '';
            
            // 刷新页面内容
            setTimeout(() => {
                checkNeedRefresh();
            }, 500);
        }
    } catch (error) {
        console.error('Command error:', error);
    }
}

// 检查是否需要刷新
async function checkNeedRefresh() {
    try {
        const response = await fetch('/need_refresh');
        const data = await response.json();
        
        if (data.refresh) {
            // 更新游戏状态
            updateGameStatus();
            updateGameLog();
        }
    } catch (error) {
        console.error('Refresh check error:', error);
    }
}

// 更新游戏状态
async function updateGameStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        // 更新UI元素
        // TODO: 根据实际UI结构更新
        
    } catch (error) {
        console.error('Status update error:', error);
    }
}

// 更新游戏日志
async function updateGameLog() {
    try {
        const response = await fetch('/log');
        const data = await response.json();
        
        // 更新日志显示
        const logContainer = document.querySelector('#narrative-log');
        if (logContainer && data.logs) {
            // TODO: 更新日志显示
        }
        
    } catch (error) {
        console.error('Log update error:', error);
    }
}

// 定期检查更新
setInterval(checkNeedRefresh, 2000);

// 导出全局对象
window.XianXia = window.XianXia || {};
window.XianXia.sendCommand = sendCommand;
window.XianXia.checkNeedRefresh = checkNeedRefresh;
