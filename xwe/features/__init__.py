"""
修仙世界引擎 - 功能增强模块
包含7大功能方向的实现
"""

# 4. AI个性化
from xwe.features.ai_personalization import (
    AdaptiveGuideSystem,
    AIPersonalization,
    ContentPreference,
    DynamicNPCBehavior,
    PersonalizationEngine,
    PlayerProfile,
    PlayerStyle,
    PlayerStyleAnalyzer,
    enhance_with_ai_features,
    personalization_engine,
)
from xwe.features.auction_commands import AuctionCommandHandler, auction_command_handler

# 8. 拍卖行系统
from xwe.features.auction_system import (
    AuctionItem,
    AuctionMode,
    AuctionSystem,
    Bidder,
    BidderType,
    auction_system,
)

# 5. 社区系统
from xwe.features.community_system import (
    CommunityHub,
    CommunityLink,
    CommunitySystem,
    Feedback,
    FeedbackCollector,
    FeedbackPriority,
    FeedbackType,
    PlayerDataAnalytics,
    community_system,
    integrate_community_features,
    show_community,
    submit_feedback,
)

# 3. 内容生态
from xwe.features.content_ecosystem import (
    ContentEcosystem,
    ContentEntry,
    ContentRegistry,
    ContentType,
    HotUpdateManager,
    ModCreator,
    ModInfo,
    ModLoader,
    content_ecosystem,
)
from xwe.features.html_output import HtmlGameLogger
from xwe.features.intelligence_system import (
    IntelItem,
    IntelligenceSystem,
    integrate_intelligence_system,
    intelligence_system,
)
from xwe.features.interactive_auction import InteractiveAuction

# 2. 沉浸式叙事
from xwe.features.narrative_system import (
    Achievement,
    AchievementSystem,
    NarrativeEventSystem,
    NarrativeSystem,
    OpeningEventGenerator,
    StoryBranchManager,
    StoryEvent,
    check_and_display_achievements,
    create_immersive_opening,
    narrative_system,
)

# 1. 基础玩家体验
from xwe.features.player_experience import (
    FriendlyErrorHandler,
    GameTipsDisplay,
    InputHelper,
    PlayerGuidance,
    SmartCommandProcessor,
    enhance_player_experience,
    input_helper,
    tips_display,
)

# 6. 技术运营
from xwe.features.technical_ops import (
    AutoBackupManager,
    ErrorHandler,
    ErrorLog,
    PerformanceMonitor,
    SaveGame,
    SaveManager,
    TechnicalOps,
    TechnicalOpsSystem,
    integrate_technical_features,
    tech_ops_system,
)

# 7. 视觉增强
from xwe.features.visual_enhancement import (
    ASCIIArt,
    Color,
    ProgressBar,
    TextAnimation,
    TextRenderer,
    VisualEffects,
    VisualTheme,
    visual_effects,
)

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
    "InteractiveAuction",
    "intelligence_system",
    "integrate_intelligence_system",
    "IntelItem",
    "IntelligenceSystem",
]
