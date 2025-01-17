import librosa
import numpy as np

class ScoreGenerator:
    def __init__(self):
        self.note_map = {
            0: '1', 1: '2', 2: '3', 
            3: '4', 4: '5', 5: '6', 
            6: '7'
        }
        
    def _quantize_pitch(self, pitch: float) -> str:
        """将音高量化为简谱音符"""
        # 将音高映射到0-6的范围
        note_index = round(pitch) % 7
        # 判断高低音
        octave = pitch // 7
        note = self.note_map[note_index]
        # 添加高低音标记
        if octave > 0:
            note = note + ('.' * int(octave))
        elif octave < 0:
            note = note + ('_' * abs(int(octave)))
        return note
        
    def _quantize_duration(self, duration: float) -> str:
        """将时长量化为简谱时值"""
        if duration >= 1.0:
            return '-'
        elif duration >= 0.5:
            return '_'
        else:
            return ''
            
    def generate_score(self, features: dict) -> str:
        """
        生成简谱
        :param features: 包含音高序列和节奏信息的字典
        :return: 简谱字符串
        """
        pitches = features['pitches']  # 音高序列
        beats = features['beats']      # 节拍点
        
        # 生成调号和节拍
        score = f"1=C {features['time_signature']}\n\n"
        
        # 按小节生成简谱
        current_measure = []
        for i in range(len(pitches)):
            note = self._quantize_pitch(pitches[i])
            duration = self._quantize_duration(beats[i])
            current_measure.append(f"{note}{duration}")
            
            # 每4个音符换行
            if (i + 1) % 4 == 0:
                score += ' '.join(current_measure) + ' |\n'
                current_measure = []
                
        return score