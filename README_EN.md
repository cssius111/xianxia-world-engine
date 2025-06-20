# Xianxia World Engine

A modular and extensible text adventure engine designed for xianxia themed games.

## 🎮 Quick Start

### Run the Game
```bash
poetry run run-game
```

### Basic Commands
```
New Game Zhang San    # create a new character
Continue              # load the latest save
Help                  # list all commands
Exit                  # quit the game
```

## 🏗️ Project Structure

```
xianxia_world_engine/
├── xwe/                    # core code
│   ├── core/              # main modules
│   │   ├── state/         # state management
│   │   ├── output/        # output system
│   │   ├── command/       # command handling
│   │   └── orchestrator.py # game orchestrator
│   ├── features/          # gameplay features
│   └── data/             # game data
├── examples/             # example code
├── tests/               # test suite
├── docs/                # documentation
└── scripts/run_game.py         # quick start script
```

## 🚀 Features

### Core
- ✅ Modular architecture for easy extension
- ✅ Multiple output channels (console, file, HTML)
- ✅ Natural language command processing
- ✅ Event-driven state management
- ✅ Automatic save and load
- ✅ Rich set of built-in commands

### Technical Highlights
- 🐍 Python 3.11+
- 📝 Complete type hints
- ⚡ Async support
- 🧪 Comprehensive unit tests
- 📚 Detailed documentation

## 💻 Development Guide

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Tests
```bash
pytest tests/
```

> **Note**: Item IDs are recommended to use plural forms such as `spirit_stones`. The old form `spirit_stone` is still accepted.

### Create a Custom Game
```python
from xwe.core.orchestrator import GameConfig, GameOrchestrator

# Configure the game
config = GameConfig(
    game_name="My Xianxia World",
    enable_html=True,
    auto_save_enabled=True
)

# Create and run the game
game = GameOrchestrator(config)
game.run_sync()
```

### Add a New Command
```python
from xwe.core.command import CommandHandler, CommandResult

class CustomHandler(CommandHandler):
    def can_handle(self, context):
        return context.raw_input.startswith("custom")

    def handle(self, context):
        context.output_manager.info("Executing custom command")
        return CommandResult.success()

# Register the handler
game.command_processor.register_handler(CustomHandler())
```

## 📖 Documentation

See the `docs/` directory for details:
- [Architecture](docs/architecture/modular_design.md)
- [API](docs/api/)
- [Migration Guide](docs/migration/)
- [Examples](examples/)

## 🎯 Gameplay

### Basic Commands
- **Move**: `go <place>`
- **Explore**: `explore`
- **Combat**: `attack`, `defend`, `escape`
- **Cultivation**: `train`, `breakthrough`
- **Interaction**: `talk to <NPC>`, `trade`
- **Items**: `inventory`, `use <item>`
- **Info**: `status`, `map`, `skills`

### Game Goal
Cultivate to immortality in the xianxia world, experiencing adventures and ascending to the heavens.

## 🛠️ Configuration Options

Create `game_config.json`:
```json
{
    "game_name": "Xianxia World",
    "game_mode": "player",
    "enable_console": true,
    "enable_html": true,
    "console_colored": true,
    "auto_save_enabled": true,
    "auto_save_interval": 300.0
}
```

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome!

## 📄 License

MIT License

## 🙏 Acknowledgments

Thanks to everyone who contributed to this project.

---

**Enjoy your journey through the Xianxia world!** 🗡️✨
