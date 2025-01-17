import unittest
import os
import sys

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from music_analyzer.audio_processor.lyrics_sync import LyricsSync

class TestLyricsSync(unittest.TestCase):
    def setUp(self):
        self.sync = LyricsSync()
        
    def print_sync_result(self, score: str, lyrics: str, result: list):
        """
        打印同步结果
        :param score: 简谱字符串
        :param lyrics: 原始歌词
        :param result: 同步结果 [(音符, 歌词, 时间)]
        """
        print("\n简谱：")
        print(score)
        print("\n歌词：")
        print(lyrics)
        print("\n同步结果：")
        
        # 按时间顺序打印
        current_word = None
        for note, word, _ in result:
            if word != current_word:
                if current_word is not None:
                    print()  # 换行显示新词
                current_word = word
                print(f"{word}: ", end="")
            print(f"{note} ", end="")
        print("\n" + "=" * 40)
        
    def test_sync_lyrics_basic(self):
        """测试基本歌词同步功能"""
        score = "1 2 3 4 | 5 6 7 1"
        lyrics = "这 是 一 首 简 单 的 歌"
        
        expected_output = [
            ('1', '这', 0.0),
            ('2', '是', 1.0),
            ('3', '一', 2.0),
            ('4', '首', 3.0),
            ('5', '简', 4.0),
            ('6', '单', 5.0),
            ('7', '的', 6.0),
            ('1', '歌', 7.0)
        ]
        
        result = self.sync.sync_lyrics(score, lyrics)
        self.print_sync_result(score, lyrics, result)
        self.assertEqual(result, expected_output)
        
    def test_sync_lyrics_multi_notes(self):
        """测试一个字对应多个音符的情况"""
        score = "1 1 2 2 | 3 3 4 4"
        lyrics = "美 丽 的 夜"
        
        expected_output = [
            ('1', '美', 0.0),
            ('1', '美', 1.0),
            ('2', '丽', 2.0),
            ('2', '丽', 3.0),
            ('3', '的', 4.0),
            ('3', '的', 5.0),
            ('4', '夜', 6.0),
            ('4', '夜', 7.0)
        ]
        
        result = self.sync.sync_lyrics(score, lyrics)
        self.print_sync_result(score, lyrics, result)
        self.assertEqual(result, expected_output)
        
    def test_sync_lyrics_complex(self):
        """测试复杂情况"""
        score = "1 2 3 4 | 5— 6 7 1"
        lyrics = "我 爱 你 中 国"
        
        expected_output = [
            ('1', '我', 0.0),
            ('2', '爱', 1.0),
            ('3', '你', 2.0),
            ('4', '中', 3.0),
            ('5—', '国', 4.0),
            ('6', '国', 6.0),
            ('7', '国', 7.0),
            ('1', '国', 8.0)
        ]
        
        result = self.sync.sync_lyrics(score, lyrics)
        self.print_sync_result(score, lyrics, result)
        self.assertEqual(result, expected_output)

if __name__ == '__main__':
    unittest.main()