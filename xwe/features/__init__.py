"""
修仙世界引擎 - 功能增强模块
包含7大功能方向的实现
"""

# 1. 基础玩家体验
from .player_experience import (
    SmartCommandProcessor,
    PlayerGuidance,
    FriendlyErrorHandler,
    InputHelper,
    GameTipsDisplay,
    input_helper,
    tips_display,
    enhance_player_experience
)

# 2. 沉浸式叙事
from .narrative_system import (
    StoryEvent,
    Achievement,
    OpeningEventGenerator,
    AchievementSystem,
    StoryBranchManager,
    NarrativeEventSystem,
    NarrativeSystem,
    narrative_system,
    create_immersive_opening,
    check_and_display_achievements
)

# 3. 内容生态
from .content_ecosystem import (
    ContentType,
    ModInfo,
    ContentEntry,
    ModLoader,
    ContentRegistry,
    HotUpdateManager,
    ModCreator,
    ContentEcosystem,
    content_ecosystem
)

# 4. AI个性化
from .ai_personalization import (
    PlayerStyle,
    ContentPreference,
    PlayerProfile,
    PlayerStyleAnalyzer,
    AdaptiveGuideSystem,
    DynamicNPCBehavior,
    PersonalizationEngine,
    AIPersonalization,
    personalization_engine,
    enhance_with_ai_features
)

# 5. 社区系统
from .community_system import (
    FeedbackType,
    FeedbackPriority,
    Feedback,
    CommunityLink,
    FeedbackCollector,
    CommunityHub,
    PlayerDataAnalytics,
    CommunitySystem,
    community_system,
    integrate_community_features,
    submit_feedback,
    show_community
)

# 6. 技术运营
from .technical_ops import (
    SaveGame,
    ErrorLog,
    SaveManager,
    ErrorHandler,
    PerformanceMonitor,
    AutoBackupManager,
    TechnicalOpsSystem,
    TechnicalOps,
    tech_ops_system,
    integrate_technical_features
)

# 7. 视觉增强
from .visual_enhancement import (
    Color,
    TextRenderer,
    ASCIIArt,
    TextAnimation,
    ProgressBar,
    VisualTheme,
    VisualEffects,
    visual_effects
)
from .html_output import HtmlGameLogger

# 8. 拍卖行系统
from .auction_system import (
    AuctionMode,
    BidderType,
    AuctionItem,
    Bidder,
    AuctionSystem,
    auction_system
)
from .auction_commands import (
    AuctionCommandHandler,
    auction_command_handler
)
from .interactive_auction import InteractiveAuction

# 版本信息
__version__ = "2.0.0"
__all__ = [
    # 玩家体验
    "enhance_player_experience",
    "input_helper",
    "tips_display",
    
    # 叙事系统
    "narrative_system",
    "NarrativeSystem",
    "create_immersive_opening",
    "check_and_display_achievements",
    
    # 内容生态
    "content_ecosystem",

    # AI个性化
    "personalization_engine",
    "AIPersonalization",
    "enhance_with_ai_features",
    
    # 社区系统
    "community_system",
    "integrate_community_features",
    "submit_feedback",
    "show_community",
    
    # 技术运营
    "tech_ops_system",
    "TechnicalOps",
    "integrate_technical_features",
    
    # 视觉增强
    "visual_effects",
    "HtmlGameLogger",
    
    # 拍卖行系统
    "auction_system",
    "auction_command_handler",
    "InteractiveAuction"
]
