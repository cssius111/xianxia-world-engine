// 状态管理模块
export class StateManager {
    constructor() {
        this.state = {
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

        // 订阅者列表
        this.subscribers = [];
    }

    // 获取状态
    getState() {
        return this.state;
    }

    // 更新状态
    setState(updates) {
        this.state = { ...this.state, ...updates };
        this.notify();
    }

    // 订阅状态变化
    subscribe(callback) {
        this.subscribers.push(callback);
        return () => {
            this.subscribers = this.subscribers.filter(cb => cb !== callback);
        };
    }

    // 通知所有订阅者
    notify() {
        this.subscribers.forEach(callback => callback(this.state));
    }

    // 特定状态操作
    addCommandToHistory(command) {
        if (this.state.commandHistory[this.state.commandHistory.length - 1] !== command) {
            this.state.commandHistory.push(command);
            if (this.state.commandHistory.length > 50) {
                this.state.commandHistory.shift();
            }
        }
        this.state.historyIndex = this.state.commandHistory.length;
        this.notify();
    }

    incrementCommandCount() {
        this.state.commandCount++;
        this.notify();
    }

    setUserInteracting(value) {
        this.state.isUserInteracting = value;
        this.notify();
    }

    unlockAchievement() {
        this.state.achievementUnlocked++;
        this.notify();
    }
}

// 创建单例实例
export const stateManager = new StateManager();
