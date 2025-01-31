from enum import Enum, auto

class NewsSource(Enum):
    OPENAI = "OPENAI"
    GROQ = "GROQ"
    ANTHROPIC = "ANTHROPIC"
    META = "META"
    DEEPSEEK = "DEEPSEEK"
    GROK = "GROK"

class ScraperStatus(Enum):
    SUCCESS = auto()
    PARTIAL = auto()
    FAILED = auto()