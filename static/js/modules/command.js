// 命令处理模块
export class CommandHandler {
    constructor(stateManager, apiClient, logManager) {
        this.stateManager = stateManager;
        this.apiClient = apiClient;
        this.logManager = logManager;

        // 可用命令列表
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

    // 发送命令
    async sendCommand(command) {
        const input = document.getElementById('command-input');
        if (input) {
            input.value = command;
            await this.executeCommand();
        }
    }

    // 执行命令
    async executeCommand() {
        const input = document.getElementById('command-input');
        const command = input.value.trim();

        if (!command) return;

        // 标记用户正在交互
        this.stateManager.setUserInteracting(true);

        // 隐藏自动完成
        const autocomplete = document.getElementById('autocomplete');
        if (autocomplete) {
            autocomplete.style.display = 'none';
        }

        // 添加到历史记录
        this.stateManager.addCommandToHistory(command);

        // 创建玩家命令日志组
        this.logManager.startLogGroup('玩家指令');
        this.logManager.addLog('msg-player', `➤ ${command}`);

        // 增加命令计数
        this.stateManager.incrementCommandCount();

        try {
            // 发送到服务器
            await this.apiClient.sendCommand(command);

            // 清空输入
            input.value = '';
            input.focus();

            // 延迟一下再完成日志组，让响应有时间加入
            setTimeout(() => {
                this.logManager.finishLogGroup();
            }, 100);

            // 更新状态和日志
            await this.updateGameState();

            // 检查教程进度
            this.checkTutorialProgress(command);

        } catch (error) {
            console.error('执行命令失败:', error);
            this.logManager.startLogGroup('系统错误');
            this.logManager.addLog('msg-warning', '【系统】命令执行失败，请稍后重试。');
            this.logManager.finishLogGroup();
        } finally {
            // 重置用户交互状态
            setTimeout(() => {
                this.stateManager.setUserInteracting(false);
            }, 1000);
        }
    }

    // 更新游戏状态
    async updateGameState() {
        const [logData, statusData] = await Promise.all([
            this.apiClient.fetchLog(),
            this.apiClient.fetchStatus()
        ]);

        // 更新日志
        this.updateLogs(logData);

        // 更新状态
        this.updateStatus(statusData);
    }

    // 更新日志显示
    updateLogs(data) {
        // 完成当前日志组
        this.logManager.finishLogGroup();

        // 清空并重建日志
        this.logManager.clearLogs();

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
                    this.logManager.createLogGroupFromLogs(groupType, groupLogs);
                }
                groupType = type;
                groupLogs = [text];
            } else {
                groupLogs.push(text);
            }
        });

        // 处理最后一组
        if (groupLogs.length > 0) {
            this.logManager.createLogGroupFromLogs(groupType, groupLogs);
        }
    }

    // 更新状态显示
    updateStatus(data) {
        const p = data.player;
        if (!p) return;

        const attrs = p.attributes;

        // 安全地更新元素内容
        const updateElement = (id, value) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value;
        };

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
        this.updateProgressBar('cultivation-progress', attrs.cultivation_level, attrs.max_cultivation);
        this.updateProgressBar('health-progress', curHealth, attrs.max_health);
        this.updateProgressBar('mana-progress', curMana, attrs.max_mana);
        this.updateProgressBar('qi-progress', curQi, attrs.max_stamina);

        // 更新位置和金币
        updateElement('location', data.location_name || data.location || '青云城');
        updateElement('gold', data.gold || 0);

        // 检查低血量警告
        if (attrs.max_health > 0 && curHealth / attrs.max_health < 0.3) {
            if (!document.querySelector('.health-warning-active')) {
                this.logManager.startLogGroup('系统警告');
                this.logManager.addLog('msg-warning health-warning-active', '【警告】你的气血值过低，请及时恢复！');
                this.logManager.finishLogGroup();
            }
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

    // 检查教程进度
    checkTutorialProgress(command) {
        const state = this.stateManager.getState();
        const cmd = command.toLowerCase();

        if (state.isNewPlayer) {
            if (state.tutorialStep === 2 && (cmd === '状态' || cmd === 's')) {
                setTimeout(() => {
                    this.logManager.startLogGroup('教程提示');
                    this.logManager.addLog('msg-tip', '[提示] 很好！你已经了解了自己的状态。现在试试输入"修炼"来提升修为。');
                    this.logManager.finishLogGroup();
                    this.stateManager.setState({ tutorialStep: 3 });
                }, 1000);
            } else if (state.tutorialStep === 3 && (cmd === '修炼' || cmd === 'c')) {
                setTimeout(() => {
                    this.logManager.startLogGroup('教程提示');
                    this.logManager.addLog('msg-tip', '[提示] 修炼可以增加修为，当修为达到上限时就能突破境界。接下来试试"探索"周围环境。');
                    this.logManager.finishLogGroup();
                    this.stateManager.setState({ tutorialStep: 4 });
                }, 3000);
            } else if (state.tutorialStep === 4 && (cmd === '探索' || cmd === 'e')) {
                setTimeout(() => {
                    this.logManager.startLogGroup('教程完成');
                    this.logManager.addLog('msg-tip', '[提示] 探索可以发现各种机缘和事件。你已经掌握了基本操作，祝你修仙之路一帆风顺！');
                    this.logManager.addLog('msg-tip', '[提示] 提示：按Tab键可以显示命令提示，使用方向键可以浏览历史命令。');
                    this.logManager.finishLogGroup();
                    this.stateManager.setState({
                        tutorialStep: 5,
                        isNewPlayer: false
                    });

                    // 解锁第一个成就
                    this.showAchievement('初入江湖', '完成新手教程');
                }, 2000);
            }
        }
    }

    // 显示成就
    showAchievement(title, desc) {
        this.logManager.showAchievement(title, desc);
        this.stateManager.unlockAchievement();
        this.updateAchievementDisplay();
    }

    // 更新成就显示
    updateAchievementDisplay() {
        const state = this.stateManager.getState();
        const countElement = document.getElementById('achievement-count');
        const pointsElement = document.getElementById('achievement-points');

        if (countElement) {
            countElement.textContent = `${state.achievementUnlocked}/${state.achievementTotal}`;
        }
        if (pointsElement) {
            pointsElement.textContent = state.achievementUnlocked * 10;
        }
    }
}
