"""Operator commands. Run migrations before these commands."""
import argparse,getpass
from sqlalchemy import select
from .database import SessionLocal
from .models import Admin,Category,Service
from .security import password_hash

CATEGORIES=[('identity','Identity & registration','পরিচয় ও নিবন্ধন','id'),('passport','Passport & travel','পাসপোর্ট ও ভ্রমণ','plane'),('education','Education','শিক্ষা','education'),('business','Work & business','কর্মসংস্থান ও ব্যবসা','briefcase'),('transport','Driving & transport','ড্রাইভিং ও পরিবহন','car'),('tax','Tax & finance','কর ও অর্থ','landmark'),('welfare','Health & welfare','স্বাস্থ্য ও কল্যাণ','heart'),('legal','Police & legal services','পুলিশ ও আইনি সেবা','shield')]
# Research targets only. Never published by seed, and no requirements are invented.
SERVICES=[('e-passport','E-passport','ই-পাসপোর্ট','passport','https://www.epassport.gov.bd/'),('birth-registration','Birth registration','জন্ম নিবন্ধন','identity','https://bdris.gov.bd/'),('birth-correction','Birth registration correction','জন্ম নিবন্ধন সংশোধন','identity','https://bdris.gov.bd/'),('death-registration','Death registration','মৃত্যু নিবন্ধন','identity','https://bdris.gov.bd/'),('nid-correction','NID information and correction','এনআইডি তথ্য ও সংশোধন','identity',''),('police-clearance','Police clearance','পুলিশ ক্লিয়ারেন্স','legal',''),('certificate-attestation','Certificate attestation','সনদ সত্যায়ন','education',''),('trade-licence','Trade licence','ট্রেড লাইসেন্স','business',''),('e-tin','e-TIN','ই-টিআইএন','tax',''),('driving-licence','Driving licence','ড্রাইভিং লাইসেন্স','transport','')]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['seed','create-admin','import-team-data','import-verified-documents']);args=parser.parse_args()
    with SessionLocal() as db:
        if args.command=='import-verified-documents':
            import json
            from .document_release import import_document_release
            print(json.dumps(import_document_release(db),ensure_ascii=False))
        elif args.command=='import-team-data':
            import json
            from .team_data import import_drafts
            print(json.dumps(import_drafts(db),ensure_ascii=False))
        elif args.command=='seed':
            for slug,en,bn,icon in CATEGORIES:
                if not db.get(Category,slug):db.add(Category(slug=slug,name_en=en,name_bn=bn,icon=icon))
            db.flush()
            for slug,en,bn,cat,url in SERVICES:
                if not db.scalar(select(Service).where(Service.slug==slug)):
                    db.add(Service(slug=slug,name_en=en,name_bn=bn,category=cat,official_url=url,status='draft'))
            db.commit();print('Categories and draft research targets initialized. No guidance was published.')
        else:
            username=input('Admin username: ').strip()
            if not username or len(username)>120:raise SystemExit('Username must contain 1–120 characters')
            if db.scalar(select(Admin).where(Admin.username==username)):raise SystemExit('Username already exists')
            password=getpass.getpass('Password (at least 14 characters): ')
            if len(password)<14 or len(password)>256:raise SystemExit('Password must contain 14–256 characters')
            if password!=getpass.getpass('Confirm password: '):raise SystemExit('Passwords do not match')
            db.add(Admin(username=username,password_hash=password_hash(password)));db.commit();print('Administrator created.')
if __name__=='__main__':main()
