/**
 * 修仙世界模拟器 - 服务工作者
 * 提供离线支持和缓存功能
 */

const CACHE_NAME = 'xianxia-world-v2.0.0';
const STATIC_CACHE = 'xianxia-static-v2.0.0';
const DYNAMIC_CACHE = 'xianxia-dynamic-v2.0.0';

// 需要缓存的静态资源
const STATIC_ASSETS = [
    '/',
    '/welcome',
    '/intro',
    '/game',
    '/static/css/ink_style.css',
    '/static/js/game_controller.js',
    '/static/js/modules/ui_controller.js',
    '/static/js/modules/audio_controller.js',
    '/static/js/modules/player_profile.js',
    '/static/js/modules/modal_controller.js',
    // 添加其他重要静态资源
];

// 需要动态缓存的API端点
const DYNAMIC_ENDPOINTS = [
    '/status',
    '/log',
    '/command',
    '/modal/',
    '/get_audio_list'
];

// 不需要缓存的路径
const EXCLUDE_PATHS = [
    '/save_game',
    '/load_game',
    '/create_character'
];

/**
 * 安装事件 - 预缓存静态资源
 */
self.addEventListener('install', event => {
    console.log('🔧 Service Worker: 安装中...');
    
    event.waitUntil(
        Promise.all([
            // 缓存静态资源
            caches.open(STATIC_CACHE).then(cache => {
                console.log('📦 缓存静态资源...');
                return cache.addAll(STATIC_ASSETS);
            }),
            
            // 立即激活新的Service Worker
            self.skipWaiting()
        ]).then(() => {
            console.log('✅ Service Worker: 安装完成');
        }).catch(error => {
            console.error('❌ Service Worker: 安装失败', error);
        })
    );
});

/**
 * 激活事件 - 清理旧缓存
 */
self.addEventListener('activate', event => {
    console.log('🚀 Service Worker: 激活中...');
    
    event.waitUntil(
        Promise.all([
            // 清理旧缓存
            caches.keys().then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && 
                            cacheName !== DYNAMIC_CACHE &&
                            cacheName.startsWith('xianxia-')) {
                            console.log('🗑️ 删除旧缓存:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            }),
            
            // 立即控制所有客户端
            self.clients.claim()
        ]).then(() => {
            console.log('✅ Service Worker: 激活完成');
        }).catch(error => {
            console.error('❌ Service Worker: 激活失败', error);
        })
    );
});

/**
 * 获取事件 - 处理网络请求
 */
self.addEventListener('fetch', event => {
    const url = new URL(event.request.url);
    
    // 跳过不需要缓存的路径
    if (shouldExcludeFromCache(url.pathname)) {
        return;
    }
    
    // 根据请求类型选择缓存策略
    if (isStaticAsset(url.pathname)) {
        // 静态资源：缓存优先
        event.respondWith(cacheFirst(event.request));
    } else if (isDynamicEndpoint(url.pathname)) {
        // 动态内容：网络优先，降级到缓存
        event.respondWith(networkFirst(event.request));
    } else {
        // 其他请求：仅网络
        event.respondWith(networkOnly(event.request));
    }
});

/**
 * 消息事件 - 处理来自主线程的消息
 */
self.addEventListener('message', event => {
    const { type, data } = event.data;
    
    switch (type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'GET_VERSION':
            event.ports[0].postMessage({
                version: CACHE_NAME,
                staticCache: STATIC_CACHE,
                dynamicCache: DYNAMIC_CACHE
            });
            break;
            
        case 'CLEAR_CACHE':
            clearAllCaches().then(() => {
                event.ports[0].postMessage({ success: true });
            }).catch(error => {
                event.ports[0].postMessage({ success: false, error: error.message });
            });
            break;
            
        case 'CACHE_SIZE':
            getCacheSize().then(size => {
                event.ports[0].postMessage({ size });
            });
            break;
            
        default:
            console.warn('未知消息类型:', type);
    }
});

/**
 * 同步事件 - 后台同步
 */
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        console.log('🔄 后台同步触发');
        event.waitUntil(doBackgroundSync());
    }
});

/**
 * 缓存优先策略
 */
async function cacheFirst(request) {
    try {
        const cache = await caches.open(STATIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            console.log('📦 从缓存返回:', request.url);
            
            // 后台更新缓存
            updateCacheInBackground(request, cache);
            
            return cachedResponse;
        }
        
        // 缓存中没有，从网络获取
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
        }
        
        return networkResponse;
    } catch (error) {
        console.error('缓存优先策略失败:', error);
        return new Response('离线状态，资源不可用', {
            status: 503,
            statusText: 'Service Unavailable'
        });
    }
}

/**
 * 网络优先策略
 */
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        
        if (networkResponse.ok) {
            const cache = await caches.open(DYNAMIC_CACHE);
            cache.put(request, networkResponse.clone());
            console.log('🌐 从网络返回并缓存:', request.url);
        }
        
        return networkResponse;
    } catch (error) {
        console.log('🌐 网络失败，尝试缓存:', request.url);
        
        const cache = await caches.open(DYNAMIC_CACHE);
        const cachedResponse = await cache.match(request);
        
        if (cachedResponse) {
            console.log('📦 从缓存返回:', request.url);
            return cachedResponse;
        }
        
        // 返回离线页面或错误响应
        if (request.headers.get('accept').includes('text/html')) {
            return getOfflinePage();
        }
        
        return new Response(JSON.stringify({
            error: '网络连接失败，请检查网络设置',
            offline: true
        }), {
            status: 503,
            headers: { 'Content-Type': 'application/json' }
        });
    }
}

/**
 * 仅网络策略
 */
async function networkOnly(request) {
    try {
        return await fetch(request);
    } catch (error) {
        console.error('网络请求失败:', request.url, error);
        throw error;
    }
}

/**
 * 后台更新缓存
 */
async function updateCacheInBackground(request, cache) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse.ok) {
            await cache.put(request, networkResponse);
            console.log('🔄 后台更新缓存:', request.url);
        }
    } catch (error) {
        console.warn('后台更新缓存失败:', error);
    }
}

/**
 * 获取离线页面
 */
function getOfflinePage() {
    return new Response(`
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>离线状态 - 修仙世界模拟器</title>
            <style>
                body {
                    font-family: 'Microsoft YaHei', sans-serif;
                    background: linear-gradient(135deg, #f5f5dc 0%, #f8f8f0 100%);
                    margin: 0;
                    padding: 40px 20px;
                    text-align: center;
                    color: #1a1a1a;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                }
                .offline-container {
                    max-width: 500px;
                    background: rgba(255, 255, 255, 0.9);
                    padding: 40px;
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                    border: 2px solid #d4af37;
                }
                .offline-icon {
                    font-size: 4rem;
                    margin-bottom: 20px;
                }
                .offline-title {
                    font-size: 1.8rem;
                    color: #d4af37;
                    margin-bottom: 15px;
                    font-weight: bold;
                }
                .offline-message {
                    font-size: 1.1rem;
                    color: #666;
                    margin-bottom: 30px;
                    line-height: 1.6;
                }
                .retry-button {
                    background: linear-gradient(135deg, #d4af37 0%, #f4d03f 100%);
                    color: #1a1a1a;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 8px;
                    font-size: 1rem;
                    font-weight: bold;
                    cursor: pointer;
                    transition: transform 0.2s ease;
                }
                .retry-button:hover {
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div class="offline-icon">📶</div>
                <h1 class="offline-title">网络连接中断</h1>
                <p class="offline-message">
                    看起来你现在处于离线状态。<br>
                    修仙之路暂时中断，请检查网络连接后重试。
                </p>
                <button class="retry-button" onclick="window.location.reload()">
                    🔄 重新连接
                </button>
            </div>
        </body>
        </html>
    `, {
        headers: { 'Content-Type': 'text/html' }
    });
}

/**
 * 判断是否为静态资源
 */
function isStaticAsset(pathname) {
    return pathname.startsWith('/static/') || 
           STATIC_ASSETS.includes(pathname) ||
           pathname.endsWith('.css') ||
           pathname.endsWith('.js') ||
           pathname.endsWith('.png') ||
           pathname.endsWith('.jpg') ||
           pathname.endsWith('.svg') ||
           pathname.endsWith('.ico');
}

/**
 * 判断是否为动态端点
 */
function isDynamicEndpoint(pathname) {
    return DYNAMIC_ENDPOINTS.some(endpoint => 
        pathname.startsWith(endpoint)
    );
}

/**
 * 判断是否应该排除缓存
 */
function shouldExcludeFromCache(pathname) {
    return EXCLUDE_PATHS.some(path => 
        pathname.startsWith(path)
    ) || pathname.includes('chrome-extension://');
}

/**
 * 清理所有缓存
 */
async function clearAllCaches() {
    const cacheNames = await caches.keys();
    return Promise.all(
        cacheNames.map(cacheName => {
            if (cacheName.startsWith('xianxia-')) {
                console.log('🗑️ 清理缓存:', cacheName);
                return caches.delete(cacheName);
            }
        })
    );
}

/**
 * 获取缓存大小
 */
async function getCacheSize() {
    const cacheNames = await caches.keys();
    let totalSize = 0;
    
    for (const cacheName of cacheNames) {
        if (cacheName.startsWith('xianxia-')) {
            const cache = await caches.open(cacheName);
            const requests = await cache.keys();
            
            for (const request of requests) {
                const response = await cache.match(request);
                if (response) {
                    const blob = await response.blob();
                    totalSize += blob.size;
                }
            }
        }
    }
    
    return totalSize;
}

/**
 * 后台同步处理
 */
async function doBackgroundSync() {
    try {
        console.log('🔄 执行后台同步...');
        
        // 这里可以添加需要后台同步的操作
        // 例如：同步离线时的游戏操作
        
        console.log('✅ 后台同步完成');
    } catch (error) {
        console.error('❌ 后台同步失败:', error);
        throw error;
    }
}

/**
 * 预加载重要资源
 */
async function preloadCriticalResources() {
    const criticalUrls = [
        '/static/js/game_controller.js',
        '/static/js/modules/ui_controller.js',
        '/static/css/ink_style.css'
    ];
    
    const cache = await caches.open(STATIC_CACHE);
    
    return Promise.all(
        criticalUrls.map(async url => {
            try {
                const response = await fetch(url);
                if (response.ok) {
                    await cache.put(url, response);
                    console.log('⚡ 预加载:', url);
                }
            } catch (error) {
                console.warn('预加载失败:', url, error);
            }
        })
    );
}

/**
 * 发送消息给客户端
 */
function notifyClients(message) {
    self.clients.matchAll().then(clients => {
        clients.forEach(client => {
            client.postMessage(message);
        });
    });
}

/**
 * 检查更新
 */
self.addEventListener('online', () => {
    console.log('🌐 网络连接恢复');
    notifyClients({ type: 'ONLINE' });
});

self.addEventListener('offline', () => {
    console.log('📶 网络连接断开');
    notifyClients({ type: 'OFFLINE' });
});

// 启动时预加载关键资源
self.addEventListener('install', event => {
    event.waitUntil(preloadCriticalResources());
});

console.log('🎮 修仙世界模拟器 Service Worker 已加载');
