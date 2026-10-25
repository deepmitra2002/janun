"""Explicitly submitted audio only. No file, text or provider response is persisted."""
from io import BytesIO
from fastapi import APIRouter,Request,HTTPException,UploadFile,File,Form
from fastapi.responses import Response
from pydantic import BaseModel,Field
from typing import Literal
from .config import settings
from .security import limiter
from .ai import client
router=APIRouter(prefix='/api/speech')
MAX_AUDIO=5_000_000

def audio_signature(data,kind):
    return ((kind in ('audio/webm','video/webm') and data.startswith(b'\x1aE\xdf\xa3')) or
       (kind in ('audio/wav','audio/x-wav') and data[:4]==b'RIFF' and data[8:12]==b'WAVE') or
       (kind in ('audio/mp4','audio/x-m4a') and data[4:8]==b'ftyp') or
       (kind=='audio/ogg' and data.startswith(b'OggS')))

@router.post('/transcribe')
async def transcribe(request:Request,file:UploadFile=File(...),language:Literal['bn','en']=Form('bn')):
    limiter.check('speech-in:'+request.client.host,5,60)
    if not settings.openai_api_key or not settings.speech_transcription_model:raise HTTPException(503,'Server speech recognition is not configured. Use text input.')
    try:
        data=await file.read(MAX_AUDIO+1)
        if not data or len(data)>MAX_AUDIO:raise HTTPException(413,'Audio must be non-empty and at most 5 MB.')
        kind=(file.content_type or '').split(';')[0]
        if not audio_signature(data,kind):raise HTTPException(415,'Unsupported or invalid audio file.')
        audio=BytesIO(data);audio.name='question.'+('wav' if 'wav' in kind else 'mp4' if 'mp4' in kind else 'ogg' if 'ogg' in kind else 'webm')
        import asyncio
        try:
            result=await asyncio.to_thread(client().audio.transcriptions.create,model=settings.speech_transcription_model,file=audio,language=language)
        except Exception:raise HTTPException(503,'Speech provider unavailable. Use text input.')
        return {'text':result.text[:2000],'language':language}
    finally:await file.close()

class SpeakInput(BaseModel):
    text:str=Field(min_length=1,max_length=8000)
    language:Literal['bn','en']='bn'

@router.post('/speak')
async def speak(data:SpeakInput,request:Request):
    limiter.check('speech-out:'+request.client.host,5,60)
    voice=settings.speech_voice_bn if data.language=='bn' else settings.speech_voice_en
    if not settings.openai_api_key or not settings.speech_synthesis_model or not voice:raise HTTPException(503,'Server speech playback is not configured. Read the displayed answer.')
    import asyncio
    try:
        result=await asyncio.to_thread(client().audio.speech.create,model=settings.speech_synthesis_model,voice=voice,input=data.text,response_format='mp3')
        return Response(result.content,media_type='audio/mpeg',headers={'Cache-Control':'no-store'})
    except Exception:raise HTTPException(503,'Speech provider unavailable. Read the displayed answer.')
