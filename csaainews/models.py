from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class Paper:
    arxiv_id: str
    title: str
    authors: list[str]
    abstract: str
    submitted_date: datetime
    updated_date: datetime
    arxiv_id_url: str
    pdf_url: str
    primary_category: str

@dataclass
class Review:
    relevant: bool
    rationale: str
    relevance: int = 0
    novelty: int = 0
    methodological_quality: int = 0
    enterprise_service_relevance: int = 0
    summary: str = ""
    trends: list[str] = field(default_factory=list)
    framework_notes: str = ""
    practical_implications: str = ""
    service_research_implications: str = ""

    @property
    def weighted_score(self) -> float:
        return self.relevance * .40 + self.novelty * .25 + self.methodological_quality * .20 + self.enterprise_service_relevance * .15
