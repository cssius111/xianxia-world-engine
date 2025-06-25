/**
 * 游戏主控制器
 */
const GameUI = {
    /**
     * 初始化游戏UI
     */
    init() {
        console.log('初始化游戏UI...');
        
        // 初始化各个子系统
        this.initEventListeners();
        this.refreshStatus();
        this.startAutoRefresh();
        
        // 显示欢迎消息
        if (window.NarrativeLog) {
            NarrativeLog.addSystem('游戏初始化完成，祝您游戏愉快！');
        }
    },
    
    /**
     * 初始化事件监听器
     */
    initEventListeners() {
        // 监听键盘快捷键
        document.addEventListener('keydown', (e) => {
            // ESC 关闭当前面板
            if (e.key === 'Escape' && window.GamePanels && window.GamePanels.currentPanel) {
                window.GamePanels.closePanel(window.GamePanels.currentPanel);
            }
            
            // Ctrl+S 快速保存
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                if (window.GamePanels) {
                    window.GamePanels.showSaveLoad();
                }
            }
        });
    },
    
    /**
     * 刷新游戏状态
     */
    async refreshStatus() {
        try {
            const response = await fetch('/status');
            const data = await response.json();
            
            if (data.player) {
                // 更新头部信息
                this.updateHeader(data.player, data.location);
                
                // 更新侧边栏状态
                this.updateStats(data.player);
            }
        } catch (error) {
            console.error('刷新状态失败:', error);
        }
    },
    
    /**
     * 更新头部信息
     */
    updateHeader(player, location) {
        const elements = {
            playerName: document.getElementById('playerName'),
            playerRealm: document.getElementById('playerRealm'),
            currentLocation: document.getElementById('currentLocation')
        };
        
        if (elements.playerName) {
            elements.playerName.textContent = player.name || '无名侠客';
        }
        
        if (elements.playerRealm) {
            elements.playerRealm.textContent = player.attributes?.realm_name || '炼气期';
        }
        
        if (elements.currentLocation) {
            elements.currentLocation.textContent = location || '青云城';
        }
    },
    
    /**
     * 更新角色状态条
     */
    updateStats(player) {
        const attrs = player.attributes || {};
        
        // 更新生命值
        const health = {
            current: attrs.current_health || 100,
            max: attrs.max_health || 100
        };
        this.updateStatBar('health', health.current, health.max);
        
        // 更新灵力值
        const mana = {
            current: attrs.current_mana || 50,
            max: attrs.max_mana || 50
        };
        this.updateStatBar('mana', mana.current, mana.max);
        
    },
    
    /**
     * 更新状态条
     */
    updateStatBar(type, current, max) {
        const bar = document.getElementById(`${type}Bar`);
        const text = document.getElementById(`${type}Text`);
        
        if (bar && text) {
            const percentage = Math.max(0, Math.min(100, (current / max) * 100));
            bar.style.width = `${percentage}%`;
            text.textContent = `${current}/${max}`;
        }
    },
    
    /**
     * 开始自动刷新
     */
    startAutoRefresh() {
        // 每30秒自动刷新一次状态
        setInterval(() => {
            this.refreshStatus();
        }, 30000);
    },
    
    /**
     * 发送命令
     * @param {string} command - 要执行的命令
     */
    sendCommand(command) {
        if (window.CommandInput) {
            window.CommandInput.executeCommand(command);
        }
    },
    
    /**
     * 清除游戏数据
     */
    clearGameData() {
        // 清除会话存储
        sessionStorage.clear();
        
        // 清除本地存储中的游戏数据
        const gameKeys = ['playerData', 'gameState', 'lastSave'];
        gameKeys.forEach(key => localStorage.removeItem(key));
        
        console.log('游戏数据已清除');
    },
    
    /**
     * 显示加载动画
     */
    showLoading() {
        // TODO: 实现加载动画
    },
    
    /**
     * 隐藏加载动画
     */
    hideLoading() {
        // TODO: 实现隐藏加载动画
    }
};

/**
 * 欢迎系统（用于游戏主界面）
 */
const WelcomeSystem = {
    /**
     * 显示欢迎界面
     */
    show() {
        // 检查是否是新会话
        const isNewSession = !sessionStorage.getItem('welcomeShown');
        
        if (isNewSession && window.GameLauncher) {
            // 标记已显示
            sessionStorage.setItem('welcomeShown', 'true');
            
            // 显示欢迎页面
            window.GameLauncher.show();
        }
    }
};

// 导出到全局
window.GameUI = GameUI;
window.WelcomeSystem = WelcomeSystem;

// 确保 DOM 加载完成后再初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM 加载完成，准备初始化游戏...');
    });
} else {
    console.log('DOM 已就绪');
}
