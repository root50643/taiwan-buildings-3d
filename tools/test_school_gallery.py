"""Regression tests for primary navigation, not full-page link presence."""
import unittest
from unittest.mock import patch
import school_gallery as g

PAGE='國立聯合大學/README.md'
R1='國立聯合大學/buildings/a'
R2='國立聯合大學/buildings/b'
CARD=lambda r: f'[<img src="buildings/{r}/previews/front.png">](buildings/{r}/README.md)'
TABLE=lambda cells:'| 建築模型 | 建築模型 | 建築模型 |\n| :---: | :---: | :---: |\n| '+' | '.join(cells)+' |\n'
class GalleryTests(unittest.TestCase):
    def test_primary_does_not_include_footer(self):
        text=TABLE([CARD('a'),'',''])+'\n## 新增\n'+CARD('b')
        ls,a,b=g.table(text,PAGE,[R1,R2]);self.assertEqual(g.identities(''.join(ls[a:b]),PAGE,[R1,R2]),{R1})
    def test_adjacent_tables_are_one_gallery(self):
        text=TABLE([CARD('a'),'',''])+'\n'+TABLE([CARD('b'),'',''])+'\n## 說明\n'
        ls,a,b=g.table(text,PAGE,[R1,R2]);self.assertEqual(g.identities(''.join(ls[a:b]),PAGE,[R1,R2]),{R1,R2})
    def test_angle_urls(self):
        self.assertEqual(g.resolve('<buildings/a/README.md>',PAGE),R1+'/README.md')
    def test_appearance_is_same_package(self):
        self.assertEqual(g.identities('[配色](buildings/a/appearance/README.md)',PAGE,[R1]),{R1})
    def test_list_footer_is_not_primary(self):
        t='- [A](buildings/a/)\n\n## 新增：B\n[B](buildings/b/)'
        self.assertEqual(g.primary_list(t,PAGE,[R1,R2])[1],{R1})
    def run_audit(self,text):
        fs={R1+'/previews/front.png',R1+'/README.md',R2+'/previews/front.png',R2+'/README.md'}
        with patch.object(g,'read',return_value=text),patch.object(g,'FILES',fs):return g.audit(PAGE,[R1,R2])
    def test_missing_fails_even_if_footer_has_link(self):
        r=self.run_audit(TABLE([CARD('a'),'',''])+'\n## 新增\n'+CARD('b'));self.assertIn('missing_packages',r['errors'])
    def test_duplicate_generated_card_fails(self):
        r=self.run_audit(TABLE([CARD('a'),CARD('a'),CARD('b')]));self.assertIn('duplicate_generated_cards',r['errors'])
    def test_nonterminal_blank_fails(self):
        r=self.run_audit(TABLE([CARD('a'),'',CARD('b')]));self.assertIn('non_terminal_padding',r['errors'])
    def test_complete_padded_gallery_passes(self):
        self.assertEqual(self.run_audit(TABLE([CARD('a'),CARD('b'),'']))['errors'],[])
    def test_two_angle_same_package_not_duplicate_card(self):
        t='| 正面 | 背面 |\n|---|---|\n| '+CARD('a')+' | '+CARD('a')+' |\n\n'+TABLE([CARD('b'),'',''])
        self.assertEqual(self.run_audit(t)['errors'],[])
    def test_linked_header_image_and_download_rows_are_one_catalog(self):
        t='| [A](buildings/a/) | [B](buildings/b/) | |\n|---|---|---|\n| '+CARD('a')+' | '+CARD('b')+' | |\n| [A來源](buildings/a/README.md) | [B來源](buildings/b/README.md) | |\n'
        self.assertEqual(self.run_audit(t)['errors'],[])
    def test_complete_non_table_sync_is_unchanged(self):
        t='# 圖鑑\n\n### [A](buildings/a/)\n\n### [B](buildings/b/)\n'
        with patch.object(g,'read',return_value=t):self.assertFalse(g.sync(PAGE,[R1,R2]))
    def test_stale_appearance_detected(self):
        text=TABLE([CARD('a'),CARD('b'),'']);fs={R1+'/previews/front.png',R1+'/appearance/previews/front.png',R1+'/README.md',R2+'/previews/front.png',R2+'/README.md'}
        with patch.object(g,'read',return_value=text),patch.object(g,'FILES',fs):self.assertIn('stale_preview',g.audit(PAGE,[R1,R2])['errors'])
if __name__=='__main__':unittest.main()
