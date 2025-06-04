# chinese_dragon_art.py
"""
中国传统龙形ASCII艺术资源
"""

# 中国龙ASCII艺术集合
CHINESE_DRAGONS = {
    "classic": """
                    ⣀⣤⣴⣶⣿⣿⣷⣶⣄⣀⣀   
                ⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⣀
              ⣰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣄
             ⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦
            ⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷
           ⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆
          ⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
         ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
        ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇
    """,
    
    "simple": """
       ╭─────╮
      │ ●   ● │    ～～～
      ╰──┬──╯    ～～～～
         │      ～～～～～
    ╭────┴────╮～～～～
    │         │～～～
    ╰─────────╯
    """,
    
    "detailed": """
                     🐲
            ╭──────────────╮
           ╱                ╲
          │  ●          ●   │
          │       ▽         │
          ╰─┬──────────┬───╯
            │          │
        ～～～╰──────────╯～～～
      ～～～～～～～～～～～～～～
    """,
    
    "welcome": """
                                    
                  龙                
                 ╱ ╲               
                ╱   ╲              
               │ ●_● │             
               │  ▽  │             
           ～～～├─────┤～～～         
         ～～～～│     │～～～～       
       ～～～～～╰─────╯～～～～～     
     ～～～～～～～～～～～～～～～～   
    """,
    
    "battle": """
            ⚔️ 龙 ⚔️
           ╱ ╲_╱ ╲
          │ ◉   ◉ │
          │   <   │
          ╰───┬───╯
       ～～～～│～～～～
    """,
    
    "mini": """～🐉～""",
    
    "achievement": """
        ✨ 🐲 ✨
         成 就
        解 锁！
    """,
}

def get_dragon_art(style="classic"):
    """获取指定风格的中国龙ASCII艺术"""
    return CHINESE_DRAGONS.get(style, CHINESE_DRAGONS["classic"])

def display_dragon_with_animation(style="flying"):
    """带动画效果的龙显示（终端环境）"""
    import time
    import os
    
    dragon = get_dragon_art(style)
    lines = dragon.split('\n')
    
    # 逐行显示，营造飞龙效果
    for line in lines:
        print(line)
        time.sleep(0.1)
    
def get_dragon_for_scene(scene_type):
    """根据场景返回合适的龙图案"""
    scene_dragons = {
        "welcome": "welcome",
        "battle": "battle", 
        "achievement": "achievement",
        "dialogue": "simple",
        "status": "mini",
        "help": "simple"
    }
    return get_dragon_art(scene_dragons.get(scene_type, "classic"))
