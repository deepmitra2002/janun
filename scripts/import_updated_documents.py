"""Stage exactly five new DOCX inputs for human review; never publish automatically.
Extracts paragraphs, table text, hyperlinks and embedded evidence with SHA256 provenance.
Usage: python scripts/import_updated_documents.py INPUT_DIR OUTPUT_DIR
"""
import hashlib,json,sys,zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

def stage(input_dir,output_dir):
    files=sorted(Path(input_dir).glob('*.docx'))
    if len(files)!=5:raise ValueError('Supply exactly five NEW Word documents; older team ZIP datasets are not replacements.')
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    reports=[];ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for index,path in enumerate(files):
        raw=path.read_bytes()
        if len(raw)>25*1024*1024:raise ValueError('DOCX exceeds 25 MB intake limit')
        with zipfile.ZipFile(path) as z:
            if sum(i.file_size for i in z.infolist())>100*1024*1024:raise ValueError('Expanded DOCX exceeds intake limit')
            doc=ET.fromstring(z.read('word/document.xml'));paragraphs=[]
            for i,p in enumerate(doc.findall('.//w:p',ns)):
                text=''.join(t.text or '' for t in p.findall('.//w:t',ns)).strip()
                if text:paragraphs.append({'paragraph_index':i,'text':text,'review_status':'pending','matched_service_slug':None,'source_urls':[],'effective_date':None,'conflicts':[]})
            links=[]
            if 'word/_rels/document.xml.rels' in z.namelist():
                rels=ET.fromstring(z.read('word/_rels/document.xml.rels'))
                links=[r.attrib.get('Target','') for r in rels if r.attrib.get('Type','').endswith('/hyperlink') and r.attrib.get('Target','').startswith(('https://','http://'))]
            media=[]
            for entry in z.infolist():
                if entry.filename.startswith('word/media/') and not entry.is_dir():
                    data=z.read(entry);digest=hashlib.sha256(data).hexdigest();name=f'{index+1}-{digest[:12]}{Path(entry.filename).suffix}'
                    (out/name).write_bytes(data);media.append({'filename':name,'sha256':digest,'original_path':entry.filename})
            reports.append({'document_name':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'review_status':'pending','paragraphs_including_table_cells':paragraphs,'hyperlinks':links,'embedded_evidence':media})
    target=out/'pending-document-intake.json';target.write_text(json.dumps({'status':'requires_human_mapping_and_review','documents':reports},ensure_ascii=False,indent=2));return target
if __name__=='__main__':print(stage(*sys.argv[1:]))
