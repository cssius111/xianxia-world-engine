// 日志管理模块
export class LogManager {
    constructor(containerId = 'narrative-log') {
        this.container = document.getElementById(containerId);
        this.currentLogGroup = null;
        this.logGroupTimer = null;
    }
    
    // 开始新的日志组
    startLogGroup(title) {
        // 如果有未完成的日志组，先完成它
        if (this.currentLogGroup) {
            this.finishLogGroup();
        }
        
        const group = document.createElement('div');
        group.className = 'log-group';
        
        if (title) {
            const header = document.createElement('div');
            header.className = 'log-group-header';
            const timestamp = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            header.textContent = `${title} - ${timestamp}`;
            group.appendChild(header);
        }
        
        this.container.appendChild(group);
        this.currentLogGroup = group;
        
        // 设置定时器，超过3秒自动结束日志组
        clearTimeout(this.logGroupTimer);
        this.logGroupTimer = setTimeout(() => {
            this.finishLogGroup();
        }, 3000);
    }
    
    // 完成当前日志组
    finishLogGroup() {
        if (this.currentLogGroup) {
            this.currentLogGroup = null;
            clearTimeout(this.logGroupTimer);
        }
    }
    
    // 添加日志条目
    addLog(className, text) {
        // 如果没有当前日志组，创建一个
        if (!this.currentLogGroup) {
            this.startLogGroup();
        }
        
        const entry = document.createElement('div');
        entry.className = `log-entry ${className}`;
        entry.textContent = text;
        
        this.currentLogGroup.appendChild(entry);
        
        // 延迟滚动，等待动画开始
        setTimeout(() => {
            if (this.container) {
                this.container.scrollTop = this.container.scrollHeight;
            }
        }, 100);
    }
    
    // 添加HTML日志
    addHtmlLog(html) {
        if (!this.container) return;
        
        const entry = document.createElement('div');
        entry.innerHTML = html;
        
        this.container.appendChild(entry);
        
        setTimeout(() => {
            this.container.scrollTop = this.container.scrollHeight;
        }, 100);
    }
    
    // 清空日志
    clearLogs() {
        if (this.container) {
            this.container.innerHTML = '';
        }
        this.currentLogGroup = null;
        clearTimeout(this.logGroupTimer);
    }
    
    // 从日志数组创建日志组
    createLogGroupFromLogs(type, logs) {
        if (!this.container) return;
        
        const group = document.createElement('div');
        group.className = 'log-group';
        
        // 根据类型添加标题
        const titles = {
            'system': '系统消息',
            'event': '剧情发展',
            'combat': '战斗记录',
            'reward': '奖励获得',
            'tip': '游戏提示',
            'warning': '重要警告',
            'player': '玩家行动'
        };
        
        if (titles[type]) {
            const header = document.createElement('div');
            header.className = 'log-group-header';
            header.textContent = titles[type];
            group.appendChild(header);
        }
        
        // 添加日志条目
        logs.forEach(text => {
            let className = 'log-entry';
            if (text.startsWith('【系统】')) className += ' msg-system';
            else if (text.startsWith('【剧情】')) className += ' msg-event';
            else if (text.startsWith('【战斗】')) className += ' msg-combat';
            else if (text.startsWith('【奖励】')) className += ' msg-reward';
            else if (text.startsWith('[提示]')) className += ' msg-tip';
            else if (text.startsWith('【警告】')) className += ' msg-warning';
            else if (text.startsWith('➤')) className += ' msg-player';

            const entry = document.createElement('div');
            entry.className = className;
            entry.textContent = text;
            group.appendChild(entry);
        });
        
        this.container.appendChild(group);
    }
    
    // 显示成就
    showAchievement(title, desc) {
        const achievementHtml = `
            <div class="msg-achievement">
                🏆 成就解锁：${title}
                <div style="font-size: 13px; margin-top: 5px; color: #ccc;">${desc}</div>
            </div>
        `;
        
        if (!this.container) return;
        
        const achievement = document.createElement('div');
        achievement.innerHTML = achievementHtml;
        this.container.appendChild(achievement.firstElementChild);
        
        setTimeout(() => {
            this.container.scrollTop = this.container.scrollHeight;
        }, 100);
    }
}

// 创建单例实例
export const logManager = new LogManager();
