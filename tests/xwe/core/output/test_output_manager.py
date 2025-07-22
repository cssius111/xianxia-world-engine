from src.xwe.core.output import (
    ConsoleChannel,
    FileChannel,
    MessageType,
    OutputManager,
    OutputMessage,
    get_default_output_manager,
)


def test_default_output_manager_basic():
    manager = get_default_output_manager()
    assert manager.channels
    channel = manager.channels[0]
    manager.send_message(OutputMessage("hello", MessageType.INFO))
    assert hasattr(channel, "messages")
    assert any("hello" in m for m in channel.messages)


def test_output_manager_with_file(tmp_path):
    console = ConsoleChannel()
    file_path = tmp_path / "out.log"
    file_channel = FileChannel(str(file_path))
    manager = OutputManager([console, file_channel])

    manager.send_message(OutputMessage("file test"))

    assert console.messages
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "file test" in content
