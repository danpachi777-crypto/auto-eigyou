#!/usr/bin/env python3
"""Record a Gmail-verified recovery proposal; never sends email."""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from email.utils import parseaddr
from delivery_budget import connect, confirm
from storage_guard import reclaim

ROOT = Path(__file__).resolve().parent
slug, proof_path = sys.argv[1:]
proof = json.loads(Path(proof_path).read_text())
review = json.loads((ROOT / 'runs/kz-20261020-163105/website-reviews' / (slug+'.json')).read_text())
headers = {h['name'].lower(): h['value'] for h in proof['payload']['headers']}
email = review['email'].strip().lower()
assert 'SENT' in proof['label_ids']
assert parseaddr(headers['from'])[1] == 'contact.designdan@gmail.com'
assert parseaddr(headers['to'])[1].lower() == email
stamp = datetime.fromtimestamp(int(proof['internal_date'])/1000, timezone.utc).isoformat()
emls = list((ROOT/'eml').glob('*/'+slug+'.eml'))
assert len(emls) == 1
eml = emls[0]
ledger = ROOT/'ledger.csv'
rows = list(csv.DictReader(ledger.open(encoding='utf-8-sig')))
assert not any(r['email'].lower() == email for r in rows)
with connect() as connection:
    confirm(connection, email, proof['id'], stamp)
row = dict.fromkeys(rows[0], '')
row.update(run_date=eml.parent.name,company=review['company'],industry=review.get('industry',''),region=review.get('region',''),email=email,source_url=review.get('discovery_source',''),website_url=review.get('website_url',review.get('website','')),checked_at=review.get('checked_at',''),eml_path=str(eml.relative_to(ROOT)),home_image_path=f'assets/{eml.parent.name}/{slug}/home.jpg',inquiry_image_path=f'assets/{eml.parent.name}/{slug}/inquiry.jpg',delivery_status='sent',gmail_sent_message_id=proof['id'],sent_at=stamp,campaign_id='kz-20261020-163105')
with ledger.open('a',encoding='utf-8',newline='') as stream:
    csv.DictWriter(stream,fieldnames=list(rows[0])).writerow(row)
rows.append(row)
count=sum(r['campaign_id']=='kz-20261020-163105' and r['delivery_status']=='sent' for r in rows)
cp=ROOT/'recovery-checkpoint.json'
d=json.loads(cp.read_text()); d['verified_sent_last_known']=count; d['remaining_unsent_target']=450-count
d.setdefault('sent_from_recovery',[]).append(slug)
d['remaining_prepared_unsent']=len(set(d['prepared'])-set(d['sent_from_recovery']))
d['status']='sending_authorized';cp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
reclaim()
print(json.dumps({'slug':slug,'verified_sent':count,'message_id':proof['id']}))
