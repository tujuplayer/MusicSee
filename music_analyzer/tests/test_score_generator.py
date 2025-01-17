import unittest
import numpy as np
import sys
sys.path.append('c:\\Users\\TUJU\\Desktop\\MusicApp\\MusicSee\\music_analyzer')
from audio_processor.score_generator import ScoreGenerator

class TestScoreGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = ScoreGenerator()
        
    def test_quantize_pitch(self):
        """测试音高量化"""
        # 测试基本音
        self.assertEqual(self.generator._quantize_pitch(0), '1')
        self.assertEqual(self.generator._quantize_pitch(1), '2')
        self.assertEqual(self.generator._quantize_pitch(6), '7')
        
        # 测试高音
        self.assertEqual(self.generator._quantize_pitch(7), '1↑')
        self.assertEqual(self.generator._quantize_pitch(14), '1↑↑')
        
        # 测试低音
        self.assertEqual(self.generator._quantize_pitch(-1), '7↓')
        self.assertEqual(self.generator._quantize_pitch(-7), '7↓↓')
        
    def test_quantize_duration(self):
        """测试时值量化"""
        # 测试长音
        self.assertEqual(self.generator._quantize_duration(1.2), '—')
        self.assertEqual(self.generator._quantize_duration(2.0), '—')
        
        # 测试中长音
        self.assertEqual(self.generator._quantize_duration(0.6), '-')
        self.assertEqual(self.generator._quantize_duration(0.8), '-')
        
        # 测试短音
        self.assertEqual(self.generator._quantize_duration(0.3), '')
        self.assertEqual(self.generator._quantize_duration(0.4), '')
        
    def test_generate_score(self):
        """测试简谱生成"""
        features = {
            'pitches': [0, 1, 2, 3, 4, 5, 6, 7, -1],
            'beats': [1.0, 0.5, 0.25, 1.0, 0.5, 0.25, 1.0, 0.5, 1.0],
            'times': [0.0, 1.0, 1.5, 1.75, 2.75, 3.25, 3.5, 4.5, 5.0],
            'time_signature': '4/4'
        }
        
        expected_score = """1=C 4/4

1— 2- 3  4— | 5- 6  7  1↑ | 7↓— 
"""
        expected_notes = [
            ('1', 1.0, 0.0),
            ('2', 0.5, 1.0),
            ('3', 0.25, 1.5),
            ('4', 1.0, 1.75),
            ('5', 0.5, 2.75),
            ('6', 0.25, 3.25),
            ('7', 1.0, 3.5),
            ('1↑', 0.5, 4.5),
            ('7↓', 1.0, 5.0)
        ]
        
        score, notes = self.generator.generate_score(features)
        self.assertEqual(score, expected_score)
        self.assertEqual(notes, expected_notes)

if __name__ == '__main__':
    unittest.main()