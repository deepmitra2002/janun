from typing import Literal
from pydantic import BaseModel, Field, field_validator

class ChatTurn(BaseModel):
    role: Literal['user','assistant']
    content: str = Field(min_length=1,max_length=2000)

class ChatInput(BaseModel):
    history: list[ChatTurn] = Field(default_factory=list,max_length=6)
    question: str = Field(min_length=2,max_length=2000)
    language: Literal['auto','en','bn','banglish'] = 'auto'
    @field_validator('question')
    @classmethod
    def strip_question(cls,v):
        v=v.strip()
        if len(v)<2: raise ValueError('Please enter a question')
        return v
class FeedbackInput(BaseModel):
    message: str = Field(min_length=5,max_length=2000)
    service_slug: str | None = Field(default=None,max_length=120)
class LoginInput(BaseModel):
    username: str = Field(min_length=1,max_length=120)
    password: str = Field(min_length=1,max_length=256)
class ServiceInput(BaseModel):
    slug: str = Field(pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$',max_length=120)
    name_en: str = Field(min_length=2,max_length=200)
    name_bn: str = Field(min_length=2,max_length=200)
    category: str = Field(max_length=80)
    description_en: str = Field(default='',max_length=1000)
    description_bn: str = Field(default='',max_length=1000)
    official_url: str = Field(default='',max_length=2000)
class SourceInput(BaseModel):
    service_id: str
    url: str = Field(max_length=2000)
    title: str = Field(min_length=2,max_length=300)
    agency: str = Field(default='',max_length=200)
class ReadinessCondition(BaseModel):
    id: str = Field(min_length=1,max_length=100)
    answer: Literal['yes','no','unsure']

class ReadinessQuestion(BaseModel):
    id: str = Field(min_length=1,max_length=100)
    text: str = Field(min_length=4,max_length=1000)
    kind: Literal['document','eligibility']
    when: ReadinessCondition | None = None


class Claims(BaseModel):
    readiness_questions: list[ReadinessQuestion] = Field(default_factory=list,max_length=60)
    @field_validator('readiness_questions')
    @classmethod
    def ordered_conditions(cls,questions):
        seen=set()
        for q in questions:
            if q.id in seen:raise ValueError('Duplicate readiness question ID')
            if q.when and q.when.id not in seen:raise ValueError('A condition must refer to an earlier question')
            seen.add(q.id)
        return questions
    eligibility: list[str] = Field(default_factory=list,max_length=30)
    documents: list[str] = Field(default_factory=list,max_length=30)
    steps: list[str] = Field(default_factory=list,max_length=30)
    fees: str | None = Field(default=None,max_length=1000)
    processing_time: str | None = Field(default=None,max_length=1000)
    deadline: str | None = Field(default=None,max_length=1000)
    @field_validator('eligibility','documents','steps')
    @classmethod
    def bounded_items(cls,v):
        if any(not x.strip() or len(x)>1000 for x in v): raise ValueError('Each item must be 1–1000 characters')
        return v
class ReviewInput(BaseModel):
    status: Literal['review','verified','published','rejected','stale','archived']
    note: str = Field(min_length=5,max_length=2000)
    review_days: int = Field(default=30,ge=1,le=180)
    claims: Claims | None = None
class JourneyInput(BaseModel):
    goal: str = Field(min_length=2,max_length=1000)
    language: Literal['en','bn'] = 'en'

class CheckInput(BaseModel):
    text: str = Field(min_length=4,max_length=20000)
    service_slug: str = Field(min_length=1,max_length=120,pattern=r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
    language: Literal['bn','en'] = 'bn'
    @field_validator('text')
    @classmethod
    def meaningful_text(cls,v):
        if len(v.strip())<4:raise ValueError('Enter a complete statement')
        return v.strip()
