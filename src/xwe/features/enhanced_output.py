"""
增强的游戏输出处理器，支持将多行相关内容组合显示
"""
from typing import Any, List, Optional, Tuple
import re


class EnhancedGameOutput:
    """增强的游戏输出处理器"""
    
    def __init__(self, html_logger=None) -> None:
        self.html_logger = html_logger
        self.output_buffer = []
        self.current_context = None
        
    def output(self, text: str, category: str = "system", force_new_block: bool = False) -> None:
        """
        智能输出处理
        
        Args:
            text: 输出文本
            category: 输出类别
            force_new_block: 是否强制开始新的输出块
        """
        if not text:
            return
            
        # 判断是否应该合并到当前块
        should_merge = self._should_merge(text, category)
        
        if self.html_logger:
            if should_merge and not force_new_block and self.output_buffer:
                # 合并到当前输出块
                is_continuation = True
            else:
                # 开始新的输出块
                is_continuation = False
                self.output_buffer = []
                
            self.html_logger.add_log(text, category, is_continuation)
            
        # 同时输出到控制台
        self._console_output(text, category)
        
        # 更新缓冲区
        self.output_buffer.append((text, category))
        
    def _should_merge(self, text: str, category: str) -> bool:
        """判断是否应该合并到当前输出块"""
        if not self.output_buffer:
            return False
            
        last_text, last_category = self.output_buffer[-1]
        
        # 相同类别的连续输出
        if category == last_category:
            # 战斗日志应该合并
            if category == "combat":
                return True
                
            # 系统消息如果是列表形式应该合并
            if category == "system" and self._is_list_item(text):
                return True
                
            # 对话应该保持独立
            if category == "dialogue":
                return False
                
        # 检测是否是同一事件的多行输出
        if self._is_related_content(last_text, text):
            return True
            
        return False
        
    def _is_list_item(self, text: str) -> bool:
        """检测是否是列表项"""
        patterns = [
            r'^[\s]*[-*·•]\s',  # 项目符号
            r'^[\s]*\d+\.\s',    # 数字列表
            r'^[\s]*[【\[].*[】\]]',  # 方括号标记
            r'^[\s]*>',          # 引用标记
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                return True
        return False
        
    def _is_related_content(self, text1: str, text2: str) -> bool:
        """判断两段文本是否相关"""
        # 如果第二段文本以小写字母或标点开始，可能是续行
        if text2 and text2[0].islower() or text2[0] in '，。！？；：':
            return True
            
        # 如果包含"并且"、"同时"等连接词
        connecting_words = ['并且', '同时', '另外', '此外', '而且', '因此', '所以']
        for word in connecting_words:
            if text2.startswith(word):
                return True
                
        return False
        
    def _console_output(self, text: str, category: str) -> None:
        """控制台输出（带颜色）"""
        color_map = {
            'system': '\033[90m',    # 灰色
            'combat': '\033[91m',    # 红色
            'success': '\033[92m',   # 绿色
            'dialogue': '\033[94m',  # 蓝色
            'error': '\033[91m',     # 红色
        }
        
        color = color_map.get(category, '')
        reset = '\033[0m' if color else ''
        
        print(f"{color}{text}{reset}")
        
    def combat_sequence(self, actions: List[str]) -> None:
        """输出战斗序列（作为一个整体）"""
        if not actions:
            return
            
        # 将所有战斗动作合并为一个输出块
        combat_text = "\n".join(actions)
        self.output(combat_text, "combat", force_new_block=True)
        
    def status_report(self, status_dict: dict) -> None:
        """输出状态报告（格式化为表格）"""
        if not status_dict:
            return
            
        lines = ["===== 角色状态 ====="]
        for key, value in status_dict.items():
            lines.append(f"{key}: {value}")
        lines.append("==================")
        
        status_text = "\n".join(lines)
        self.output(status_text, "system", force_new_block=True)
        
    def dialogue_exchange(self, speaker: str, dialogue: str, responses: Optional[List[str]] = None) -> None:
        """输出对话交流（包括选项）"""
        dialogue_text = f"【{speaker}】: {dialogue}"
        
        if responses:
            dialogue_text += "\n\n可选回应："
            for i, response in enumerate(responses, 1):
                dialogue_text += f"\n  {i}. {response}"
                
        self.output(dialogue_text, "dialogue", force_new_block=True)


# 使用示例
if __name__ == "__main__":
    from xwe.features.html_output import HtmlGameLogger
    
    # 创建HTML日志器
    html_logger = HtmlGameLogger("game_output.html")
    
    # 创建增强输出处理器
    output = EnhancedGameOutput(html_logger)
    
    # 测试各种输出
    output.output("游戏开始！", "system")
    output.output("正在加载世界...", "system")
    output.output("加载完成！", "system")
    
    # 战斗序列
    output.combat_sequence([
        "你发起了攻击！",
        "造成了 50 点伤害",
        "敌人反击！",
        "你受到了 20 点伤害",
        "战斗胜利！获得100经验值"
    ])
    
    # 状态报告
    output.status_report({
        "生命值": "80/100",
        "法力值": "50/50",
        "经验值": "1500/2000",
        "金币": 350
    })
    
    # 对话
    output.dialogue_exchange(
        "神秘商人",
        "年轻人，我这里有些好东西，要不要看看？",
        ["让我看看你的商品", "不用了，谢谢", "你是谁？"]
    )
