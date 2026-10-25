import unittest
from datetime import datetime, timedelta, timezone
from app.domain import can_transition, is_fresh, normalize_query, validate_citations, order_steps, safe_url

class DomainTests(unittest.TestCase):
 def test_publication_requires_review(self):
  self.assertFalse(can_transition('pending','published'))
  self.assertTrue(can_transition('review','verified'))
  self.assertTrue(can_transition('verified','published'))
 def test_missing_or_expired_review_is_not_fresh(self):
  self.assertFalse(is_fresh(None))
  self.assertFalse(is_fresh(datetime.now(timezone.utc)-timedelta(seconds=1)))
  self.assertTrue(is_fresh(datetime.now(timezone.utc)+timedelta(days=1)))
 def test_banglish_adds_search_terms(self):
  self.assertIn('passport', normalize_query('  passport korte ki lage  '))
  self.assertIn('birth', normalize_query('jonmo nibondhon'))
  self.assertIn('passport', normalize_query('পাসপোর্ট করতে চাই'))
 def test_reject_fabricated_citation(self):
  self.assertEqual(validate_citations(['a','a','b'], {'a'}), ['a'])
 def test_dependencies_ordered_and_cycles_rejected(self):
  steps=[{'id':'b','depends_on':['a']},{'id':'a','depends_on':[]}]
  self.assertEqual([x['id'] for x in order_steps(steps)],['a','b'])
  with self.assertRaises(ValueError): order_steps([{'id':'a','depends_on':['a']}])
 def test_ingestion_url_boundaries(self):
  self.assertTrue(safe_url('https://www.mygov.bd/services', {'www.mygov.bd'}))
  for url in ['http://www.mygov.bd','https://www.mygov.bd.evil.com','https://u:p@www.mygov.bd','https://127.0.0.1','https://www.mygov.bd:444']:
   self.assertFalse(safe_url(url, {'www.mygov.bd'}))

if __name__=='__main__': unittest.main()
