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
class Claims(BaseModel):
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
