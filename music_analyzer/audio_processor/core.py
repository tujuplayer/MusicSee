import numpy as np
import librosa

class AudioProcessor:
    def __init__(self):
        self.sample_rate = 22050  # 默认采样率

    def load_audio(self, file_path: str) -> np.ndarray:
        """
        加载音频文件
        :param file_path: 音频文件路径
        :return: 音频数据 (numpy数组)
        """
        try:
            audio, _ = librosa.load(file_path, sr=self.sample_rate)
            return audio
        except Exception as e:
            print(f"加载音频失败: {str(e)}")
            return None

    def extract_features(self, audio: np.ndarray) -> dict:
        """
        提取音频特征
        :param audio: 音频数据
        :return: 包含音高、节奏等特征的字典
        """
        features = {}
        try:
            # 提取音高
            pitches, magnitudes = librosa.core.piptrack(y=audio, sr=self.sample_rate)
            features['pitch'] = pitches
            
            # 提取节奏
            tempo, _ = librosa.beat.beat_track(y=audio, sr=self.sample_rate)
            features['tempo'] = tempo
            
            return features
        except Exception as e:
            print(f"特征提取失败: {str(e)}")
            return None