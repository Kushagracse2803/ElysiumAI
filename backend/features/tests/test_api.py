from types import SimpleNamespace

from features.resume_analyzer import resume_expert


class DummyCompletions:
    def create(self, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="resume analysis ok"))]
        )


class DummyGroqClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=DummyCompletions())


def test_resume_analyzer_is_callable_from_app_flow():
    result = resume_expert.analyze_resume("John Doe\nPython, SQL", DummyGroqClient(), "fake-model")

    assert result == "resume analysis ok"
