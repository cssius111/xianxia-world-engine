// API客户端模块
export class ApiClient {
    constructor(baseUrl = '') {
        this.baseUrl = baseUrl;
    }

    // 发送命令
    async sendCommand(command) {
        const response = await fetch(`${this.baseUrl}/command`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({command})
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    // 获取状态
    async fetchStatus() {
        const response = await fetch(`${this.baseUrl}/status`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    // 获取日志
    async fetchLog() {
        const response = await fetch(`${this.baseUrl}/log`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }

    // 检查是否需要刷新
    async checkNeedRefresh() {
        const response = await fetch(`${this.baseUrl}/need_refresh`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return response.json();
    }
}

// 创建单例实例
export const apiClient = new ApiClient();
