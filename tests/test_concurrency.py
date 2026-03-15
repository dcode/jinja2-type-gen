import asyncio

from jinja2_type_gen import TemplateTypeAnalyzer


async def analyze_template(analyzer: TemplateTypeAnalyzer, source: str) -> dict:
    # A dummy async wrapper around our synchronous parser to simulate
    # concurrent tasks extracting signatures.
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, analyzer.analyze_source, source)


def test_concurrent_analysis():
    analyzer = TemplateTypeAnalyzer()

    templates = [
        "{% signature a: int %}",
        "{% signature b: str %}",
        "{% signature c: bool %}",
        "{% signature d: float %}",
        "{% signature e: list[int] %}",
    ]

    async def _run():
        return await asyncio.gather(*(analyze_template(analyzer, t) for t in templates))

    results = asyncio.run(_run())

    assert len(results) == 5
    assert "a" in results[0]
    assert "b" in results[1]
    assert "c" in results[2]
    assert "d" in results[3]
    assert "e" in results[4]
