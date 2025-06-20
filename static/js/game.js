// 游戏主模块
(function() {
    'use strict';

    // ========== 游戏状态管理 ==========
    const gameState = {
        isNewPlayer: true,
        tutorialStep: 0,
        commandCount: 0,
        visitedAreas: new Set(['青云山']),
        commandHistory: [],
        historyIndex: -1,
        currentEvent: null,
        achievementUnlocked: 0,
        achievementTotal: 20,
        currentLogGroup: null,
        logGroupTimer: null,
        needsRefresh: false,
        isUserInteracting: false,
        lastUpdateTime: 0
    };

    // 记录上一次获取的刷新状态
    let lastKnownStatus = null;

    // 可用命令列表（与服务器同步）
    const availableCommands = [
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

    // ========== 工具函数 ==========
    function hideLoading() {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }

    function updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) element.textContent = value;
    }

    function updateProgressBar(id, current, max) {
        const bar = document.getElementById(id);
        if (bar && max > 0) {
            const percent = Math.min(100, Math.max(0, (current / max * 100)));
            bar.style.width = `${percent}%`;
        }
    }

    // ========== 日志系统 ==========
    function startLogGroup(title) {
        // 如果有未完成的日志组，先完成它
        if (gameState.currentLogGroup) {
            finishLogGroup();
        }

        const log = document.getElementById('narrative-log');
        const group = document.createElement('div');
        group.className = 'log-group';

        if (title) {
            const header = document.createElement('div');
            header.className = 'log-group-header';
            const timestamp = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
            header.textContent = `${title} - ${timestamp}`;
            group.appendChild(header);
        }

        log.appendChild(group);
        gameState.currentLogGroup = group;

        // 设置定时器，超过3秒自动结束日志组
        clearTimeout(gameState.logGroupTimer);
        gameState.logGroupTimer = setTimeout(() => {
            finishLogGroup();
        }, 3000);
    }

    function finishLogGroup() {
        if (gameState.currentLogGroup) {
            gameState.currentLogGroup = null;
            clearTimeout(gameState.logGroupTimer);
        }
    }

    function addLog(className, text) {
        // 如果没有当前日志组，创建一个
        if (!gameState.currentLogGroup) {
            startLogGroup();
        }

        const entry = document.createElement('div');
        entry.className = `log-entry ${className}`;
        entry.textContent = text;

        gameState.currentLogGroup.appendChild(entry);

        // 延迟滚动，等待动画开始
        setTimeout(() => {
            const log = document.getElementById('narrative-log');
            if (log) {
                log.scrollTop = log.scrollHeight;
            }
        }, 100);
    }

    function addHtmlLog(html) {
        const log = document.getElementById('narrative-log');
        if (!log) return;

        const entry = document.createElement('div');
        entry.innerHTML = html;

        log.appendChild(entry);

        setTimeout(() => {
            log.scrollTop = log.scrollHeight;
        }, 100);
    }

    function createLogGroupFromLogs(type, logs) {
        const log = document.getElementById('narrative-log');
        if (!log) return;

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

        log.appendChild(group);
    }

    // ========== 成就系统 ==========
    function showAchievement(title, desc) {
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

        gameState.achievementUnlocked++;
        updateAchievementDisplay();

        setTimeout(() => {
            log.scrollTop = log.scrollHeight;
        }, 100);
    }

    function updateAchievementDisplay() {
        const countElement = document.getElementById('achievement-count');
        const pointsElement = document.getElementById('achievement-points');

        if (countElement) {
            countElement.textContent = `${gameState.achievementUnlocked}/${gameState.achievementTotal}`;
        }
        if (pointsElement) {
            pointsElement.textContent = gameState.achievementUnlocked * 10;
        }
    }

    // ========== 教程系统 ==========
    function initTutorial() {
        if (gameState.isNewPlayer && gameState.tutorialStep === 0) {
            setTimeout(() => {
                hideLoading();
                // 创建欢迎日志组
                startLogGroup('新手引导');
                addLog('msg-system', '【系统】欢迎进入修仙世界。你将扮演一位凡人，踏入仙途。');
                addLog('msg-event', '【剧情】你出生在青云山下的一个普通村落。十六岁那年，一位游方道人路过，发现你有修炼资质，便传授了一卷《基础吐纳诀》。从此，你踏上了修仙之路……');
                addLog('msg-tip tutorial-highlight', '[提示] 你可以输入"修炼"、"背包"、"探索"等指令开始游戏。试试输入"状态"查看你的角色信息。');
                finishLogGroup();

                // Roll角色事件
                triggerRollEvent();
                gameState.tutorialStep = 1;
            }, 1000);
        } else {
            setTimeout(() => {
                hideLoading();
                fetchLog();
            }, 500);
        }
    }

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
        addHtmlLog(eventHtml);
    }

    function checkTutorialProgress(command) {
        const cmd = command.toLowerCase();

        if (gameState.isNewPlayer) {
            if (gameState.tutorialStep === 2 && (cmd === '状态' || cmd === 's')) {
                setTimeout(() => {
                    startLogGroup('教程提示');
                    addLog('msg-tip', '[提示] 很好！你已经了解了自己的状态。现在试试输入"修炼"来提升修为。');
                    finishLogGroup();
                    gameState.tutorialStep = 3;
                }, 1000);
            } else if (gameState.tutorialStep === 3 && (cmd === '修炼' || cmd === 'c')) {
                setTimeout(() => {
                    startLogGroup('教程提示');
                    addLog('msg-tip', '[提示] 修炼可以增加修为，当修为达到上限时就能突破境界。接下来试试"探索"周围环境。');
                    finishLogGroup();
                    gameState.tutorialStep = 4;
                }, 3000);
            } else if (gameState.tutorialStep === 4 && (cmd === '探索' || cmd === 'e')) {
                setTimeout(() => {
                    startLogGroup('教程完成');
                    addLog('msg-tip', '[提示] 探索可以发现各种机缘和事件。你已经掌握了基本操作，祝你修仙之路一帆风顺！');
                    addLog('msg-tip', '[提示] 提示：按Tab键可以显示命令提示，使用方向键可以浏览历史命令。');
                    finishLogGroup();
                    gameState.tutorialStep = 5;
                    gameState.isNewPlayer = false;

                    // 解锁第一个成就
                    showAchievement('初入江湖', '完成新手教程');
                }, 2000);
            }
        }
    }

    // ========== 命令系统 ==========
    async function sendCommand(command) {
        const input = document.getElementById('command-input');
        if (input) {
            input.value = command;
            executeCommand();
        }
    }

    async function executeCommand() {
        const input = document.getElementById('command-input');
        const command = input.value.trim();

        if (!command) return;

        // 标记用户正在交互
        gameState.isUserInteracting = true;

        // 隐藏自动完成
        const autocomplete = document.getElementById('autocomplete');
        if (autocomplete) {
            autocomplete.style.display = 'none';
        }

        // 添加到历史记录
        if (gameState.commandHistory[gameState.commandHistory.length - 1] !== command) {
            gameState.commandHistory.push(command);
            if (gameState.commandHistory.length > 50) {
                gameState.commandHistory.shift();
            }
        }
        gameState.historyIndex = gameState.commandHistory.length;

        // 创建玩家命令日志组
        startLogGroup('玩家指令');
        addLog('msg-player', `➤ ${command}`);

        // 增加命令计数
        gameState.commandCount++;

        try {
            // 发送到服务器
            await fetch('/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command})
            });

            // 清空输入
            input.value = '';
            input.focus();

            // 延迟一下再完成日志组，让响应有时间加入
            setTimeout(() => {
                finishLogGroup();
            }, 100);

            // 更新状态和日志
            await fetchLog();
            await fetchStatus();

            // 检查教程进度
            checkTutorialProgress(command);

        } catch (error) {
            console.error('执行命令失败:', error);
            startLogGroup('系统错误');
            addLog('msg-warning', '【系统】命令执行失败，请稍后重试。');
            finishLogGroup();
        } finally {
            // 重置用户交互状态
            setTimeout(() => {
                gameState.isUserInteracting = false;
            }, 1000);
        }
    }

    // ========== 状态更新 ==========
    async function fetchStatus() {
        try {
            const res = await fetch('/status');
            if (!res.ok) throw new Error('获取状态失败');

            const data = await res.json();
            const p = data.player;
            if (!p) return;

            const attrs = p.attributes;

            updateElement('player-name', p.name || '无名侠客');
            updateElement('realm', attrs.realm_name || '炼气一层');
            updateElement('cultivation', `(${attrs.cultivation_level || 0} / ${attrs.max_cultivation || 100})`);

            const curHealth = Math.max(0, Math.min(attrs.current_health || 0, attrs.max_health || 0));
            const curMana = Math.max(0, Math.min(attrs.current_mana || 0, attrs.max_mana || 0));
            const curQi = Math.max(0, Math.min(attrs.current_stamina || 0, attrs.max_stamina || 0));

            updateElement('health', `${curHealth} / ${attrs.max_health || 0}`);
            updateElement('mana', `${curMana} / ${attrs.max_mana || 0}`);
            updateElement('qi', `${curQi} / ${attrs.max_stamina || 0}`);
            updateElement('attack', Math.floor(attrs.attack_power || 10));
            updateElement('defense', Math.floor(attrs.defense || 5));

            // 处理加成显示
            const deffects = p.extra_data && p.extra_data.destiny ? p.extra_data.destiny.effects || {} : {};
            const atkBonus = deffects.attack || 0;
            const defBonus = deffects.defense || 0;

            updateElement('attack-bonus', atkBonus ? `(${atkBonus>=0?'+':''}${atkBonus})` : '');
            updateElement('defense-bonus', defBonus ? `(${defBonus>=0?'+':''}${defBonus})` : '');

            // 更新进度条
            updateProgressBar('cultivation-progress', attrs.cultivation_level, attrs.max_cultivation);
            updateProgressBar('health-progress', curHealth, attrs.max_health);
            updateProgressBar('mana-progress', curMana, attrs.max_mana);
            updateProgressBar('qi-progress', curQi, attrs.max_stamina);

            // 更新位置和金币
            updateElement('location', data.location_name || data.location || '青云城');
            updateElement('gold', data.gold || 0);

            // 检查低血量警告
            if (attrs.max_health > 0 && curHealth / attrs.max_health < 0.3) {
                if (!document.querySelector('.health-warning-active')) {
                    startLogGroup('系统警告');
                    addLog('msg-warning health-warning-active', '【警告】你的气血值过低，请及时恢复！');
                    finishLogGroup();
                }
            }

        } catch (error) {
            console.error('获取状态失败:', error);
        }
    }

    async function fetchLog() {
        try {
            const res = await fetch('/log');
            if (!res.ok) throw new Error('获取日志失败');

            const data = await res.json();
            const log = document.getElementById('narrative-log');
            if (!log) return;

            // 完成当前日志组
            finishLogGroup();

            // 清空并重建日志
            log.innerHTML = '';

            // 将日志按类型分组
            let groupType = null;
            let groupLogs = [];

            data.logs.forEach((text, index) => {
                // 判断日志类型
                let type = 'general';
                if (text.startsWith('【系统】')) type = 'system';
                else if (text.startsWith('【剧情】')) type = 'event';
                else if (text.startsWith('【战斗】')) type = 'combat';
                else if (text.startsWith('【奖励】')) type = 'reward';
                else if (text.startsWith('[提示]')) type = 'tip';
                else if (text.startsWith('【警告】')) type = 'warning';
                else if (text.startsWith('➤')) type = 'player';

                // 如果类型改变或达到5条，创建新组
                if (type !== groupType || groupLogs.length >= 5) {
                    if (groupLogs.length > 0) {
                        createLogGroupFromLogs(groupType, groupLogs);
                    }
                    groupType = type;
                    groupLogs = [text];
                } else {
                    groupLogs.push(text);
                }
            });

            // 处理最后一组
            if (groupLogs.length > 0) {
                createLogGroupFromLogs(groupType, groupLogs);
            }

            log.scrollTop = log.scrollHeight;

        } catch (error) {
            console.error('获取日志失败:', error);
        }
    }

    // ========== 自动更新 ==========
    async function checkUpdates() {
        // 如果用户正在交互，跳过自动刷新
        if (gameState.isUserInteracting) return;

        try {
            const res = await fetch('/need_refresh');
            if (!res.ok) return;

            const data = await res.json();

            // 仅在状态变化时刷新
            if (JSON.stringify(data) !== JSON.stringify(lastKnownStatus)) {
                lastKnownStatus = data;

                if (data.refresh && data.last_update > gameState.lastUpdateTime) {
                    gameState.lastUpdateTime = data.last_update;
                    await fetchLog();
                    await fetchStatus();
                }
            }
        } catch (error) {
            console.warn('检查更新失败:', error);
        }
    }

    // ========== 自动完成 ==========
    function showAutoComplete() {
        const input = document.getElementById('command-input');
        const autocomplete = document.getElementById('autocomplete');

        if (!input || !autocomplete) return;

        const value = input.value.toLowerCase().trim();
        autocomplete.innerHTML = '';

        if (value.length === 0) {
            // 显示常用命令
            const commonCmds = ['状态', '修炼', '探索', '背包', '帮助'];
            commonCmds.forEach(cmd => {
                const cmdInfo = availableCommands.find(c => c.cmd === cmd);
                if (cmdInfo) {
                    addAutoCompleteItem(cmd, cmdInfo.desc);
                }
            });
        } else {
            // 匹配命令
            const matches = availableCommands.filter(cmd =>
                cmd.cmd.toLowerCase().includes(value) ||
                cmd.desc.toLowerCase().includes(value)
            );

            matches.slice(0, 8).forEach(cmd => {
                addAutoCompleteItem(cmd.cmd, cmd.desc);
            });
        }

        if (autocomplete.children.length > 0) {
            autocomplete.style.display = 'block';
        } else {
            autocomplete.style.display = 'none';
        }
    }

    function addAutoCompleteItem(command, desc) {
        const autocomplete = document.getElementById('autocomplete');
        if (!autocomplete) return;

        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.dataset.command = command;
        item.innerHTML = `${command}<span class="autocomplete-desc">${desc}</span>`;
        item.onclick = () => {
            const input = document.getElementById('command-input');
            if (input) {
                input.value = command;
                autocomplete.style.display = 'none';
                input.focus();
            }
        };
        autocomplete.appendChild(item);
    }

    // ========== 键盘输入处理 ==========
    function handleKeyDown(event) {
        const input = event.target;
        const autocomplete = document.getElementById('autocomplete');

        // Tab键 - 显示/选择自动完成
        if (event.key === 'Tab') {
            event.preventDefault();
            if (autocomplete && autocomplete.style.display === 'block' && autocomplete.children.length > 0) {
                // 选择第一个建议
                const firstItem = autocomplete.children[0];
                if (firstItem && firstItem.dataset.command) {
                    input.value = firstItem.dataset.command;
                    autocomplete.style.display = 'none';
                }
            } else {
                showAutoComplete();
            }
        }
        // 方向键 - 历史记录
        else if (event.key === 'ArrowUp') {
            event.preventDefault();
            if (gameState.historyIndex > 0) {
                gameState.historyIndex--;
                input.value = gameState.commandHistory[gameState.historyIndex];
            }
        } else if (event.key === 'ArrowDown') {
            event.preventDefault();
            if (gameState.historyIndex < gameState.commandHistory.length - 1) {
                gameState.historyIndex++;
                input.value = gameState.commandHistory[gameState.historyIndex];
            } else {
                gameState.historyIndex = gameState.commandHistory.length;
                input.value = '';
            }
        }
        // ESC - 关闭自动完成
        else if (event.key === 'Escape') {
            if (autocomplete) {
                autocomplete.style.display = 'none';
            }
        }
        // Enter - 执行命令
        else if (event.key === 'Enter') {
            executeCommand();
        }
    }

    function handleKeyUp(event) {
        // 快捷键
        if (event.altKey || event.ctrlKey) {
            const key = event.key.toLowerCase();
            const cmd = availableCommands.find(c => c.shortcut === key);
            if (cmd) {
                sendCommand(cmd.cmd);
                return;
            }
        }

        // 输入时更新自动完成
        if (!['Tab', 'Enter', 'Escape', 'ArrowUp', 'ArrowDown'].includes(event.key)) {
            showAutoComplete();
        }
    }

    // ========== 工具提示 ==========
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

    // ========== 事件选择 ==========
    async function makeEventChoice(choiceIndex) {
        const choices = ['剑修之路', '体修之路', '法修之路'];
        startLogGroup('命运选择');
        addLog('msg-player', `➤ 选择：${choices[choiceIndex]}`);

        // 移除事件容器
        const eventContainers = document.querySelectorAll('.event-container');
        eventContainers.forEach(container => container.style.display = 'none');

        // 发送选择到服务器
        try {
            await fetch('/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: `选择 ${choiceIndex + 1}`})
            });

            // 刷新状态和日志
            await fetchLog();
            await fetchStatus();
        } catch (error) {
            console.error('发送选择失败:', error);
        }

        if (gameState.tutorialStep === 1) {
            setTimeout(() => {
                addLog('msg-tip', '[提示] 很好！你已经选择了自己的道路。现在试试输入"状态"查看你的角色信息。');
                gameState.tutorialStep = 2;
                finishLogGroup();
            }, 1000);
        } else {
            finishLogGroup();
        }
    }

    // ========== 初始化 ==========
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
        fetchStatus();
        updateAchievementDisplay();

        // 智能刷新 - 只在需要时检查更新，频率降低
        setInterval(checkUpdates, 5000);

        // 定期随机事件 - 降低频率
        setInterval(() => {
            if (Math.random() < 0.05 && !gameState.isNewPlayer && !gameState.isUserInteracting) {
                const ambientEvents = [
                    '【剧情】山风徐来，带着淡淡的草药香。',
                    '【剧情】远处传来仙鹤的清鸣声。',
                    '【剧情】天边有流光划过，似是有修士御剑而行。',
                    '【剧情】夜色渐深，星河璀璨。',
                    '【剧情】灵气波动异常，似乎有宝物出世。',
                    '【剧情】远山传来阵阵钟声，那是某个宗门的晚课。'
                ];
                startLogGroup('环境描述');
                addLog('msg-event', ambientEvents[Math.floor(Math.random() * ambientEvents.length)]);
                finishLogGroup();
            }
        }, 60000);

        // 点击空白处隐藏自动完成
        document.addEventListener('click', (e) => {
            if (!e.target.matches('.command-input')) {
                const autocomplete = document.getElementById('autocomplete');
                if (autocomplete) {
                    autocomplete.style.display = 'none';
                }
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

    // ========== 导出公共接口 ==========
    window.GameUI = {
        init,
        sendCommand,
        executeCommand,
        makeEventChoice,
        showTooltip,
        hideTooltip
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
})();
