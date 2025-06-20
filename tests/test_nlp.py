from xwe.core.nlp import NLPConfig, NLPProcessor


def test_nlp_parsing():
    nlp = NLPProcessor(None, NLPConfig(enable_llm=False))
    samples = [
        "我想攻击那个妖兽",
        "看看我的状态",
        "去坊市逛逛",
    ]
    for text in samples:
        result = nlp.parse(text)
        assert result.command_type is not None
