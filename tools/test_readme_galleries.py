import unittest
from validate_readme_galleries import inspect
class GalleryChecks(unittest.TestCase):
 def setUp(self):
  self.path='學校/校區/buildings/model/README.md';self.known={self.path,'學校/校區/buildings/model/previews/front.png'};self.good='# 模型\n\n## 模型預覽\n\n| 正面 | 背面 | 俯視 |\n| --- | --- | --- |\n| ![圖](previews/front.png) | | |\n\n## 限制\n未試印。\n'
 def test_valid(self):self.assertEqual(inspect(self.path,self.good,self.known),[])
 def test_missing_image_even_without_links(self):self.assertTrue(inspect(self.path,'# 模型\n\n## 範圍\n文字',self.known))
 def test_wrong_order(self):self.assertTrue(inspect(self.path,self.good.replace('## 模型預覽','## 範圍\n文字\n\n## 模型預覽'),self.known))
 def test_missing_file(self):self.assertTrue(inspect(self.path,self.good.replace('front.png','absent.png'),self.known))
 def test_invalid_separator(self):self.assertTrue(inspect(self.path,self.good.replace('| --- | --- | --- |','| --- | --- | |'),self.known))
 def test_title_preserved(self):self.assertTrue(inspect(self.path,self.good.replace('# 模型\n',''),self.known))
if __name__=='__main__':unittest.main()
