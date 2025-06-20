from unittest.mock import patch

from xwe_v2.plugins.enhanced_output import EnhancedGameOutput


class DummyLogger:
    def __init__(self):
        self.logs = []

    def add_log(self, text, category, is_continuation):
        self.logs.append((text, category, is_continuation))


def test_output_merging():
    logger = DummyLogger()
    output = EnhancedGameOutput(html_logger=logger)
    with patch.object(output, "_console_output"):
        output.output("- 第一条", "system")
        output.output("- 第二条", "system")

    assert logger.logs[0] == ("- 第一条", "system", False)
    assert logger.logs[1] == ("- 第二条", "system", True)


def test_combat_sequence():
    logger = DummyLogger()
    output = EnhancedGameOutput(html_logger=logger)
    with patch.object(output, "_console_output"):
        output.combat_sequence(["a", "b", "c"])

    assert len(logger.logs) == 1
    text, category, is_continuation = logger.logs[0]
    assert category == "combat"
    assert "a\nb\nc" in text
    assert not is_continuation
