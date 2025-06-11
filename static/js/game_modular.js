// 游戏主模块 - ES6模块化版本
import { stateManager } from './modules/state.js';
import { apiClient } from './modules/api.js';
import { logManager } from './modules/log.js';
import { CommandHandler } from './modules/command.js';

// 创建命令处理器实例
const commandHandler = new CommandHandler(stateManager, apiClient, logManager);

// 初始化教程
function initTutorial() {
    const state = stateManager.getState();
    
    if (state.isNewPlayer && state.tutorialStep === 0) {
        setTimeout(() => {
            hideLoading();
            // 创建欢迎日志组
            logManager.startLogGroup('新手引导');
            logManager.addLog('msg-system', '【系统】欢迎进入修仙世界。你将扮演一位凡人，踏入仙途。');
            logManager.addLog('msg-event', '【剧情】你出生在青云山下的一个普通村落。十六岁那年，一位游方道人路过，发现你有修炼资质，便传授了一卷《基础吐纳诀》。从此，你踏上了修仙之路……');
            logManager.addLog('msg-tip tutorial-highlight', '[提示] 你可以输入"修炼"、"背包"、"探索"等指令开始游戏。试试输入"状态"查看你的角色信息。');
            logManager.finishLogGroup();
            
            // Roll角色事件
            triggerRollEvent();
            stateManager.setState({ tutorialStep: 1 });
        }, 1000);
    } else {
        setTimeout(() => {
            hideLoading();
            commandHandler.updateGameState();
        }, 500);
    }
}

// 隐藏加载动画
function hideLoading() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
}

// 触发Roll角色事件
function triggerRollEvent() {
    const eventHtml = `
        <div class="event-container">
            <div class="event-title">【命运抉择】</div>
            <div class="event-content">
                道人掐指一算，说道："你的命格特殊，有三种可能的发展方向。选择你的道路吧。"
            </div>
            <div class="event-choices">
                <button class="event-choice" onclick="GameUI.makeEventChoice(0)">1. 剑修之路 - 攻击力提升，但防御较弱</button>
                <button class="event-choice" onclick="GameUI.makeEventChoice(1)">2. 体修之路 - 防御力超强，但速度较慢</button>
                <button class="event-choice" onclick="GameUI.makeEventChoice(2)">3. 法修之路 - 灵力充沛，但体质较弱</button>
            </div>
        </div>
    `;
    logManager.addHtmlLog(eventHtml);
}

// 事件选择
async function makeEventChoice(choiceIndex) {
    const choices = ['剑修之路', '体修之路', '法修之路'];
    logManager.startLogGroup('命运选择');
    logManager.addLog('msg-player', `➤ 选择：${choices[choiceIndex]}`);
    
    // 移除事件容器
    const eventContainers = document.querySelectorAll('.event-container');
    eventContainers.forEach(container => container.style.display = 'none');
    
    // 发送选择到服务器
    try {
        await apiClient.sendCommand(`选择 ${choiceIndex + 1}`);
        
        // 刷新状态和日志
        await commandHandler.updateGameState();
    } catch (error) {
        console.error('发送选择失败:', error);
    }
    
    const state = stateManager.getState();
    if (state.tutorialStep === 1) {
        setTimeout(() => {
            logManager.addLog('msg-tip', '[提示] 很好！你已经选择了自己的道路。现在试试输入"状态"查看你的角色信息。');
            stateManager.setState({ tutorialStep: 2 });
            logManager.finishLogGroup();
        }, 1000);
    } else {
        logManager.finishLogGroup();
    }
}

// 智能刷新
async function checkUpdates() {
    const state = stateManager.getState();
    
    // 如果用户正在交互，跳过自动刷新
    if (state.isUserInteracting) return;
    
    try {
        const data = await apiClient.checkNeedRefresh();
        if (data.refresh && data.last_update > state.lastUpdateTime) {
            stateManager.setState({ lastUpdateTime: data.last_update });
            await commandHandler.updateGameState();
        }
    } catch (error) {
        console.error('检查更新失败:', error);
    }
}

// 自动完成功能
class AutoComplete {
    constructor(commandHandler) {
        this.commandHandler = commandHandler;
        this.input = document.getElementById('command-input');
        this.autocomplete = document.getElementById('autocomplete');
    }
    
    show() {
        if (!this.input || !this.autocomplete) return;
        
        const value = this.input.value.toLowerCase().trim();
        this.autocomplete.innerHTML = '';
        
        if (value.length === 0) {
            // 显示常用命令
            const commonCmds = ['状态', '修炼', '探索', '背包', '帮助'];
            commonCmds.forEach(cmd => {
                const cmdInfo = this.commandHandler.availableCommands.find(c => c.cmd === cmd);
                if (cmdInfo) {
                    this.addItem(cmd, cmdInfo.desc);
                }
            });
        } else {
            // 匹配命令
            const matches = this.commandHandler.availableCommands.filter(cmd => 
                cmd.cmd.toLowerCase().includes(value) ||
                cmd.desc.toLowerCase().includes(value)
            );
            
            matches.slice(0, 8).forEach(cmd => {
                this.addItem(cmd.cmd, cmd.desc);
            });
        }
        
        if (this.autocomplete.children.length > 0) {
            this.autocomplete.style.display = 'block';
        } else {
            this.autocomplete.style.display = 'none';
        }
    }
    
    addItem(command, desc) {
        if (!this.autocomplete) return;
        
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.dataset.command = command;
        item.innerHTML = `${command}<span class="autocomplete-desc">${desc}</span>`;
        item.onclick = () => {
            if (this.input) {
                this.input.value = command;
                this.autocomplete.style.display = 'none';
                this.input.focus();
            }
        };
        this.autocomplete.appendChild(item);
    }
    
    hide() {
        if (this.autocomplete) {
            this.autocomplete.style.display = 'none';
        }
    }
}

const autoComplete = new AutoComplete(commandHandler);

// 键盘输入处理
function handleKeyDown(event) {
    const input = event.target;
    const state = stateManager.getState();
    
    // Tab键 - 显示/选择自动完成
    if (event.key === 'Tab') {
        event.preventDefault();
        const autocomplete = document.getElementById('autocomplete');
        if (autocomplete && autocomplete.style.display === 'block' && autocomplete.children.length > 0) {
            // 选择第一个建议
            const firstItem = autocomplete.children[0];
            if (firstItem && firstItem.dataset.command) {
                input.value = firstItem.dataset.command;
                autoComplete.hide();
            }
        } else {
            autoComplete.show();
        }
    }
    // 方向键 - 历史记录
    else if (event.key === 'ArrowUp') {
        event.preventDefault();
        if (state.historyIndex > 0) {
            stateManager.setState({ historyIndex: state.historyIndex - 1 });
            input.value = state.commandHistory[state.historyIndex - 1];
        }
    } else if (event.key === 'ArrowDown') {
        event.preventDefault();
        if (state.historyIndex < state.commandHistory.length - 1) {
            stateManager.setState({ historyIndex: state.historyIndex + 1 });
            input.value = state.commandHistory[state.historyIndex + 1];
        } else {
            stateManager.setState({ historyIndex: state.commandHistory.length });
            input.value = '';
        }
    }
    // ESC - 关闭自动完成
    else if (event.key === 'Escape') {
        autoComplete.hide();
    }
    // Enter - 执行命令
    else if (event.key === 'Enter') {
        commandHandler.executeCommand();
    }
}

function handleKeyUp(event) {
    // 快捷键
    if (event.altKey || event.ctrlKey) {
        const key = event.key.toLowerCase();
        const cmd = commandHandler.availableCommands.find(c => c.shortcut === key);
        if (cmd) {
            commandHandler.sendCommand(cmd.cmd);
            return;
        }
    }
    
    // 输入时更新自动完成
    if (!['Tab', 'Enter', 'Escape', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
        autoComplete.show();
    }
}

// 工具提示
function showTooltip(element, text) {
    const tooltip = document.getElementById('tooltip');
    if (!tooltip || !element) return;
    
    const rect = element.getBoundingClientRect();
    tooltip.textContent = text;
    tooltip.style.left = rect.left + 'px';
    tooltip.style.top = (rect.top - 30) + 'px';
    tooltip.classList.add('show');
}

function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    if (tooltip) {
        tooltip.classList.remove('show');
    }
}

// 初始化
function init() {
    // 聚焦输入框
    const input = document.getElementById('command-input');
    if (input) {
        input.focus();
        
        // 绑定事件
        input.addEventListener('keydown', handleKeyDown);
        input.addEventListener('keyup', handleKeyUp);
    }
    
    // 初始化教程
    initTutorial();
    
    // 获取初始状态
    commandHandler.updateStatus();
    commandHandler.updateAchievementDisplay();
    
    // 智能刷新
    setInterval(checkUpdates, 5000);
    
    // 定期随机事件
    setInterval(() => {
        const state = stateManager.getState();
        if (Math.random() < 0.05 && !state.isNewPlayer && !state.isUserInteracting) {
            const ambientEvents = [
                '【剧情】山风徐来，带着淡淡的草药香。',
                '【剧情】远处传来仙鹤的清鸣声。',
                '【剧情】天边有流光划过，似是有修士御剑而行。',
                '【剧情】夜色渐深，星河璀璨。',
                '【剧情】灵气波动异常，似乎有宝物出世。',
                '【剧情】远山传来阵阵钟声，那是某个宗门的晚课。'
            ];
            logManager.startLogGroup('环境描述');
            logManager.addLog('msg-event', ambientEvents[Math.floor(Math.random() * ambientEvents.length)]);
            logManager.finishLogGroup();
        }
    }, 60000);
    
    // 点击空白处隐藏自动完成
    document.addEventListener('click', (e) => {
        if (!e.target.matches('.command-input')) {
            autoComplete.hide();
        }
    });
    
    // 快捷键提示
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('mouseenter', function() {
            const shortcut = this.querySelector('.shortcut');
            if (shortcut) {
                showTooltip(this, `快捷键: Alt+${shortcut.textContent}`);
            }
        });
        link.addEventListener('mouseleave', hideTooltip);
    });
    
    // 防止页面滑动时消失
    document.addEventListener('touchmove', function(e) {
        // 只允许在可滚动区域内滑动
        if (!e.target.closest('.narrative-log') && !e.target.closest('.sidebar')) {
            e.preventDefault();
        }
    }, { passive: false });
}

// 导出公共接口
window.GameUI = {
    init,
    sendCommand: (cmd) => commandHandler.sendCommand(cmd),
    executeCommand: () => commandHandler.executeCommand(),
    makeEventChoice,
    showTooltip,
    hideTooltip,
    handleKeyDown,
    handleKeyUp
};

// 页面加载完成
window.addEventListener('load', init);

// 页面可见性变化时的处理
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // 页面重新显示时检查更新
        setTimeout(checkUpdates, 500);
    }
});
