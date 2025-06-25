/**
 * 修仙世界引擎 - 优化版游戏客户端
 * 版本: 2.0.0
 * 更新: 2025-06-22
 */

class XianxiaGameClient {
    constructor() {
        this.gameState = {
            isNewPlayer: true,
            tutorialStep: 0,
            commandCount: 0,
            visitedAreas: new Set(['青云山']),
            commandHistory: [],
            historyIndex: -1,
            currentEvent: null,
            achievementUnlocked: 0,
            achievementTotal: 30,
            currentLogGroup: null,
            logGroupTimer: null,
            needsRefresh: false,
            isUserInteracting: false,
            lastUpdateTime: 0,
            devMode: false
        };

        this.lastKnownStatus = null;
        this.availableCommands = [];
        this.initializeCommands();
        this.bindEvents();
    }

    // 初始化可用命令
    initializeCommands() {
        this.availableCommands = [
            { cmd: '状态', desc: '查看角色状态', shortcut: 's' },
            { cmd: '修炼', desc: '打坐修炼', shortcut: 'c' },
            { cmd: '探索', desc: '探索当前区域', shortcut: 'e' },
            { cmd: '背包', desc: '查看物品', shortcut: 'b' },
            { cmd: '功法', desc: '查看技能', shortcut: 'k' },
            { cmd: '地图', desc: '查看地图', shortcut: 'm' },
            { cmd: '帮助', desc: '显示帮助', shortcut: 'h' },
            { cmd: '攻击', desc: '攻击目标', shortcut: 'a' },
            { cmd: '防御', desc: '防御姿态', shortcut: 'd' },
            { cmd: '使用', desc: '使用物品', shortcut: 'u' },
            { cmd: '对话', desc: '与NPC交谈', shortcut: 't' },
            { cmd: '商店', desc: '查看商店', shortcut: null },
            { cmd: '任务', desc: '查看任务', shortcut: 'q' },
            { cmd: '成就', desc: '查看成就', shortcut: null },
            { cmd: '保存', desc: '保存游戏', shortcut: null },
            { cmd: '退出', desc: '退出游戏', shortcut: null }
        ];
    }

    // 绑定事件
    bindEvents() {
        // 页面加载完成
        document.addEventListener('DOMContentLoaded', () => {
            this.init();
        });

        // 页面可见性变化
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                setTimeout(() => this.checkUpdates(), 500);
            }
        });

        // 点击空白处隐藏自动完成
        document.addEventListener('click', (e) => {
            if (!e.target.matches('.command-input')) {
                this.hideAutocomplete();
            }
        });

        // 防止页面滑动时消失
        document.addEventListener('touchmove', (e) => {
            if (!e.target.closest('.narrative-log') && !e.target.closest('.sidebar')) {
                e.preventDefault();
            }
        }, { passive: false });
    }

    // 初始化游戏
    init() {
        this.gameState.devMode = window.devMode || false;
        
        if (this.gameState.devMode) {
            console.log('[DEV] 修仙世界引擎 - 开发模式已启用');
            console.log('[DEV] 初始状态:', this.gameState);
            console.log('[DEV] 可用命令:', this.availableCommands);
        }

        // 聚焦输入框
        const input = document.getElementById('command-input');
        if (input) {
            input.focus();
            input.addEventListener('keydown', (e) => this.handleKeyDown(e));
            input.addEventListener('keyup', (e) => this.handleKeyUp(e));
        }

        // 绑定提交按钮
        const submitBtn = document.querySelector('.command-submit');
        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.executeCommand());
        }

        // 初始化教程
        this.initTutorial();

        // 获取初始状态
        this.fetchStatus();
        this.updateAchievementDisplay();

        // 启动定时器
        this.startTimers();

        // 绑定模态框事件
        this.bindModalEvents();
    }

    // 启动定时器
    startTimers() {
        // 智能刷新 - 降低频率
        setInterval(() => this.checkUpdates(), 5000);

        // 随机环境事件 - 降低频率
        setInterval(() => {
            if (Math.random() < 0.05 && !this.gameState.isNewPlayer && !this.gameState.isUserInteracting) {
                this.triggerAmbientEvent();
            }
        }, 60000);
    }

    // 绑定模态框相关事件
    bindModalEvents() {
        // 功能网格点击事件
        document.querySelectorAll('.function-link').forEach(link => {
            link.addEventListener('click', (e) => {
                const modalName = e.target.textContent.trim();
                const modalMap = {
                    '状态': 'status',
                    '背包': 'inventory',
                    '修炼': 'cultivation',
                    '成就': 'achievement',
                    '探索': 'exploration',
                    '地图': 'map',
                    '任务': 'quest',
                    '保存': 'save',
                    '加载': 'load',
                    '帮助': 'help',
                    '设定': 'settings',
                    '退出': 'exit'
                };
                
                if (modalMap[modalName]) {
                    this.openModal(modalMap[modalName]);
                }
            });
        });

        // 模态框关闭事件
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal') || e.target.classList.contains('modal-close')) {
                this.closeModal();
            }
        });

        // ESC键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
                this.hideAutocomplete();
            }
        });
    }

    // 初始化新手引导
    initTutorial() {
        if (this.gameState.isNewPlayer && this.gameState.tutorialStep === 0) {
            setTimeout(() => {
                this.hideLoading();
                this.startLogGroup('新手引导');
                this.addLog('msg-system', '【系统】欢迎进入修仙世界。你将扮演一位凡人，踏入仙途。');
                this.addLog('msg-event', '【剧情】你出生在青云山下的一个普通村落。十六岁那年，一位游方道人路过，发现你有修炼资质，便传授了一卷《基础吐纳诀》。从此，你踏上了修仙之路……');
                this.addLog('msg-tip tutorial-highlight', '[提示] 你可以输入"修炼"、"背包"、"探索"等指令开始游戏。试试输入"状态"查看你的角色信息。');
                this.finishLogGroup();
                this.triggerRollEvent();
                this.gameState.tutorialStep = 1;
            }, 1000);
        } else {
            setTimeout(() => {
                this.hideLoading();
                this.fetchLog();
            }, 500);
        }
    }

    // 隐藏加载动画
    hideLoading() {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    // 创建日志组
    startLogGroup(title) {
        if (this.gameState.currentLogGroup) {
            this.finishLogGroup();
        }

        const log = document.getElementById('narrative-log');
        if (!log) return;

        const group = document.createElement('div');
        group.className = 'log-group';

        if (title) {
            const header = document.createElement('div');
            header.className = 'log-group-header';
            const timestamp = new Date().toLocaleTimeString('zh-CN', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            header.textContent = `${title} - ${timestamp}`;
            group.appendChild(header);
        }

        log.appendChild(group);
        this.gameState.currentLogGroup = group;

        clearTimeout(this.gameState.logGroupTimer);
        this.gameState.logGroupTimer = setTimeout(() => {
            this.finishLogGroup();
        }, 3000);
    }

    // 完成日志组
    finishLogGroup() {
        if (this.gameState.currentLogGroup) {
            this.gameState.currentLogGroup = null;
            clearTimeout(this.gameState.logGroupTimer);
        }
    }

    // 添加日志
    addLog(className, text) {
        if (!this.gameState.currentLogGroup) {
            this.startLogGroup();
        }

        const entry = document.createElement('div');
        entry.className = `log-entry ${className}`;
        entry.textContent = text;

        this.gameState.currentLogGroup.appendChild(entry);

        setTimeout(() => {
            const log = document.getElementById('narrative-log');
            if (log) {
                log.scrollTop = log.scrollHeight;
            }
        }, 100);
    }

    // 添加HTML日志
    addHtmlLog(html) {
        const log = document.getElementById('narrative-log');
        if (!log) return;

        const entry = document.createElement('div');
        entry.innerHTML = html;
        log.appendChild(entry);

        setTimeout(() => {
            log.scrollTop = log.scrollHeight;
        }, 100);
    }

    // 触发角色选择事件
    triggerRollEvent() {
        const eventHtml = `
            <div class="event-container">
                <div class="event-title">【命运抉择】</div>
                <div class="event-content">
                    道人掐指一算，说道："你的命格特殊，有三种可能的发展方向。选择你的道路吧。"
                </div>
                <div class="event-choices">
                    <button class="event-choice" onclick="gameClient.makeEventChoice(0)">1. 剑修之路 - 攻击力提升，但防御较弱</button>
                    <button class="event-choice" onclick="gameClient.makeEventChoice(1)">2. 体修之路 - 防御力超强，但速度较慢</button>
                    <button class="event-choice" onclick="gameClient.makeEventChoice(2)">3. 法修之路 - 灵力充沛，但体质较弱</button>
                </div>
            </div>
        `;
        this.addHtmlLog(eventHtml);
    }

    // 处理事件选择
    async makeEventChoice(choiceIndex) {
        const choices = ['剑修之路', '体修之路', '法修之路'];
        this.startLogGroup('命运选择');
        this.addLog('msg-player', `➤ 选择：${choices[choiceIndex]}`);

        // 移除事件容器
        document.querySelectorAll('.event-container').forEach(container => {
            container.style.display = 'none';
        });

        try {
            await this.sendCommand(`选择 ${choiceIndex + 1}`);
            await this.fetchLog();
            await this.fetchStatus();
        } catch (error) {
            console.error('发送选择失败:', error);
        }

        if (this.gameState.tutorialStep === 1) {
            setTimeout(() => {
                this.addLog('msg-tip', '[提示] 很好！你已经选择了自己的道路。现在试试输入"状态"查看你的角色信息。');
                this.gameState.tutorialStep = 2;
                this.finishLogGroup();
            }, 1000);
        } else {
            this.finishLogGroup();
        }
    }

    // 执行命令
    async executeCommand() {
        const input = document.getElementById('command-input');
        const command = input?.value?.trim();

        if (!command) return;

        if (this.gameState.devMode) {
            console.log('[DEV] 执行命令:', command);
            console.log('[DEV] 当前状态:', this.gameState);
        }

        this.gameState.isUserInteracting = true;
        this.hideAutocomplete();

        // 添加到历史记录
        if (this.gameState.commandHistory[this.gameState.commandHistory.length - 1] !== command) {
            this.gameState.commandHistory.push(command);
            if (this.gameState.commandHistory.length > 50) {
                this.gameState.commandHistory.shift();
            }
        }
        this.gameState.historyIndex = this.gameState.commandHistory.length;

        // 创建玩家命令日志组
        this.startLogGroup('玩家指令');
        this.addLog('msg-player', `➤ ${command}`);
        this.gameState.commandCount++;

        try {
            await this.sendCommand(command);
            input.value = '';
            input.focus();

            setTimeout(() => this.finishLogGroup(), 100);

            await this.fetchLog();
            await this.fetchStatus();
            this.checkTutorialProgress(command);

        } catch (error) {
            console.error('执行命令失败:', error);
            this.startLogGroup('系统错误');
            this.addLog('msg-warning', '【系统】命令执行失败，请稍后重试。');
            this.finishLogGroup();
        } finally {
            setTimeout(() => {
                this.gameState.isUserInteracting = false;
            }, 1000);
        }
    }

    // 发送命令到服务器
    async sendCommand(command) {
        const response = await fetch('/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    // 检查教程进度
    checkTutorialProgress(command) {
        const cmd = command.toLowerCase();

        if (this.gameState.isNewPlayer) {
            if (this.gameState.tutorialStep === 2 && (cmd === '状态' || cmd === 's')) {
                setTimeout(() => {
                    this.startLogGroup('教程提示');
                    this.addLog('msg-tip', '[提示] 很好！你已经了解了自己的状态。现在试试输入"修炼"来提升修为。');
                    this.finishLogGroup();
                    this.gameState.tutorialStep = 3;
                }, 1000);
            } else if (this.gameState.tutorialStep === 3 && (cmd === '修炼' || cmd === 'c')) {
                setTimeout(() => {
                    this.startLogGroup('教程提示');
                    this.addLog('msg-tip', '[提示] 修炼可以增加修为，当修为达到上限时就能突破境界。接下来试试"探索"周围环境。');
                    this.finishLogGroup();
                    this.gameState.tutorialStep = 4;
                }, 3000);
            } else if (this.gameState.tutorialStep === 4 && (cmd === '探索' || cmd === 'e')) {
                setTimeout(() => {
                    this.startLogGroup('教程完成');
                    this.addLog('msg-tip', '[提示] 探索可以发现各种机缘和事件。你已经掌握了基本操作，祝你修仙之路一帆风顺！');
                    this.addLog('msg-tip', '[提示] 提示：按Tab键可以显示命令提示，使用方向键可以浏览历史命令。');
                    this.finishLogGroup();
                    this.gameState.tutorialStep = 5;
                    this.gameState.isNewPlayer = false;
                    this.showAchievement('初入江湖', '完成新手教程');
                }, 2000);
            }
        }
    }

    // 显示成就
    showAchievement(title, desc) {
        const achievementHtml = `
            <div class="msg-achievement">
                🏆 成就解锁：${title}
                <div style="font-size: 13px; margin-top: 5px; color: #ccc;">${desc}</div>
            </div>
        `;

        const log = document.getElementById('narrative-log');
        if (!log) return;

        const achievement = document.createElement('div');
        achievement.innerHTML = achievementHtml;
        log.appendChild(achievement.firstElementChild);

        this.gameState.achievementUnlocked++;
        this.updateAchievementDisplay();

        setTimeout(() => {
            log.scrollTop = log.scrollHeight;
        }, 100);
    }

    // 更新成就显示
    updateAchievementDisplay() {
        const countElement = document.getElementById('achievement-count');
        const pointsElement = document.getElementById('achievement-points');

        if (countElement) {
            countElement.textContent = `${this.gameState.achievementUnlocked}/${this.gameState.achievementTotal}`;
        }
        if (pointsElement) {
            pointsElement.textContent = this.gameState.achievementUnlocked * 10;
        }
    }

    // 获取状态
    async fetchStatus() {
        try {
            const response = await fetch('/status');
            if (!response.ok) throw new Error('获取状态失败');

            const data = await response.json();
            const player = data.player;
            if (!player) return;

            if (this.gameState.devMode) {
                console.log('[DEV] 状态数据:', data);
                console.log('[DEV] 玩家属性:', player.attributes);
            }

            this.updatePlayerDisplay(player, data);
        } catch (error) {
            console.error('获取状态失败:', error);
        }
    }

    // 更新玩家显示
    updatePlayerDisplay(player, data) {
        const attrs = player.attributes;

        // 安全更新元素
        this.updateElement('player-name', player.name || '无名侠客');
        this.updateElement('realm', attrs.realm_name || '炼气一层');
        this.updateElement('realm-progress', `(${attrs.realm_progress || 0} %)`);

        // 确保数值在合理范围内
        const curHealth = Math.max(0, Math.min(attrs.current_health || 0, attrs.max_health || 0));
        const curMana = Math.max(0, Math.min(attrs.current_mana || 0, attrs.max_mana || 0));

        this.updateElement('health', `${curHealth} / ${attrs.max_health || 0}`);
        this.updateElement('mana', `${curMana} / ${attrs.max_mana || 0}`);

        // 更新进度条
        this.updateProgressBar('health-progress', curHealth, attrs.max_health);
        this.updateProgressBar('mana-progress', curMana, attrs.max_mana);

        // 更新位置和金币
        this.updateElement('location', data.location_name || data.location || '青云城');
        this.updateElement('gold', data.gold || 0);

        // 检查警告
        this.checkHealthWarning(curHealth, attrs.max_health);
    }

    // 安全更新元素
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }

    // 更新进度条
    updateProgressBar(id, current, max) {
        const bar = document.getElementById(id);
        if (bar && max > 0) {
            const percent = Math.min(100, Math.max(0, (current / max * 100)));
            bar.style.width = `${percent}%`;
        }
    }

    // 检查血量警告
    checkHealthWarning(current, max) {
        if (max > 0 && current / max < 0.3) {
            if (!document.querySelector('.health-warning-active')) {
                this.startLogGroup('系统警告');
                this.addLog('msg-warning health-warning-active', '【警告】你的气血值过低，请及时恢复！');
                this.finishLogGroup();
            }
        }
    }

    // 获取日志
    async fetchLog() {
        try {
            const response = await fetch('/log');
            if (!response.ok) throw new Error('获取日志失败');

            const data = await response.json();
            this.rebuildLogDisplay(data.logs);
        } catch (error) {
            console.error('获取日志失败:', error);
        }
    }

    // 重建日志显示
    rebuildLogDisplay(logs) {
        const log = document.getElementById('narrative-log');
        if (!log) return;

        this.finishLogGroup();
        log.innerHTML = '';

        // 将日志按类型分组
        this.groupAndDisplayLogs(logs);
        log.scrollTop = log.scrollHeight;
    }

    // 分组并显示日志
    groupAndDisplayLogs(logs) {
        const log = document.getElementById('narrative-log');
        if (!log) return;

        let groupType = null;
        let groupLogs = [];

        logs.forEach((text) => {
            const type = this.getLogType(text);

            if (type !== groupType || groupLogs.length >= 5) {
                if (groupLogs.length > 0) {
                    this.createLogGroupFromLogs(groupType, groupLogs);
                }
                groupType = type;
                groupLogs = [text];
            } else {
                groupLogs.push(text);
            }
        });

        if (groupLogs.length > 0) {
            this.createLogGroupFromLogs(groupType, groupLogs);
        }
    }

    // 获取日志类型
    getLogType(text) {
        if (text.startsWith('【系统】')) return 'system';
        if (text.startsWith('【剧情】')) return 'event';
        if (text.startsWith('【战斗】')) return 'combat';
        if (text.startsWith('【奖励】')) return 'reward';
        if (text.startsWith('[提示]')) return 'tip';
        if (text.startsWith('【警告】')) return 'warning';
        if (text.startsWith('➤')) return 'player';
        return 'general';
    }

    // 从日志数组创建日志组
    createLogGroupFromLogs(type, logs) {
        const log = document.getElementById('narrative-log');
        if (!log) return;

        const group = document.createElement('div');
        group.className = 'log-group';

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

        logs.forEach(text => {
            const entry = document.createElement('div');
            entry.className = `log-entry ${this.getLogClassName(text)}`;
            entry.textContent = text;
            group.appendChild(entry);
        });

        log.appendChild(group);
    }

    // 获取日志CSS类名
    getLogClassName(text) {
        if (text.startsWith('【系统】')) return 'msg-system';
        if (text.startsWith('【剧情】')) return 'msg-event';
        if (text.startsWith('【战斗】')) return 'msg-combat';
        if (text.startsWith('【奖励】')) return 'msg-reward';
        if (text.startsWith('[提示]')) return 'msg-tip';
        if (text.startsWith('【警告】')) return 'msg-warning';
        if (text.startsWith('➤')) return 'msg-player';
        return '';
    }

    // 智能检查更新
    async checkUpdates() {
        if (this.gameState.isUserInteracting) return;

        try {
            const response = await fetch('/need_refresh');
            if (!response.ok) return;

            const data = await response.json();
            if (JSON.stringify(data) !== JSON.stringify(this.lastKnownStatus)) {
                this.lastKnownStatus = data;
                if (data.refresh && data.last_update > this.gameState.lastUpdateTime) {
                    this.gameState.lastUpdateTime = data.last_update;
                    await this.fetchLog();
                    await this.fetchStatus();
                }
            }
        } catch (error) {
            console.warn('检查更新失败:', error);
        }
    }

    // 触发环境事件
    triggerAmbientEvent() {
        const ambientEvents = [
            '【剧情】山风徐来，带着淡淡的草药香。',
            '【剧情】远处传来仙鹤的清鸣声。',
            '【剧情】天边有流光划过，似是有修士御剑而行。',
            '【剧情】夜色渐深，星河璀璨。',
            '【剧情】灵气波动异常，似乎有宝物出世。',
            '【剧情】远山传来阵阵钟声，那是某个宗门的晚课。'
        ];
        
        this.startLogGroup('环境描述');
        this.addLog('msg-event', ambientEvents[Math.floor(Math.random() * ambientEvents.length)]);
        this.finishLogGroup();
    }

    // 处理键盘输入
    handleKeyDown(event) {
        const input = event.target;
        const autocomplete = document.getElementById('autocomplete');

        if (event.key === 'Tab') {
            event.preventDefault();
            if (autocomplete && autocomplete.style.display === 'block' && autocomplete.children.length > 0) {
                const firstItem = autocomplete.children[0];
                if (firstItem?.dataset?.command) {
                    input.value = firstItem.dataset.command;
                    this.hideAutocomplete();
                }
            } else {
                this.showAutoComplete();
            }
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            this.navigateHistory(-1, input);
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            this.navigateHistory(1, input);
        } else if (event.key === 'Enter') {
            this.executeCommand();
        }
    }

    // 处理键盘释放
    handleKeyUp(event) {
        // 快捷键处理
        if (event.altKey || event.ctrlKey) {
            const key = event.key.toLowerCase();
            const cmd = this.availableCommands.find(c => c.shortcut === key);
            if (cmd) {
                this.sendCommandDirectly(cmd.cmd);
                return;
            }
        }

        // 更新自动完成
        if (!['Tab', 'Enter', 'Escape', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
            this.showAutoComplete();
        }
    }

    // 历史导航
    navigateHistory(direction, input) {
        if (direction === -1 && this.gameState.historyIndex > 0) {
            this.gameState.historyIndex--;
            input.value = this.gameState.commandHistory[this.gameState.historyIndex];
        } else if (direction === 1) {
            if (this.gameState.historyIndex < this.gameState.commandHistory.length - 1) {
                this.gameState.historyIndex++;
                input.value = this.gameState.commandHistory[this.gameState.historyIndex];
            } else {
                this.gameState.historyIndex = this.gameState.commandHistory.length;
                input.value = '';
            }
        }
    }

    // 直接发送命令
    sendCommandDirectly(command) {
        const input = document.getElementById('command-input');
        if (input) {
            input.value = command;
            this.executeCommand();
        }
    }

    // 显示自动完成
    showAutoComplete() {
        const input = document.getElementById('command-input');
        const autocomplete = document.getElementById('autocomplete');
        if (!input || !autocomplete) return;

        const value = input.value.toLowerCase().trim();
        autocomplete.innerHTML = '';

        if (value.length === 0) {
            const commonCmds = ['状态', '修炼', '探索', '背包', '帮助'];
            commonCmds.forEach(cmd => {
                const cmdInfo = this.availableCommands.find(c => c.cmd === cmd);
                if (cmdInfo) {
                    this.addAutoCompleteItem(cmd, cmdInfo.desc);
                }
            });
        } else {
            const matches = this.availableCommands.filter(cmd =>
                cmd.cmd.toLowerCase().includes(value) ||
                cmd.desc.toLowerCase().includes(value)
            );

            matches.slice(0, 8).forEach(cmd => {
                this.addAutoCompleteItem(cmd.cmd, cmd.desc);
            });
        }

        if (autocomplete.children.length > 0) {
            autocomplete.style.display = 'block';
        } else {
            autocomplete.style.display = 'none';
        }
    }

    // 添加自动完成项
    addAutoCompleteItem(command, desc) {
        const autocomplete = document.getElementById('autocomplete');
        if (!autocomplete) return;

        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.dataset.command = command;
        item.innerHTML = `${command}<span class="autocomplete-desc">${desc}</span>`;
        item.addEventListener('click', () => {
            const input = document.getElementById('command-input');
            if (input) {
                input.value = command;
                this.hideAutocomplete();
                input.focus();
            }
        });
        autocomplete.appendChild(item);
    }

    // 隐藏自动完成
    hideAutocomplete() {
        const autocomplete = document.getElementById('autocomplete');
        if (autocomplete) {
            autocomplete.style.display = 'none';
        }
    }

    // 打开模态框
    async openModal(modalName) {
        const modal = document.getElementById('modal');
        const modalContent = document.getElementById('modal-content');
        
        if (!modal || !modalContent) return;
        
        modalContent.innerHTML = '<div class="loading"><div class="loading-spinner"></div><div>加载中...</div></div>';
        modal.style.display = 'block';
        
        try {
            const response = await fetch(`/modal/${modalName}`);
            if (!response.ok) throw new Error('加载失败');
            
            const html = await response.text();
            modalContent.innerHTML = html;
            
            // 处理特殊模态框
            this.handleSpecialModal(modalName);
        } catch (error) {
            console.error('加载模态框失败:', error);
            modalContent.innerHTML = '<p style="color: #ff6b6b;">加载失败，请稍后重试</p>';
        }
    }

    // 处理特殊模态框
    handleSpecialModal(modalName) {
        switch (modalName) {
            case 'save':
                this.sendCommandDirectly('保存');
                setTimeout(() => this.closeModal(), 1000);
                break;
            case 'load':
                this.sendCommandDirectly('加载');
                setTimeout(() => this.closeModal(), 1000);
                break;
            case 'exit':
                this.handleExitModal();
                break;
        }
    }

    // 处理退出模态框
    handleExitModal() {
        const modalContent = document.getElementById('modal-content');
        if (modalContent) {
            modalContent.innerHTML = `
                <h3 style="font-size: 20px; margin-bottom: 20px; color: #d8d8d8;">确认退出</h3>
                <p style="margin-bottom: 30px; color: #b8b8b8;">确定要退出游戏吗？未保存的进度将丢失。</p>
                <div style="display: flex; gap: 20px; justify-content: center;">
                    <button onclick="window.location.href='/welcome'" 
                        style="padding: 12px 24px; background: #8b0000; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">确定退出</button>
                    <button onclick="gameClient.closeModal()" 
                        style="padding: 12px 24px; background: #6b6b6b; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 14px;">取消</button>
                </div>
            `;
        }
    }

    // 关闭模态框
    closeModal() {
        const modal = document.getElementById('modal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    // 显示提示
    showTooltip(element, text) {
        const tooltip = document.getElementById('tooltip');
        if (!tooltip || !element) return;

        const rect = element.getBoundingClientRect();
        tooltip.textContent = text;
        tooltip.style.left = rect.left + 'px';
        tooltip.style.top = (rect.top - 30) + 'px';
        tooltip.classList.add('show');
    }

    // 隐藏提示
    hideTooltip() {
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.classList.remove('show');
        }
    }
}

// 创建全局实例
window.gameClient = new XianxiaGameClient();