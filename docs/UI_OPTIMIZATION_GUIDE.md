# Web UI 界面优化与交互设计建议

本文档给出了在修仙世界引擎中改进 Web UI 的一些思路，以暗色背景为基调，示例代码基于 **Vue 3 + TailwindCSS**。以下各小节分别对应任务需求，附带组件拆分与实现示例。

## 1. 动态境界显示
```vue
<!-- SidebarStatus.vue 中的一部分 -->
<div class="status-line">
  <span class="status-label">境界</span>
  <span class="status-value">
    {{ realmName }}（{{ realmPercent }}%）
  </span>
</div>
```
- `realmName`：角色当前境界名称。
- `realmPercent`：突破进度，0~100。
- 在游戏状态更新时同步 `realmPercent`，使文本保持实时。

## 2. 灵力值格式校验
```vue
<div class="status-line">
  <span class="status-label">灵力值</span>
  <span class="status-value">{{ mana.current }} / {{ mana.max }}</span>
</div>
```
- `mana` 为 `{ current: number, max: number }`。
- 在更新逻辑中若检测到 `current > max`，自动置为 `max`，防止出现 `180/156` 的错误。

## 3. 攻击与防御分开显示
```vue
<div class="status-line"><span class="status-label">攻击</span><span class="status-value">{{ attack }}</span></div>
<div class="status-line"><span class="status-label">防御</span><span class="status-value">{{ defense }}</span></div>
```
- 取消原有 "攻击 / 防御" 混合格式，保持信息清晰。

## 4. 弹窗信息面板
```vue
<!-- InfoModal.vue -->
<template>
  <a-modal v-model:open="visible" width="70%" :footer="null">
    <h3 class="text-xl mb-4">{{ title }}</h3>
    <table class="w-full table-auto text-left">
      <tr v-for="item in items" :key="item.label">
        <th class="w-1/4 p-2">{{ item.label }}</th>
        <td class="p-2">{{ item.value }}</td>
      </tr>
    </table>
  </a-modal>
</template>
```
- 使用 Ant Design Vue 的 `a-modal` 组件，宽度约占屏幕 70%。
- 通过 `items` 数组渲染表格，使“查看状态/背包/功法”等信息集中展示。

## 5. 侧边栏添加“查看功法”
```vue
<!-- SidebarMenu.vue -->
<ul>
  <li @click="showStatus">查看状态</li>
  <li @click="showInventory">查看背包</li>
  <li @click="showSkills">查看功法</li>
</ul>
```
- 触发对应的弹窗，保持与其他入口一致的样式。

## 6. 专有名词说明
```vue
<!-- 使用 Tooltip 展示解释 -->
<a-tooltip placement="right" :title="skillDesc">
  <span class="cursor-help text-emerald-300">{{ skillName }}</span>
</a-tooltip>
```
- 鼠标悬浮或点击专有名词时弹出解释，统一采用 Ant Design 的 `a-tooltip`。

## 7. 美化标题与重要输出
```vue
<!-- LogCard.vue -->
<div class="p-4 bg-gray-800 rounded shadow mb-3">
  <slot />
</div>
```
- 游戏日志与标题等内容均放入 `LogCard` 组件中，使其带有圆角阴影效果。
- 可在文本中加入轻量级 Emoji，例如 “✨=== 游戏开始 ===✨”。

## 8. Markdown 样式支持
可结合 `marked` 库将服务器返回的 Markdown 文本转为 HTML：
```vue
<div v-html="renderMarkdown(log)" class="prose prose-invert"></div>
```
- `prose` 类来自 Tailwind Typography 插件，便于排版。

## 9. 布局建议与组件拆分
- `App.vue`：总体布局，包含侧边栏、日志区域与命令输入。
- `SidebarStatus.vue`：侧边栏属性与导航。
- `InfoModal.vue`：查看状态/背包/功法等大弹窗。
- `LogCard.vue`：包裹重要输出及标题。
- 其他功能（如 Tooltip、Markdown 渲染）可按需封装为独立组件或组合函数。

以上示例仅为核心思路，实际接入时需与后端接口数据格式保持一致，并统一使用暗色风格与适当留白以增强阅读体验。
