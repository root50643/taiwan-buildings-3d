"""Regression tests for primary navigation, not full-page link presence."""
import pathlib, re, tempfile, unittest
from unittest.mock import patch
import school_gallery as g

PAGE='國立聯合大學/README.md'
R1='國立聯合大學/buildings/a'
R2='國立聯合大學/buildings/b'
CARD=lambda r: f'[<img src="buildings/{r}/previews/front.png">](buildings/{r}/README.md)'
TABLE=lambda cells:'| 建築模型 | 建築模型 | 建築模型 |\n| :---: | :---: | :---: |\n| '+' | '.join(cells)+' |\n'
class RepresentativeTests(unittest.TestCase):
    def setUp(self):
        self.choice={'A':{'gallery':'A/README.md','cover':'A/buildings/old/previews/front.png'}}
        self.registry={'schools':{'A':dict(self.choice['A'],count=2)}}
        self.files=set(self.choice['A'].values())|{'A/buildings/new/previews/front.png'}
        self.text='[<img src="A/buildings/old/previews/front.png" width="260">](A/README.md)'
    def check(self):
        return g.homepage_representative_errors(self.text,self.choice,self.registry,{'A'},self.files)
    def test_adding_model_keeps_selection(self):
        self.assertEqual(self.check(),[])
    def test_homepage_reselection_rejected(self):
        self.text=self.text.replace('/old/','/new/');self.assertIn('homepage_representative_changed:A',self.check())
    def test_registry_reselection_rejected(self):
        self.registry['schools']['A']['cover']='A/buildings/new/previews/front.png'
        self.assertIn('registry_representative_changed:A',self.check())
    def test_joint_automatic_reselection_rejected(self):
        self.text=self.text.replace('/old/','/new/');self.registry['schools']['A']['cover']='A/buildings/new/previews/front.png'
        self.assertEqual(len(self.check()),2)
    def test_explicit_selection_update_accepted(self):
        self.text=self.text.replace('/old/','/new/')
        self.choice['A']['cover']=self.registry['schools']['A']['cover']='A/buildings/new/previews/front.png'
        self.assertEqual(self.check(),[])
    def test_missing_selected_path_rejected(self):
        self.files.remove(self.choice['A']['cover']);self.assertIn('representative_missing_path:A',self.check())
    def test_duplicate_homepage_card_rejected(self):
        self.text+=self.text;self.assertIn('homepage_representative_changed:A',self.check())
    def test_missing_school_selection_rejected(self):
        self.choice={};self.assertEqual(self.check(),['representative_school_set'])
    def test_image_bytes_not_locked(self):
        self.assertEqual(set(self.choice['A']),{'gallery','cover'});self.assertEqual(self.check(),[])


class PendingRepresentativeTests(unittest.TestCase):
    def setUp(self):
        self.choice={'N':{'gallery':'N/README.md','cover':None,'status':'pending_user_selection'}}
        self.registry={'schools':{'N':dict(self.choice['N'],count=1)}}
        self.files={'N/README.md','N/buildings/first/previews/front.png','A/cover.png'}
        self.text=TABLE(['**[N｜1 組](N/README.md)**<br>代表圖待指定','',''])
    def check(self):
        return g.homepage_representative_errors(self.text,self.choice,self.registry,{'N'},self.files)
    def test_pending_text_only_accepted(self):self.assertEqual(self.check(),[])
    def test_null_without_marker_rejected(self):
        del self.choice['N']['status'];self.assertTrue(self.check())
    def test_missing_null_key_rejected(self):
        del self.choice['N']['cover'];self.assertIn('pending_representative_state:N',self.check())
    def test_missing_registry_null_rejected(self):
        del self.registry['schools']['N']['cover'];self.assertTrue(self.check())
    def test_registry_state_mismatch_rejected(self):
        del self.registry['schools']['N']['status'];self.assertTrue(self.check())
    def test_pending_chosen_cover_rejected(self):
        self.choice['N']['cover']='N/buildings/first/previews/front.png';self.assertTrue(self.check())
    def test_registry_autoselection_rejected(self):
        self.registry['schools']['N']['cover']='N/buildings/first/previews/front.png';self.assertTrue(self.check())
    def test_registry_cover_bypass_rejected(self):
        self.choice['N']['registry_cover']=None;self.assertTrue(self.check())
    def test_missing_gallery_rejected(self):
        self.files.remove('N/README.md');self.assertTrue(self.check())
    def test_pending_borrowed_school_gallery_rejected(self):
        self.choice['N']['gallery']=self.registry['schools']['N']['gallery']='A/README.md'
        self.files.add('A/README.md');self.text=self.text.replace('N/README.md','A/README.md');self.assertTrue(self.check())
    def test_duplicate_text_card_rejected(self):
        self.text+=self.text;self.assertTrue(self.check())
    def test_missing_text_card_rejected(self):
        self.text='';self.assertTrue(self.check())
    def test_missing_visible_marker_rejected(self):
        self.text=self.text.replace('代表圖待指定','');self.assertTrue(self.check())
    def test_html_image_in_pending_card_rejected(self):
        self.text=self.text.replace('代表圖待指定','代表圖待指定<img src="A/cover.png">');self.assertTrue(self.check())
    def test_markdown_image_in_pending_card_rejected(self):
        self.text=self.text.replace('代表圖待指定','代表圖待指定 ![借圖](A/cover.png)');self.assertTrue(self.check())
    def test_reference_image_in_pending_card_rejected(self):
        self.text=self.text.replace('代表圖待指定','代表圖待指定 ![borrow][borrowed]')+'\n[borrowed]: A/cover.png'
        self.assertTrue(self.check())
    def test_collapsed_reference_image_rejected(self):
        self.text=self.text.replace('代表圖待指定','代表圖待指定 ![borrow][]')+'\n[borrow]: A/cover.png'
        self.assertTrue(self.check())
    def test_shortcut_reference_image_rejected(self):
        self.text=self.text.replace('代表圖待指定','代表圖待指定 ![borrow]')+'\n[borrow]: A/cover.png'
        self.assertTrue(self.check())
    def test_collapsed_html_marker_rejected(self):
        self.text=self.text.replace('代表圖待指定','<details><summary>more</summary><br>代表圖待指定<br></details>');self.assertTrue(self.check())
    def test_hidden_html_marker_with_breaks_rejected(self):
        self.text=self.text.replace('代表圖待指定','<span hidden><br>代表圖待指定<br></span>');self.assertTrue(self.check())
    def test_reference_image_elsewhere_rejected(self):
        self.text+='\n![own][new]\n[new]: N/buildings/first/previews/front.png';self.assertTrue(self.check())
    def test_commented_pending_marker_rejected(self):
        self.text=self.text.replace('代表圖待指定','<!--代表圖待指定-->');self.assertTrue(self.check())
    def test_hidden_pending_marker_rejected(self):
        self.text=self.text.replace('代表圖待指定','<span style="display:none">代表圖待指定</span>');self.assertTrue(self.check())
    def test_own_image_elsewhere_rejected(self):
        self.text+='\n![own](N/buildings/first/previews/front.png)';self.assertTrue(self.check())
    def test_html_own_image_elsewhere_rejected(self):
        self.text+='\n<img src="N/buildings/first/previews/front.png">';self.assertTrue(self.check())
    def test_unrelated_selected_school_accepted(self):
        self.choice['A']={'gallery':'A/README.md','cover':'A/cover.png'}
        self.registry['schools']['A']=dict(self.choice['A'],count=2)
        self.files.add('A/README.md');self.text+='[<img src="A/cover.png">](A/README.md)'
        self.assertEqual(g.homepage_representative_errors(self.text,self.choice,self.registry,{'N','A'},self.files),[])
    def test_unknown_status_rejected(self):
        self.choice['N']['status']='automatic';self.assertTrue(self.check())
    def test_coordinated_explicit_selection_accepted(self):
        for entry in (self.choice['N'],self.registry['schools']['N']):
            del entry['status'];entry['cover']='N/buildings/first/previews/front.png'
        self.text='[<img src="N/buildings/first/previews/front.png">](N/README.md)'
        self.assertEqual(self.check(),[])  # Consent still requires human/history review.

class GalleryTests(unittest.TestCase):
    def sync_text(self,text,expected):
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);path=root/PAGE;path.parent.mkdir(parents=True);path.write_text(text)
            fs={r+'/previews/front.png' for r in expected}|{r+'/README.md' for r in expected}
            with patch.object(g,'ROOT',root),patch.object(g,'read',side_effect=lambda p:(root/p).read_text()),patch.object(g,'FILES',fs),patch.object(g,'new_card',side_effect=lambda r,p:CARD(r.rsplit('/',1)[-1])):
                changed=g.sync(PAGE,expected)
                result=path.read_text()
                self.assertFalse(g.sync(PAGE,expected),'second sync must be idempotent')
            return changed,result
    def card_rows(self,text):
        blocks=re.findall(r'(?m)(?:^\|.*\n?)+',text)
        self.assertEqual(len(blocks),1)
        rows=[g.splitrow(row) for row in blocks[0].splitlines()[2:]]
        self.assertTrue(all(len(row)==3 for row in rows))
        return rows
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
    def test_unmigrated_legacy_two_angle_same_package_not_duplicate_card(self):
        t='| 正面 | 背面 |\n|---|---|\n| '+CARD('a')+' | '+CARD('a')+' |\n\n'+TABLE([CARD('b'),'',''])
        self.assertEqual(self.run_audit(t)['errors'],['fragmented_card_gallery','overview_not_one_image_per_building'])
    def test_linked_header_image_and_download_rows_are_one_catalog(self):
        t='| [A](buildings/a/) | [B](buildings/b/) | |\n|---|---|---|\n| '+CARD('a')+' | '+CARD('b')+' | |\n| [A來源](buildings/a/README.md) | [B來源](buildings/b/README.md) | |\n'
        self.assertEqual(self.run_audit(t)['errors'],[])
    def test_complete_non_table_sync_is_unchanged(self):
        t='# 圖鑑\n\n### [A](buildings/a/)\n\n### [B](buildings/b/)\n'
        with patch.object(g,'read',return_value=t):self.assertFalse(g.sync(PAGE,[R1,R2]))
    def test_latest_footer_is_not_non_table_primary(self):
        t='- [A](buildings/a/)\n\n## 最新新增：B\n[B](buildings/b/)'
        self.assertEqual(g.primary_list(t,PAGE,[R1,R2])[1],{R1})
    def test_new_footer_duplicate_is_rejected(self):
        text=TABLE([CARD('a'),CARD('b'),''])+'\n## 最新新增：A\n'+CARD('a')
        self.assertIn('duplicate_new_model_footer',self.run_audit(text)['errors'])
    def test_detailed_qa_and_expandable_history_are_preserved(self):
        text=TABLE([CARD('a'),CARD('b'),''])+'\n## 新增A限定覆核\n[A QA](buildings/a/README.md)\n\n## 新增館舍與建築群\n<details>\n'+CARD('a')+'\n</details>'
        self.assertEqual(self.run_audit(text)['errors'],[])
    def test_stale_appearance_detected(self):
        text=TABLE([CARD('a'),CARD('b'),'']);fs={R1+'/previews/front.png',R1+'/appearance/previews/front.png',R1+'/README.md',R2+'/previews/front.png',R2+'/README.md'}
        with patch.object(g,'read',return_value=text),patch.object(g,'FILES',fs):self.assertIn('stale_preview',g.audit(PAGE,[R1,R2])['errors'])
    def test_sync_fills_existing_row_and_preserves_full_card_and_footer(self):
        first=CARD('a')+'<br>**標題 A**<br>[下載](buildings/a/model.stl) · [來源](buildings/a/sources.md) · 外觀近似'
        footer='\n## 限制\n原有來源與說明不刪除。\n'
        changed,text=self.sync_text('# 圖鑑\n\n'+TABLE([first,CARD('b'),''])+footer,[R1,R2,R1[:-1]+'c'])
        self.assertTrue(changed)
        self.assertEqual(self.card_rows(text),[[first,CARD('b'),CARD('c')]])
        self.assertTrue(text.endswith(footer))
    def test_sync_consolidates_fragmented_cards_when_adding_sixth(self):
        roots=[R1[:-1]+x for x in 'abcdef']
        before=TABLE([CARD('a'),CARD('b'),'']).replace('建築模型','建物')+'\n'+''.join(TABLE([CARD(x),'',''])+'\n' for x in 'cde')
        changed,text=self.sync_text(before,roots)
        self.assertTrue(changed)
        self.assertEqual(self.card_rows(text),[[CARD(x) for x in 'abc'],[CARD(x) for x in 'def']])
    def test_sync_seventh_card_only_pads_last_row(self):
        roots=[R1[:-1]+x for x in 'abcdefg']
        _,text=self.sync_text(g.card_table([CARD(x) for x in 'abcdef']),roots)
        self.assertEqual(self.card_rows(text),[[CARD(x) for x in 'abc'],[CARD(x) for x in 'def'],[CARD('g'),'','']])
    def test_complete_fragmented_card_galleries_are_repaired(self):
        text=TABLE([CARD('a'),'',''])+'\n'+TABLE([CARD('b'),'',''])
        changed,result=self.sync_text(text,[R1,R2])
        self.assertTrue(changed);self.assertEqual(self.card_rows(result),[[CARD('a'),CARD('b'),'']])
    def test_complete_single_table_is_not_reformatted(self):
        text=TABLE([CARD('a'),CARD('b'),'']).replace('建築模型','建物')
        changed,result=self.sync_text(text,[R1,R2])
        self.assertFalse(changed);self.assertEqual(result,text)
    def test_specialized_multiline_and_multiangle_catalogs_are_preserved(self):
        layouts=[
            '| [A](buildings/a/) |  |  |\n|---|---|---|\n| '+CARD('a')+' |  |  |\n| [下載](buildings/a/model.stl) |  |  |\n',
            '| 建築模型 | 建築模型 | 建築模型 |\n|---|---|---|\n| '+CARD('a')+' | '+CARD('a')+' |  |\n',
            '| 正面 | 背面 |\n|---|---|\n| '+CARD('a')+' | '+CARD('a')+' |\n',
        ]
        for text in layouts:
            with self.subTest(text=text):
                _,result=self.sync_text(text+'\n## 說明\n保留\n',[R1,R2])
                rows=self.card_rows(result);self.assertEqual(len(rows),1)
                self.assertEqual(g.identities(rows[0][0],PAGE,[R1,R2]),{R1})
                self.assertEqual(rows[0][1],CARD('b'))
                for line in text.splitlines()[2:]:
                    for cell in g.splitrow(line):
                        if cell:self.assertIn(cell,rows[0][0])
                self.assertTrue(result.endswith('\n## 說明\n保留\n'))
    def test_named_columns_keep_headers_images_downloads_and_source_notes(self):
        text='| A 的限定名稱 | B 的限定名稱 |\n|---|---|\n| '+CARD('a')+' | '+CARD('b')+' |\n| [下載](buildings/a/model.stl) · 來源限定A | [來源](buildings/b/sources.md) · 限定B |\n\n'+TABLE([CARD('c'),'',''])
        _,result=self.sync_text(text,[R1,R2,R1[:-1]+'c'])
        row=self.card_rows(result)[0]
        self.assertEqual(row[0],'A 的限定名稱<br>'+CARD('a')+'<br>[下載](buildings/a/model.stl) · 來源限定A')
        self.assertEqual(row[1],'B 的限定名稱<br>'+CARD('b')+'<br>[來源](buildings/b/sources.md) · 限定B')
    def test_generic_headers_and_special_manufacturing_link_keep_exact_card(self):
        special=CARD('a').replace('buildings/a/README.md','buildings/a/manufacturing/v2/README.md')
        for header in ['| 建築一 | 建築二 | 建築三 |','| 模型 | 模型 | 模型 |','| 圖鑑 | 圖鑑 | 圖鑑 |','| 建築／模型 | 建築／模型 | 建築／模型 |']:
            with self.subTest(header=header):
                text=TABLE([special,'','']).replace('| 建築模型 | 建築模型 | 建築模型 |',header)+'\n'+TABLE([CARD('b'),'',''])
                _,result=self.sync_text(text,[R1,R2]);self.assertEqual(self.card_rows(result),[[special,CARD('b'),'']])
    def test_semantic_section_boundary_is_not_crossed(self):
        text=TABLE([CARD('a'),CARD('b'),''])+'\n## 歷史細節\n'+TABLE([CARD('a'),'',''])
        changed,result=self.sync_text(text,[R1,R2]);self.assertFalse(changed);self.assertEqual(result,text)
    def test_named_same_model_views_and_repeat_index_are_one_card(self):
        rear=CARD('a').replace('/front.png','/rear.png')
        text='| A 正面 | A 背面 |\n|---|---|\n| '+CARD('a')+' | '+rear+' |\n\n'+TABLE([CARD('b'),'',''])
        _,result=self.sync_text(text,[R1,R2]);row=self.card_rows(result)[0]
        self.assertIn('A 正面<br>'+CARD('a'),row[0]);self.assertIn('A 背面<br>',row[0]);self.assertNotIn(rear,row[0])
        self.assertEqual(row[1],CARD('b'))
    def test_placeholder_notes_do_not_become_fake_model_cards(self):
        text='| A | 後續 |\n|---|---|\n| '+CARD('a')+' | 尚未交付 |\n| [來源](buildings/a/sources.md) | [工作範圍](coverage/) |\n\n'+TABLE([CARD('b'),'',''])
        _,result=self.sync_text(text,[R1,R2]);self.assertEqual(len(self.card_rows(result)),1)
        self.assertIn('\n後續<br>尚未交付<br>[工作範圍](coverage/)\n',result)
    def test_unknown_model_or_image_is_not_hidden_as_note(self):
        for extra in [CARD('unknown'),'![unknown](unknown.png)']:
            text=TABLE([CARD('a'),extra,''])+'\n'+TABLE([CARD('b'),'',''])
            lines,a,b=g.table(text,PAGE,[R1,R2])
            self.assertIsNone(g.packed_gallery(lines,a,b,PAGE,[R1,R2]))
    def test_requested_galleries_have_one_packed_table(self):
        for page in ['國立陽明交通大學/光復校區/README.md','國立臺灣大學/README.md']:
            with self.subTest(page=page):
                expected=g.pages()[page];text=g.read(page)
                rows=self.card_rows(text);cells=[c for row in rows for c in row]
                self.assertEqual(len(rows),(len(expected)+2)//3)
                self.assertTrue(all(cells[:len(expected)]));self.assertFalse(any(cells[len(expected):]))
                ids=[g.identities(c,page,expected) for c in cells if c]
                self.assertTrue(all(len(x)==1 for x in ids));self.assertEqual(len(ids),len(expected))
                self.assertEqual(set().union(*ids),set(expected))
    def test_homepage_recent_sections_rejected_but_main_catalog_allowed(self):
        self.assertEqual(g.homepage_recent_sections('## 新增大專校院圖鑑\n## 模型範圍與限制\n'),[])
        self.assertEqual(len(g.homepage_recent_sections('## 最新新增：A\n## 最近新增的建築物\n')),2)
        self.assertEqual(g.homepage_recent_sections(g.read('README.md')),[])
    def test_mixed_markdown_and_bounded_previews_are_normalized_without_other_edits(self):
        first='[![A & B](buildings/a/previews/front.png)](buildings/a/README.md)<br>[下載](buildings/a/model.stl) · 限定文字'
        second=CARD('b').replace('front.png"','front.png" width="220"')
        before='# 圖鑑\n\n'+TABLE([first,second,''])+'\n## 說明\n![來源照](source.jpg)\n'
        self.assertIn('mixed_preview_widths',self.run_audit(before)['errors'])
        changed,after=self.sync_text(before,[R1,R2]);self.assertTrue(changed)
        expected=before.replace('![A & B](buildings/a/previews/front.png)','<img src="buildings/a/previews/front.png" alt="A &amp; B" width="220">')
        self.assertEqual(after,expected)
        self.assertNotIn('mixed_preview_widths',self.run_audit(after)['errors'])
    def test_overview_vertical_views_keep_first_angle_and_proportional_height(self):
        front=CARD('a').replace('front.png"','front.png" width="420" height="420"')
        rear=front.replace('front.png','rear.png')
        other=CARD('b').replace('front.png"','front.png" width="220"')
        before=TABLE([front+'<br>'+rear,other,''])
        _,after=self.sync_text(before,[R1,R2])
        self.assertEqual(after.count('width="220"'),2)
        self.assertNotIn('height=',after);self.assertNotIn('rear.png',after)
    def test_overview_single_image_normalization_is_width_idempotent(self):
        front=CARD('a').replace('front.png"','front.png" width="150"')
        pair=front+front.replace('front.png','rear.png')
        other=CARD('b').replace('front.png"','front.png" width="220"')
        before=TABLE([pair,other,''])
        changed,after=self.sync_text(before,[R1,R2])
        self.assertTrue(changed);self.assertEqual(after.count('<img'),2)
        self.assertNotIn('rear.png',after);self.assertEqual(after.count('width="220"'),2)
        self.assertEqual(g.mixed_preview_blocks(after,PAGE,[R1,R2]),[])
    def test_uniform_widths_hero_and_unknown_source_images_are_not_reformatted(self):
        for width in ['260','44%']:
            before=TABLE([CARD('a'),CARD('b'),'']).replace('front.png"','front.png" width="'+width+'"')
            self.assertEqual(g.normalize_mixed_preview_widths(before,PAGE,[R1,R2]),before)
        for before in ['![hero](buildings/a/previews/front.png)\n',TABLE(['![A](buildings/a/previews/front.png)','<img src="source.jpg" width="220">',''])]:
            self.assertEqual(g.normalize_mixed_preview_widths(before,PAGE,[R1,R2]),before)
    def test_all_unbounded_views_not_inferred_to_be_different_sizes(self):
        before=TABLE([CARD('a'),CARD('b'),''])
        self.assertEqual(g.normalize_mixed_preview_widths(before,PAGE,[R1,R2]),before)
    def test_new_cards_always_have_bounded_width_and_no_height(self):
        fs={R1+'/README.md',R1+'/previews/front.png'}
        with patch.object(g,'FILES',fs),patch.object(g,'read',return_value='# A\n'):
            card=g.new_card(R1,PAGE)
        self.assertIn('width="220"',card);self.assertNotIn('height=',card)
    def test_model_source_photo_is_not_mistaken_for_model_preview(self):
        before=TABLE(['![來源照](buildings/a/sources/exterior.jpg)',CARD('b').replace('front.png"','front.png" width="220"'),''])
        self.assertEqual(g.normalize_mixed_preview_widths(before,PAGE,[R1,R2]),before)
    def test_alt_entities_are_not_double_escaped(self):
        before=TABLE(['![A &amp; B](buildings/a/previews/front.png)',CARD('b').replace('front.png"','front.png" width="220"'),''])
        after=g.normalize_mixed_preview_widths(before,PAGE,[R1,R2])
        self.assertIn('alt="A &amp; B"',after);self.assertNotIn('&amp;amp;',after)
    def test_markdown_src_entities_are_not_double_escaped(self):
        before=TABLE(['![A](buildings/a/previews/front.png?raw=1&amp;foo=2)',CARD('b').replace('front.png"','front.png" width="220"'),''])
        after=g.normalize_mixed_preview_widths(before,PAGE,[R1,R2])
        self.assertIn('src="buildings/a/previews/front.png?raw=1&amp;foo=2"',after)
        self.assertEqual(g.preview_images(after)[0]['src'],'buildings/a/previews/front.png?raw=1&foo=2')
    def test_complex_markdown_image_syntax_is_preserved_conservatively(self):
        for image in ['![A **B**](buildings/a/previews/front.png)','![A](buildings/a/previews/front.png "title")',r'![A](buildings/a/previews/front\(1\).png)','![A](buildings/a/previews/front(1).png)']:
            before=TABLE([image,CARD('b').replace('front.png"','front.png" width="220"'),''])
            self.assertEqual(g.normalize_mixed_preview_widths(before,PAGE,[R1,R2]),before)
    def test_html_alt_dimension_words_are_not_parsed_as_attributes(self):
        first='<img src="buildings/a/previews/front.png" alt="Example height=420 and width=300" width="420">'
        second=CARD('b').replace('front.png"','front.png" width="220"')
        after=g.normalize_mixed_preview_widths(TABLE([first,second,'']),PAGE,[R1,R2])
        self.assertIn('alt="Example height=420 and width=300" width="220"',after)
        self.assertEqual([i['width'] for i in g.preview_images(after)],['220','220'])

class SingleImageOverviewTests(unittest.TestCase):
    def normalize(self,text,page=PAGE,expected=None):
        with patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',{page}):
            return g.normalize_overview_representatives(text,page,expected or [R1,R2])
    def test_linked_markdown_keeps_existing_front_and_all_other_links(self):
        rear='[![rear](buildings/a/previews/rear.png)](buildings/a/README.md) '
        front='[![front](buildings/a/previews/front.png)](buildings/a/README.md)'
        text=TABLE([front+' '+rear+'<br>[STL](buildings/a/model.stl) [QA](buildings/a/QA.md)',CARD('b'),''])
        after=self.normalize(text)
        self.assertEqual(after,text.replace(rear,''))
        self.assertEqual(self.normalize(after),after)
        self.assertNotIn('[](',after)
    def test_linked_html_removes_only_extra_image_markup(self):
        rear='[<img src="buildings/a/previews/rear.png" alt="rear">](buildings/a/) '
        text=TABLE([CARD('a')+' '+rear+'note',CARD('b'),''])
        self.assertEqual(self.normalize(text),text.replace(rear,''))
    def test_existing_special_view_is_retained_when_no_front_present(self):
        text=TABLE(['![chosen](buildings/a/previews/detail.png) ![other](buildings/a/previews/rear.png)',CARD('b'),''])
        after=self.normalize(text)
        self.assertIn('previews/detail.png',after);self.assertNotIn('previews/rear.png',after)
        self.assertNotIn('buildings/a/previews/front.png',after)
    def test_first_selected_view_is_not_replaced_by_a_later_front(self):
        text=TABLE(['![selected](buildings/a/previews/rear.png) ![later](buildings/a/previews/front.png)',CARD('b'),''])
        after=self.normalize(text)
        self.assertIn('buildings/a/previews/rear.png',after)
        self.assertNotIn('buildings/a/previews/front.png',after)
    def test_appearance_front_is_not_changed_to_original_asset(self):
        text=TABLE([CARD('a').replace('/previews/','/appearance/previews/')+' ![rear](buildings/a/appearance/previews/rear.png)',CARD('b'),''])
        after=self.normalize(text)
        self.assertIn('/appearance/previews/front.png',after)
        self.assertNotIn('buildings/a/previews/front.png',after)
    def test_other_overviews_are_not_silently_migrated(self):
        text=TABLE([CARD('a')+' '+CARD('a'),CARD('b'),''])
        with patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',set()):
            self.assertEqual(g.normalize_overview_representatives(text,PAGE,[R1,R2]),text)
    def test_individual_model_gallery_is_always_excluded(self):
        page=R1+'/README.md';text='| front | rear | top |\n|---|---|---|\n| ![front](previews/front.png) | ![rear](previews/rear.png) | ![top](previews/top.png) |\n'
        self.assertEqual(self.normalize(text,page,[R1]),text)
    def test_scoped_audit_rejects_duplicate_preview_not_duplicate_links(self):
        text=TABLE([CARD('a')+' '+CARD('a')+' [download](buildings/a/README.md)',CARD('b'),''])
        fs={r+'/previews/front.png' for r in [R1,R2]}|{r+'/README.md' for r in [R1,R2]}
        with patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',{PAGE}),patch.object(g,'FILES',fs),patch.object(g,'read',return_value=text):
            result=g.audit(PAGE,[R1,R2]);self.assertIn('overview_not_one_image_per_building',result['errors'])
        with patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',{PAGE}),patch.object(g,'FILES',fs),patch.object(g,'read',return_value=self.normalize(text)):
            self.assertEqual(g.audit(PAGE,[R1,R2])['errors'],[])
    def test_formatted_label_is_counted_read_only_without_rewrite(self):
        text=TABLE(['![front **label**](buildings/a/previews/front.png)',CARD('b'),''])
        self.assertEqual(self.normalize(text),text)
        fs={r+'/previews/front.png' for r in [R1,R2]}|{r+'/README.md' for r in [R1,R2]}
        with patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',{PAGE}),patch.object(g,'FILES',fs),patch.object(g,'read',return_value=text):
            self.assertEqual(g.audit(PAGE,[R1,R2])['errors'],[])
    def test_sync_repairs_scoped_overview_and_is_idempotent(self):
        text=TABLE([CARD('a')+' '+CARD('a'),CARD('b'),''])+'\n## QA\n[Evidence](buildings/a/README.md)\n'
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);p=root/PAGE;p.parent.mkdir(parents=True);p.write_text(text)
            fs={r+'/previews/front.png' for r in [R1,R2]}|{r+'/README.md' for r in [R1,R2]}
            with patch.object(g,'ROOT',root),patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',{PAGE}),patch.object(g,'FILES',fs),patch.object(g,'read',side_effect=lambda page:(root/page).read_text()):
                self.assertTrue(g.sync(PAGE,[R1,R2]));self.assertFalse(g.sync(PAGE,[R1,R2]))
            self.assertIn('## QA\n[Evidence](buildings/a/README.md)',p.read_text())
            groups=g.overview_preview_groups(p.read_text(),PAGE,[R1,R2]);self.assertEqual([len(x) for x in groups.values()],[1,1])
    def test_new_card_has_exactly_one_preview(self):
        fs={R1+'/README.md',R1+'/previews/front.png',R1+'/previews/rear.png'}
        with patch.object(g,'FILES',fs),patch.object(g,'read',return_value='# Example\n'):
            self.assertEqual(len(g.preview_images(g.new_card(R1,PAGE))),1)

class VisibleOverviewPolicyTests(unittest.TestCase):
    def audit_text(self,text,extra_files=()):
        fs={r+'/previews/front.png' for r in [R1,R2]}|{r+'/README.md' for r in [R1,R2]}|set(extra_files)
        with patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',{PAGE}),patch.object(g,'FILES',fs),patch.object(g,'read',return_value=text):
            return g.audit(PAGE,[R1,R2])
    def test_all_canonical_school_campus_pages_are_enabled(self):
        chosen=[p for p in g.pages() if g.single_image_overview(p)]
        self.assertEqual(len(chosen),259)
        self.assertTrue(all(p.split('/')[0] in g.SCHOOLS for p in chosen))
    def test_homepage_model_and_other_catalogs_never_enabled(self):
        for page in ['README.md',R1+'/README.md',*g.OTHER_ROOTS]:
            with self.subTest(page=page),patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',{page}):
                self.assertFalse(g.single_image_overview(page))
    def test_current_appearance_footer_duplicate_is_rejected(self):
        text=TABLE([CARD('a'),CARD('b'),''])+'\n## 現行配色\n![彩色](buildings/a/appearance/previews/front.png)\n'
        result=self.audit_text(text,[R1+'/appearance/previews/front.png'])
        self.assertIn('overview_not_one_image_per_building',result['errors'])
        self.assertEqual(result['overview_image_counts'][R1],2)
    def test_footer_download_and_model_links_do_not_count_as_images(self):
        text=TABLE([CARD('a'),CARD('b'),''])+'\n[配色](buildings/a/appearance/README.md) [下載](buildings/a/model.stl)\n'
        self.assertEqual(self.audit_text(text)['errors'],[])
    def test_collapsed_supporting_multiviews_are_preserved_and_excluded(self):
        detail='<details>\n<summary>限定模型細節</summary>\n'+CARD('a')+CARD('a')+'\n</details>\n'
        text=TABLE([CARD('a'),CARD('b'),''])+detail
        self.assertEqual(self.audit_text(text)['errors'],[])
        self.assertIn(detail,text)
    def test_quoted_open_word_is_not_boolean_attribute(self):
        text=TABLE([CARD('a'),CARD('b'),''])+'<details title="open instructions">'+CARD('a')+'</details>'
        self.assertEqual(self.audit_text(text)['errors'],[])
    def test_visible_summary_images_cannot_hide_in_collapsed_details(self):
        for summary in ['<summary>'+CARD('a')+'</summary>', '<summary>![A](buildings/a/previews/front.png)</summary>', '<summary>'+CARD('a')]:
            text=TABLE([CARD('a'),CARD('b'),''])+'<details>'+summary+'supporting text</details>'
            self.assertIn('unparsed_overview_images',self.audit_text(text)['errors'])
    def test_open_details_are_visible_and_counted(self):
        for opening in ['<details open>','<details open="open">']:
            text=TABLE([CARD('a'),CARD('b'),''])+opening+CARD('a')+'</details>'
            self.assertIn('overview_not_one_image_per_building',self.audit_text(text)['errors'])
    def test_nested_collapsed_details_are_masked_without_offset_loss(self):
        text='before<details>'+CARD('a')+'<details open>'+CARD('a')+'</details></details>after'
        masked=g.visible_overview_text(text)
        self.assertEqual(len(masked),len(text));self.assertTrue(masked.startswith('before'));self.assertTrue(masked.endswith('after'))
        self.assertNotIn('<img',masked)
    def test_unbalanced_detail_boundaries_fail_closed(self):
        for detail in ['<details>'+CARD('a'),'</details>', '<details>'+CARD('a')+'</details></details>']:
            self.assertIn('unparsed_overview_images',self.audit_text(TABLE([CARD('a'),CARD('b'),''])+detail)['errors'])
    def test_angle_bracket_destination_and_formatted_label_count(self):
        text=TABLE(['![A **label**](<buildings/a/previews/front.png>)',CARD('b'),''])
        self.assertEqual(self.audit_text(text)['errors'],[])
    def test_unknown_reference_style_images_fail_closed(self):
        text=TABLE([CARD('a'),CARD('b'),''])+'\n![extra][preview]\n[preview]: buildings/a/previews/front.png\n'
        self.assertIn('unparsed_overview_images',self.audit_text(text)['errors'])
    def test_broken_footer_image_is_rejected(self):
        text=TABLE([CARD('a'),CARD('b'),''])+'\n![extra](buildings/a/previews/missing.png)\n'
        self.assertIn('broken_overview_image',self.audit_text(text)['errors'])
    def test_sync_never_silently_removes_supporting_or_footer_sections(self):
        footer='\n## 現行配色\n'+CARD('a')+'\n<details>'+CARD('a')+'</details>\n'
        text=TABLE([CARD('a'),CARD('b'),''])+footer
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp);p=root/PAGE;p.parent.mkdir(parents=True);p.write_text(text)
            fs={r+'/previews/front.png' for r in [R1,R2]}|{r+'/README.md' for r in [R1,R2]}
            with patch.object(g,'ROOT',root),patch.object(g,'SINGLE_IMAGE_OVERVIEW_PAGES',{PAGE}),patch.object(g,'FILES',fs),patch.object(g,'read',side_effect=lambda page:(root/page).read_text()):
                self.assertFalse(g.sync(PAGE,[R1,R2]));self.assertEqual(p.read_text(),text)
                self.assertIn('overview_not_one_image_per_building',g.audit(PAGE,[R1,R2])['errors'])

if __name__=='__main__':unittest.main()
