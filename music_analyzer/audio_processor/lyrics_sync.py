from pydub import AudioSegment
import speech_recognition as sr
from typing import List, Tuple

class LyricsSync:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    def extract_lyrics(self, audio_path: str) -> List[Tuple[str, float]]:
        """
        从音频中提取歌词
        :param audio_path: 音频文件路径
        :return: 识别出的歌词列表，每个元素包含歌词和时间戳
        """
        try:
            # 加载音频文件
            audio = AudioSegment.from_file(audio_path)
            # 转换为wav格式
            audio = audio.set_frame_rate(16000).set_channels(1)
            # 使用语音识别
            with sr.AudioFile(audio.export(format='wav')) as source:
                audio_data = self.recognizer.record(source)
                result = self.recognizer.recognize_google(audio_data, language='zh-CN', show_all=True)
                if result:
                    return result['alternative'][0]['words']
                return []
        except Exception as e:
            print(f"歌词识别失败: {str(e)}")
            return []
            
    def sync_lyrics(self, score: str, lyrics: str, bpm: int = 60, time_signature: str = '4/4') -> List[Tuple[str, str, float]]:
        """
        同步歌词和简谱
        :param score: 简谱字符串
        :param lyrics: 歌词字符串，用空格分隔
        :param bpm: 每分钟节拍数
        :param time_signature: 节拍，如 '4/4'
        :return: 同步结果 [(音符, 歌词, 时间)]
        """
        # 解析简谱
        notes = self._parse_score(score)
        
        # 将歌词字符串转换为列表
        lyrics_list = lyrics.split()
        lyric_index = 0
        current_word_duration = 0.0
        
        # 计算每拍时间（秒）
        beat_duration = 60.0 / bpm  # 每拍时间 = 60秒 / BPM
        
        # 解析节拍
        beats_per_measure = int(time_signature.split('/')[0])
        measure_duration = beats_per_measure * beat_duration  # 每小节时间
        
        synced_lyrics = []
        
        for note, duration, start_time in notes:
            # 计算音符的时间戳
            note_timestamp = start_time * beat_duration
            
            # 处理留白部分
            if note == '0':  # 休止符
                synced_lyrics.append(('0', '', note_timestamp))
                continue
                
            if lyric_index < len(lyrics_list):
                word = lyrics_list[lyric_index]
                synced_lyrics.append((note, word, note_timestamp))
                
                # 累加当前歌词的时长
                current_word_duration += duration * beat_duration
                
                # 根据节拍判断是否切换到下一个歌词
                if current_word_duration >= measure_duration * 0.75:  # 75%的小节长度
                    lyric_index += 1
                    current_word_duration = 0.0
            else:
                synced_lyrics.append((note, '', note_timestamp))
                
        return synced_lyrics
        
    def _parse_score(self, score: str) -> List[Tuple[str, float, float]]:
        """
        解析简谱字符串
        :param score: 简谱字符串
        :return: 音符列表 [(音符, 时长, 开始时间)]
        """
        notes = []
        current_time = 0.0
        
        # 按空格分割音符
        for note_str in score.split():
            # 跳过小节线
            if note_str == '|':
                continue
                
            # 解析音符
            base_note = ''
            octave = 0
            duration = 1.0  # 默认时值
            
            # 解析高低音符号
            if '↑' in note_str:
                octave = note_str.count('↑')
                base_note = note_str.replace('↑', '')
            elif '↓' in note_str:
                octave = -note_str.count('↓')
                base_note = note_str.replace('↓', '')
            else:
                base_note = note_str
                
            # 解析时值符号
            if '—' in base_note:
                duration = 2.0
                base_note = base_note.replace('—', '')
            elif '-' in base_note:
                duration = 1.5
                base_note = base_note.replace('-', '')
            elif len(base_note) > 1:  # 处理连在一起的音符
                duration = 1.0 / len(base_note)
                base_note = base_note  # 保持原样
                
            notes.append((note_str, duration, current_time))
            current_time += duration
            
        return notes

    def generate_score_with_lyrics(self, score: str, lyrics: str, bpm: int = 60, time_signature: str = '4/4') -> str:
        """
        生成带歌词的简谱
        :param score: 简谱字符串
        :param lyrics: 歌词字符串
        :param bpm: 每分钟节拍数
        :param time_signature: 节拍
        :return: 带歌词的简谱字符串
        """
        synced_lyrics = self.sync_lyrics(score, lyrics, bpm, time_signature)
        
        # 初始化简谱和歌词行
        score_lines = []
        lyric_lines = []
        
        current_measure = []
        current_lyric = []
        current_time = 0.0
        
        for note, word, timestamp in synced_lyrics:
            # 每八拍换行
            if timestamp >= current_time + 8.0 * (60.0 / bpm):  # 八拍时间 = 8 * 每拍时间
                score_lines.append(' '.join(current_measure))
                lyric_lines.append(' '.join(current_lyric))
                current_measure = []
                current_lyric = []
                current_time = timestamp
                
            # 处理不同时值的音符
            if len(note) > 1 and not any(c in note for c in ['↑', '↓', '—', '-']):  # 连在一起的音符
                current_measure.append(f"({note})")  # 用括号表示连在一起的音符
            else:
                current_measure.append(note)
            current_lyric.append(word if word else '·')  # 用·表示无歌词部分
        
        # 添加最后一行的简谱和歌词
        if current_measure:
            score_lines.append(' '.join(current_measure))
            lyric_lines.append(' '.join(current_lyric))
        
        # 合并简谱和歌词
        result = []
        for score_line, lyric_line in zip(score_lines, lyric_lines):
            result.append(score_line)
            result.append(lyric_line)
            result.append('')  # 空行分隔
        
        return '\n'.join(result)