from threading import Thread
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
from kivy.properties import ObjectProperty, NumericProperty
from kivy.clock import Clock
import os
import librosa
import librosa.display
import matplotlib.pyplot as plt
import io
from kivy.core.image import Image as CoreImage
from matplotlib.backends.backend_agg import FigureCanvasAgg
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.behaviors import DragBehavior
from kivy.uix.slider import Slider
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.core.audio import SoundLoader



# 添加字体支持
resource_add_path(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts'))
LabelBase.register(
    name='ChineseFont', 
    fn_regular  =    'SourceHanSansCN-Regular.otf', 
    fn_bold     =    'SourceHanSansCN-Regular.otf'
)

class DragDropLabel(Label):
    """
    支持拖拽文件的Label控件
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = '拖拽音乐文件到这里'
        self.font_name = 'ChineseFont'
        self.font_size = 20
        self.color = (0.5, 0.5, 0.5, 1)
        self.halign = 'center'
        self.valign = 'middle'
        
        # 绑定Window的拖拽事件
        Window.bind(on_drop_file=self._on_drop_file)

    def _on_drop_file(self, window, filepath, x, y):
        """
        拖拽文件完成后的回调
        """
        try:
            self.handle_dropped_file(filepath)
        except ValueError as ve:
            self.show_error_message(str(ve))
        except FileNotFoundError as fnfe:
            self.show_error_message(f"文件未找到: {str(fnfe)}")
        except Exception as e:
            self.show_error_message(f"拖拽文件失败: {str(e)}")
    
    def handle_dropped_file(self, filepath):
        """
        处理拖放的文件
        """
        # 确保文件路径是字符串
        if isinstance(filepath, bytes):
            filepath = filepath.decode('utf-8')

        # 检查文件格式
        supported_formats = ('.mp3', '.wav', '.flac', '.ogg')
        if not filepath.lower().endswith((supported_formats)):
            raise ValueError(f'仅支持 {", ".join(supported_formats)} 文件！')

        # 检查文件是否存在
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")

        # 调用父窗口的load_file方法
        parent_window = self.get_parent_window()
        if parent_window and hasattr(parent_window, 'load_file'):
            parent_window.load_file(filepath)
        else:
            raise RuntimeError("无法访问 MainWindow 的 load_file 方法")

    def show_error_message(self, message):
        popup = Popup(
           title='错误',
           content=Label(
               text=message,
               font_name='ChineseFont',
               font_size=14
           ),
           size_hint=(0.8, 0.4)
       )
        popup.open()

    def get_parent_window(self):
        """
        安全地获取父窗口
        """
        parent = self.parent
        while parent is not None:
            if hasattr(parent, 'load_file'):
                return parent
            parent = parent.parent
        return None
    
class FancyButton(Button):
    """自定义带动画效果的按钮"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''  # 禁用默认背景
        self.background_color = (0.2, 0.6, 1, 1)  # 默认蓝色
        self.bind(on_press=self.on_press_animation, on_release=self.on_release_animation)
        self.original_size = self.size  # 保存原始大小

    def on_press_animation(self, instance):
        """点击时的动画效果"""
        anim = Animation(background_color=(0.1, 0.5, 0.9, 1), duration=0.1) + Animation(background_color=(0.2, 0.6, 1, 1), duration=0.1)
        anim.start(instance)

    def on_release_animation(self, instance):
        """释放时的动画效果"""
        anim = Animation(size=(self.original_size[0] * 1.1, self.original_size[1] * 1.1), duration=0.1) + Animation(size=self.original_size, duration=0.1)
        anim.start(instance)

    def on_touch_down(self, touch):
        """鼠标悬停时的放大效果"""
        if self.collide_point(*touch.pos):
            anim = Animation(size=(self.original_size[0] * 1.05, self.original_size[1] * 1.05), duration=0.1)
            anim.start(self)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        """鼠标离开时的恢复效果"""
        if self.collide_point(*touch.pos):
            anim = Animation(size=self.original_size, duration=0.1)
            anim.start(self)
        return super().on_touch_up(touch)

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):

        """
        初始化主窗口
        """
        super().__init__(**kwargs)

        self.is_dragging = False
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = [10, 10, 10, 10]

        # 设置默认字体
        self.default_font = 'ChineseFont'

        # 初始化窗口大小和标题
        Window.size = (1200, 800)
        Window.title = '音乐分析程序'
        
        # 顶部工具栏
        self.add_widget(self.create_toolbar())
   
        
        # 主内容区域
        self.main_content = BoxLayout(
            orientation='horizontal',
            spacing=20,
            size_hint=(1, 0.8)
        )

        # 左侧文件信息区
        self.left_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.4, 1),
            spacing=10
        )
        self.left_panel.add_widget(self.create_file_info_panel())
        self.left_panel.add_widget(self.create_waveform_panel())
        self.main_content.add_widget(self.left_panel)

        # 右侧分析结果区
        self.right_panel = BoxLayout(
            orientation='vertical',
            size_hint=(0.6, 1),
            spacing=10
        )
        self.right_panel.add_widget(self.create_analysis_panel())
        self.right_panel.add_widget(self.create_player_controls())
        self.main_content.add_widget(self.right_panel)

        self.add_widget(self.main_content)

        # 添加底部状态栏
        self.add_widget(self.create_status_bar())
        
           # 初始化播放器
        self.sound = None
        self.is_playing = False
        self.playback_position = 0

                # 添加拖拽文件提示
        self.drag_drop_label = DragDropLabel(size_hint=(1, 0.2))
        self.add_widget(self.drag_drop_label)

        # 初始化文件标签
        self.file_label = Label(
            text='未选择文件',
            size_hint=(1, 0.1),
            font_name=self.default_font,
            font_size=16,
            color=(0.5, 0.5, 0.5, 1)  # 灰色字体
        )
        self.add_widget(self.file_label)

        

        # 初始化进度条
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(1, 0.05)
        )
        self.add_widget(self.progress_bar)  # 只添加一次

    def create_toolbar(self):
        """
        创建顶部工具栏
        """
        toolbar = BoxLayout(
            size_hint=(1, 0.05),
            spacing=10
        )

        # 上传音乐按钮
        upload_btn = Button(
            text='上传音乐',
            font_name='ChineseFont',
            font_size=14
        )
        upload_btn.bind(on_press=self.show_file_chooser)
        toolbar.add_widget(upload_btn)

        # 导入音乐按钮
        import_btn = Button(
            text='导入音乐',
            font_name='ChineseFont',
            font_size=14
        )
        import_btn.bind(on_press=self.show_link_input)
        toolbar.add_widget(import_btn)

        # 设置按钮
        settings_btn = Button(
            text='设置',
            font_name='ChineseFont',
            font_size=14
        )
        settings_btn.bind(on_press=self.show_settings_panel)
        toolbar.add_widget(settings_btn)

        # 关于按钮
        about_btn = Button(
            text='关于',
            font_name='ChineseFont',
            font_size=14
        )
        about_btn.bind(on_press=self.show_about_panel)
        toolbar.add_widget(about_btn)

        return toolbar
    def create_waveform_panel(self):
        """
        创建波形图显示面板
        """
        waveform_panel = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.5),
            spacing=10,
            padding=[10, 10, 10, 10]
        )

        # 波形图标题
        waveform_title = Label(
            text='波形图',
            font_name='ChineseFont',
            font_size=16,
            size_hint=(1, 0.1),
            color=(0.2, 0.2, 0.2, 1)
        )
        waveform_panel.add_widget(waveform_title)

        # 波形图显示区域
        self.waveform_image = Image(
            source='',  # 初始为空
            size_hint=(1, 0.8),
            allow_stretch=True
        )
        waveform_panel.add_widget(self.waveform_image)

        # 刷新按钮
        refresh_btn = Button(
            text='刷新波形图',
            font_name='ChineseFont',
            font_size=14,
            size_hint=(1, 0.1)
        )
        refresh_btn.bind(on_press=self.refresh_waveform)
        waveform_panel.add_widget(refresh_btn)

        return waveform_panel
    
    def refresh_waveform(self, instance):
        """
        刷新波形图
        """
        if hasattr(self, 'selected_file') and self.selected_file:
            self.update_waveform(self.selected_file)
        else:
            self.show_error_message('请先选择音乐文件！')

    def create_file_info_panel(self):
        """
        创建文件信息面板
        """
        file_info_panel = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.2),
            spacing=10
        )

        # 文件标签
        self.file_label = Label(
            text='未选择文件',
            font_name='ChineseFont',
            font_size=16,
            color=(0.2, 0.2, 0.2, 1),
            size_hint=(1, 0.5),
            halign='left',
            valign='middle'
        )
        file_info_panel.add_widget(self.file_label)

        # 文件信息
        self.file_info_label = Label(
            text='文件大小: 0 MB\n时长: 0:00',
            font_name='ChineseFont',
            font_size=14,
            color=(0.4, 0.4, 0.4, 1),
            size_hint=(1, 0.5),
            halign='left',
            valign='middle'
        )
        file_info_panel.add_widget(self.file_info_label)

        return file_info_panel




    def create_player_controls(self):
        """
        创建播放器控件
        """
        player_panel = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.3),
            spacing=10
        )

        # 播放/暂停按钮
        self.play_button = ToggleButton(
            text='播放',
            font_name='ChineseFont',
            font_size=16,
            size_hint=(1, 0.2)
        )
        self.play_button.bind(on_press=self.toggle_play)
        player_panel.add_widget(self.play_button)

        # 进度条
        progress_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.progress_label = Label(
            text='00:00 / 00:00',
            font_name='ChineseFont',
            font_size=14,
            size_hint=(0.2, 1)
        )
        self.progress_slider = Slider(
            min=0,
            max=100,
            value=0,
            size_hint=(0.8, 1)
        )
        self.progress_slider.bind(value=self.on_progress_change)
        progress_layout.add_widget(self.progress_label)
        progress_layout.add_widget(self.progress_slider)
        player_panel.add_widget(progress_layout)

        # 音量控制
        volume_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        self.volume_label = Label(
            text='音量: 50%',
            font_name='ChineseFont',
            font_size=14,
            size_hint=(0.2, 1)
        )
        self.volume_slider = Slider(
            min=0,
            max=1,
            value=0.5,
            size_hint=(0.8, 1)
        )
        self.volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(self.volume_label)
        volume_layout.add_widget(self.volume_slider)
        player_panel.add_widget(volume_layout)

        return player_panel

    def create_status_bar(self):
        """
        创建底部状态栏
        """
        status_bar = BoxLayout(
            size_hint=(1, 0.05),
            spacing=10
        )

        # 状态标签
        self.status_label = Label(
            text='就绪',
            font_name='ChineseFont',
            font_size=14,
            color=(0.4, 0.4, 0.4, 1),
            size_hint=(0.8, 1),
            halign='left',
            valign='middle'
        )
        status_bar.add_widget(self.status_label)

        # 进度条
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint=(0.2, 1)
        )
        status_bar.add_widget(self.progress_bar)

        return status_bar

    def toggle_play(self, instance):
        """
        切换播放/暂停状态
        """
        if not hasattr(self, 'sound') or not self.sound:
            self.show_error_message('请先加载音频文件！')
            return

        if self.is_playing:
            self.sound.stop()
            self.play_button.text = '播放'
            self.is_playing = False
            Clock.unschedule(self.update_progress)
        else:
            self.sound.play()
            self.play_button.text = '暂停'
            self.is_playing = True
            Clock.schedule_interval(self.update_progress, 0.1)

    def update_progress(self, dt):
        """
        更新播放进度
        """
        if not hasattr(self, 'sound') or not self.sound:
                return

        if self.sound.state == 'play':
            current_time = self.sound.get_pos()
            total_time = self.sound.length
            
            # 防止除零错误
            if total_time > 0:
                progress = (current_time / total_time) * 100
                self.progress_slider.value = progress
                
                # 更新时间显示
                current_min = int(current_time // 60)
                current_sec = int(current_time % 60)
                total_min = int(total_time // 60)
                total_sec = int(total_time % 60)
                self.progress_label.text = f'{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}'

    def on_progress_change(self, instance, value):
        """
        拖动进度条时跳转到指定位置
        """
        if self.sound and self.total_duration > 0:
            try:
                # 防止递归调用
                if not self.is_dragging:
                    return
                    
                target_time = (value / 100) * self.total_duration

                # 暂停进度更新
                Clock.unschedule(self.update_progress)

                # 跳转到指定位置        
                self.sound.seek(target_time)
                
                # 立即更新显示
                current_min = int(target_time // 60)
                current_sec = int(target_time % 60)
                total_min = int(self.total_duration // 60)
                total_sec = int(self.total_duration % 60)
                self.progress_label.text = f'{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}'
                # 恢复进度更新
                Clock.schedule_interval(self.update_progress, 0.1)
            except Exception as e:
                self.show_error_message(f'跳转失败: {str(e)}')

    def on_volume_change(self, instance, value):
        """
        调整音量
        """
        if hasattr(self, 'sound') and self.sound:
            try:
                self.sound.volume = value
                self.volume_label.text = f'音量: {int(value * 100)}%'
            except Exception as e:
                self.show_error_message(f'音量调整失败: {str(e)}')

    def load_file(self, filepath):
        """
        加载音频文件并初始化播放器
        """
        try:
            
            # 停止当前播放的音乐
            if self.sound and self.sound.state == 'play':
                self.sound.stop()
                self.is_playing = False
                self.play_button.text = '播放'
                Clock.unschedule(self.update_progress)  # 停止进度更新

            # 加载音频文件
            self.sound = SoundLoader.load(filepath)
            if not self.sound:
                raise ValueError('无法加载音频文件！')
            
            # 绑定进度条事件
            self.progress_slider.bind(value=self.on_progress_change)
        

            # 更新文件标签
            self.file_label.text = f'已选择文件: {os.path.basename(filepath)}'
            
            # 保存文件路径
            self.selected_file = filepath

            # 获取文件大小
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # 转换为MB
            file_size_str = f'{file_size:.2f} MB'
            
            # 获取音频时长
            y, sr = librosa.load(filepath, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            self.total_duration = duration  # 保存总时长
            minutes = int(duration // 60)
            seconds = int(duration % 60)
            duration_str = f'{minutes}:{seconds:02d}'
            
            # 更新文件信息
            self.file_info_label.text = f'文件大小: {file_size_str}\n时长: {duration_str}'
            
            # 初始化播放器设置
            self.sound.volume = self.volume_slider.value
            self.progress_slider.max = 100
            self.progress_slider.value = 0
            self.play_button.text = '播放'
            self.is_playing = False
            
            # 初始化进度条
            self.progress_label.text = '00:00 / ' + duration_str
            
            # 显示成功提示
            self.show_success_message('文件加载成功！')
            
            # 更新波形图
            self.update_waveform(filepath)
            
            # 启动进度更新
            Clock.schedule_interval(self.update_progress, 0.1)
            
        except Exception as e:
            self.show_error_message(f'加载失败: {str(e)}')
            self.sound = None

    def _load_file_thread(self, filepath):
        """
        在后台线程中加载文件
        """
        # 使用Clock逐步更新进度条
        Clock.schedule_interval(self.update_progress, 0.1)
        
        # 加载音频文件
        y, sr = librosa.load(filepath, sr=None)
        
        # 在主线程中更新UI
        Clock.schedule_once(lambda dt: self._update_waveform(y, sr))

    def show_success_message(self, message):
        """
        显示成功提示
        """
        popup = Popup(
            title='成功',
            content=Label(
                text=message,
                font_name='ChineseFont',
                font_size=14
            ),
            size_hint=(0.8, 0.4)
        )
        popup.open()

    def show_error_message(self, message):
        """
        显示错误提示
        """
        popup = Popup(
            title='错误',
            content=Label(
                text=message,
                font_name='ChineseFont',
                font_size=14
            ),
            size_hint=(0.8, 0.4)
        )
        popup.open()

        # 将进度条添加到界面
        self.progress_bar = ProgressBar(
        max=100,
        value=0,
        size_hint=(1, 0.05)
        )
        self.add_widget(self.progress_bar)  
        
            # 禁用右键菜单
        from kivy.config import Config
        Config.set('input', 'mouse', 'mouse,disable_multitouch')

    def show_settings_panel(self, instance):
        """
        显示设置面板
        """
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 设置项：主题选择
        theme_label = Label(
            text='主题选择',
            font_name='ChineseFont',
            font_size=16,
            size_hint=(1, 0.2)
        )
        content.add_widget(theme_label)
        
        # 主题切换按钮
        theme_buttons = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.2))
        light_theme_btn = Button(
            text='浅色主题',
            font_name='ChineseFont',
            font_size=14
        )
        dark_theme_btn = Button(
            text='深色主题',
            font_name='ChineseFont',
            font_size=14
        )
        theme_buttons.add_widget(light_theme_btn)
        theme_buttons.add_widget(dark_theme_btn)
        content.add_widget(theme_buttons)
        
        # 设置项：音量控制
        volume_label = Label(
            text='默认音量',
            font_name='ChineseFont',
            font_size=16,
            size_hint=(1, 0.2)
        )
        content.add_widget(volume_label)
        
        self.default_volume_slider = Slider(
            min=0,
            max=1,
            value=0.5,
            size_hint=(1, 0.2)
        )
        content.add_widget(self.default_volume_slider)
        
        # 关闭按钮
        close_btn = Button(
            text='关闭',
            font_name='ChineseFont',
            font_size=14,
            size_hint=(1, 0.2)
        )
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)
        
        popup = Popup(
            title='设置',
            content=content,
            size_hint=(0.8, 0.6)
        )
        popup.open()

    def create_analysis_panel(self):
        """
        创建分析面板
        """
        analysis_panel = BoxLayout(
            orientation='vertical',
            spacing=10,
            padding=[10, 10, 10, 10],
            size_hint=(1, 1)
        )

        # 添加分析按钮
        analyze_btn = Button(
            text='开始分析',
            font_name='ChineseFont',
            font_size=14,
            size_hint=(1, 0.1)
        )
        analyze_btn.bind(on_press=self.start_analysis)
        analysis_panel.add_widget(analyze_btn)

        # 添加结果展示区域
        self.result_grid = GridLayout(
            cols=1,
            size_hint_y=None,
            spacing=10,
            padding=[10, 10, 10, 10]
        )
        self.result_grid.bind(minimum_height=self.result_grid.setter('height'))

        # 添加滚动视图
        scroll_view = ScrollView(size_hint=(1, 0.9))
        scroll_view.add_widget(self.result_grid)
        analysis_panel.add_widget(scroll_view)

        return analysis_panel

    def add_about_tab(self):
        """
        添加关于页面
        """
        about_tab = BoxLayout(orientation='vertical', spacing=10, padding=10)
        self.main_content.add_widget(about_tab)

    def show_file_chooser(self, instance):
        """
        显示文件选择器弹窗
        :param instance: 触发事件的控件
        """
        # 创建文件选择器布局
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 路径输入框
        self.path_input = TextInput(
            multiline=False,
            size_hint=(0.8, 1),
            font_name=self.default_font,
            font_size=14
        )
        self.path_input.text = os.path.expanduser('~')
        
        # 刷新按钮
        refresh_btn = FancyButton(
            text='刷新',
            font_name='ChineseFont',
            size_hint=(0.2, 1),
            on_press=self.update_file_chooser_path
        )
        
        # 路径导航栏
        path_bar = BoxLayout(size_hint=(1, 0.1), spacing=10)
        path_bar.add_widget(self.path_input)
        path_bar.add_widget(refresh_btn)
        
        # 文件选择器
        self.file_chooser = FileChooserListView(
            path=self.path_input.text,
            filters=['*.mp3', '*.wav', '.flac', '.ogg'],  # 添加更多支持的格式
            size_hint=(1, 0.8),
            font_name=self.default_font
        )
        self.file_chooser.bind(path=self.update_path_input)
        self.file_chooser.bind(selection=self.select_file)
        
        # 底部按钮
        btn_bar = BoxLayout(size_hint=(1, 0.1), spacing=10)
        cancel_btn = FancyButton(
            text='取消',
            font_name='ChineseFont',
            on_press=lambda x: self.popup.dismiss()
        )
        btn_bar.add_widget(cancel_btn)
        
        # 组装布局
        content.add_widget(path_bar)
        content.add_widget(self.file_chooser)
        content.add_widget(btn_bar)
        
        # 创建弹窗
        self.popup = Popup(
            title='选择音乐文件',
            content=content,
            size_hint=(0.9, 0.9),
            title_font='ChineseFont'
        )
        self.popup.open()

        

    def update_path_input(self, instance, value):
        """
        更新路径输入框
        :param instance: 触发事件的控件
        :param value: 新的路径值
        """
        self.path_input.text = value

    def update_file_chooser_path(self, instance):
        """
        更新文件选择器路径
        :param instance: 触发事件的控件
        """
        if os.path.exists(self.path_input.text):
            self.file_chooser.path = self.path_input.text

    def select_file(self, instance, selection, *args):
        """
        选择文件后的回调
        :param instance: 触发事件的控件
        :param selection: 选择的文件列表
        """
        if selection:
            try:
                self.selected_file = selection[0]
                
                # 检查文件格式
                supported_formats = ('.mp3', '.wav', '.flac', '.ogg')
                if not self.selected_file.lower().endswith(supported_formats):
                    raise ValueError(f'仅支持 {", ".join(supported_formats)} 文件！')
                
                # 检查文件是否存在
                if not os.path.exists(self.selected_file):
                    raise FileNotFoundError(f"文件不存在: {self.selected_file}")
                
                # 更新文件标签
                self.file_label.text = f'已选择文件: {os.path.basename(self.selected_file)}'

                # 更新文件信息
                file_size = os.path.getsize(self.selected_file) / (1024 * 1024)  # 转换为MB
                file_size_str = f'{file_size:.2f} MB'
                
                y, sr = librosa.load(self.selected_file, sr=None)
                duration = librosa.get_duration(y=y, sr=sr)
                minutes = int(duration // 60)
                seconds = int(duration % 60)
                duration_str = f'{minutes}:{seconds:02d}'
                
                self.file_info_label.text = f'文件大小: {file_size_str}\n时长: {duration_str}'

                self.popup.dismiss()
                
                # 清空之前的分析结果
                self.clear_results()
                
                # 更新波形图
                self.update_waveform()
                
                # 重置进度条
                self.progress_bar.value = 0
                
                # 加载音频文件
                self.load_file(self.selected_file)
                
            except Exception as e:
                self.show_error_message(f'加载失败: {str(e)}')
                self.selected_file = None
                self.file_label.text = '未选择文件'
                self.file_info_label.text = ''

    def update_waveform(self, filepath=None):
        """更新波形显示"""
        # 如果传入了文件路径，则更新 selected_file
        if filepath:
            self.selected_file = filepath
            
        if hasattr(self, 'selected_file') and self.selected_file:
            try:
                # 清空之前的波形图
                self.waveform_image.source = 'assets/waveform_placeholder.png'
                # 加载音频文件
                y, sr = librosa.load(self.selected_file, sr=None)
                
                # 创建波形图
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(y)
                ax.set_title('Waveform')
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Amplitude')
                
                # 将图形渲染为图像
                canvas = FigureCanvasAgg(fig)
                buf = io.BytesIO()
                canvas.print_png(buf)
                buf.seek(0)
                
                # 将图像加载到Kivy的Image控件
                im = CoreImage(buf, ext='png')
                self.waveform_image.texture = im.texture
                
                # 清理资源
                buf.close()
                plt.close(fig)
            except Exception as e:
                self.show_message(f'波形图显示失败: {str(e)}')
        else:
            self.show_message('请先选择音乐文件！')

    def start_analysis(self, instance):
        """
        开始分析
        :param instance: 触发事件的控件
        """
        if hasattr(self, 'selected_file'):
            self.progress_bar.value = 0
            self.analyze_audio()
        else:
            self.show_message('请先选择音乐文件！')

    def update_progress(self, dt):
        """
        更新播放进度
        """
        if self.sound and self.sound.state == 'play':
            try:
                current_time = self.sound.get_pos()
                if current_time < 0:  # 某些平台可能返回负值
                    current_time = 0
                
                # 更新进度条
                progress = (current_time / self.total_duration) * 100
                self.progress_slider.value = progress
                
                # 更新时间显示
                current_min = int(current_time // 60)
                current_sec = int(current_time % 60)
                total_min = int(self.total_duration // 60)
                total_sec = int(self.total_duration % 60)
                self.progress_label.text = f'{current_min:02d}:{current_sec:02d} / {total_min:02d}:{total_sec:02d}'
                
            except Exception as e:
                print(f"更新进度时出错: {str(e)}")


    def _analyze_audio_thread(self):
        """
        在后台线程中执行音频分析
        """
        # 使用Clock逐步更新进度条
        Clock.schedule_interval(self.update_progress, 0.1)
        
        # 加载音频文件
        y, sr = librosa.load(self.selected_file, sr=None)
        
        # 提取音乐特征
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        zero_crossing_rate = librosa.feature.zero_crossing_rate(y)
        
        # 在主线程中更新UI
        Clock.schedule_once(lambda dt: self._update_ui(tempo, spectral_centroid, zero_crossing_rate))

    def _update_ui(self, tempo, spectral_centroid, zero_crossing_rate):
        """
        在主线程中更新UI
        """
        self.show_message(f'节奏: {float(tempo):.2f} BPM\n'
                        f'频谱中心: {float(spectral_centroid.mean()):.2f} Hz\n'
                        f'过零率: {float(zero_crossing_rate.mean()):.2f}')
        
        # 停止进度条更新
        Clock.unschedule(self.update_progress)
        self.progress_bar.value = 100

    def analyze_audio(self):
        """
        分析音频
        """
        if hasattr(self, 'selected_file'):
            try:
                # 清空之前的分析结果
                self.clear_results()
                self.progress_bar.value = 0
                
                # 使用线程执行耗时操作
                Thread(target=self._analyze_audio_thread, daemon=True).start()
            except Exception as e:
                self.show_message(f'音频分析失败: {str(e)}')
        else:
            self.show_message('请先选择音乐文件！')

    
    def clear_results(self):
        """
        清空结果展示区域
        """
        if hasattr(self, 'result_grid'):
            self.result_grid.clear_widgets()

    def show_message(self, message):
        """
        显示消息
        :param message: 要显示的消息内容
        """
       # 清空之前的内容
        self.clear_results()
    
        
        # 添加新消息
        result_label = Label(
        text=message, 
        size_hint_y=None, 
        height=100,  # 增加高度以确保完整显示
        font_name=self.default_font,
        font_size=16,  # 增大字体
        color=(1, 1, 1, 1),  # 黑色文本
        halign='center',  # 居中对齐
        valign='middle',  # 垂直居中
        padding=(10, 10)  # 增加内边距
        )
        result_label.bind(texture_size=result_label.setter('size'))
        self.result_grid.add_widget(result_label)
        
        # 确保结果区域可以滚动
        self.result_grid.height = result_label.height

    def show_settings(self, instance):
        """
        显示设置窗口
        :param instance: 触发事件的控件
        """
        # 创建设置窗口布局
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 添加主题选择
        theme_label = Label(
            text='选择主题:',
            size_hint=(1, 0.1),
            font_name=self.default_font
        )
        content.add_widget(theme_label)
        
        theme_selector = TextInput(
            text='light',
            size_hint=(1, 0.1),
            font_name=self.default_font
        )
        content.add_widget(theme_selector)
        
        # 添加确认按钮
        confirm_btn = FancyButton(
            text='确认',
            size_hint=(1, 0.1),
            font_name=self.default_font,
            on_press=lambda x: self.apply_settings(theme_selector.text)
        )
        content.add_widget(confirm_btn)
        
        # 创建弹窗
        self.settings_popup = Popup(
            title='设置',
            content=content,
            size_hint=(0.8, 0.6),
            title_font=self.default_font
        )
        self.settings_popup.open()

    def apply_settings(self, theme):
        """
        应用设置
        :param theme: 选择的主题
        """
        # 定义主题颜色
        if theme == 'light':
            bg_color = (1, 1, 1, 1)  # 白色背景
            text_color = (0, 0, 0, 1)  # 黑色文字
            button_color = (0.9, 0.9, 0.9, 1)  # 浅灰色按钮
        elif theme == 'dark':
            bg_color = (0.1, 0.1, 0.1, 1)  # 深色背景
            text_color = (1, 1, 1, 1)  # 白色文字
            button_color = (0.2, 0.2, 0.2, 1)  # 深灰色按钮

        # 应用主题到窗口
        Window.clearcolor = bg_color

        # 更新所有标签颜色
        self._update_widget_colors(self, text_color, bg_color, button_color)

        self.settings_popup.dismiss()
        self.show_message(f'主题已切换为: {theme}')

    def _update_widget_colors(self, widget, text_color, bg_color, button_color):
        """
        递归更新所有子控件的颜色
        """
        if hasattr(widget, 'children'):
            for child in widget.children:
                self._update_widget_colors(child, text_color, bg_color, button_color)

        # 更新标签颜色
        if isinstance(widget, Label):
            widget.color = text_color
            if hasattr(widget, 'background_color'):
                widget.background_color = bg_color

        # 更新按钮颜色
        if isinstance(widget, Button):
            widget.background_color = button_color
            widget.color = text_color

        # 更新文本输入框颜色
        if isinstance(widget, TextInput):
            widget.background_color = bg_color
            widget.foreground_color = text_color

    def show_about_panel(self, instance):
        """
        显示关于面板
        :param instance: 触发事件的控件
        """
        # 创建面板内容
        content = BoxLayout(orientation='vertical', spacing=10, padding=20)
        about_label = Label(
            text='音乐分析程序\n版本 1.0\n作者: 屠居',
            font_name=self.default_font,
            font_size=16,
            halign='center',
            color=(0.5, 0.5, 0.5, 1)  # 灰色字体
        )
        content.add_widget(about_label)
        
        # 创建关闭按钮
        close_btn = Button(
            text='关闭',
            size_hint=(1, 0.2),
            font_name=self.default_font,
            background_color=(0.8, 0.8, 0.8, 0.8),  # 半透明灰色
            color=(0.5, 0.5, 0.5, 1),  # 灰色字体
            on_press=lambda x: self.about_popup.dismiss()
        )
        content.add_widget(close_btn)
        
        # 创建上拉面板
        self.about_popup = Popup(
            title='',
            content=content,
            size_hint=(0.8, None),
            height=200,  # 根据内容调整高度
            background_color=(1, 1, 1, 0.9),  # 半透明背景
            separator_height=0,  # 隐藏标题栏
            auto_dismiss=False
        )
        
        # 添加上拉动画
        self.about_popup.opacity = 0
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.about_popup)
        
        # 打开面板
        self.about_popup.open()        


    def _update_waveform(self, y, sr):
        """
        在主线程中更新波形图
        """
        # 绘制波形图
        fig = plt.figure(figsize=(10, 2))
        librosa.display.waveshow(y, sr=sr)
        plt.axis('off')
        
        # 将波形图转换为Kivy可用的图像
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        buf.seek(0)
        core_image = CoreImage(buf, ext='png')
        self.waveform_image.texture = core_image.texture
        
        # 停止进度条更新
        Clock.unschedule(self.update_progress)
        self.progress_bar.value = 100

    def show_link_input(self, instance):
        """
        显示链接输入弹窗
        :param instance: 触发事件的控件
        """
        # 创建弹窗布局
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 链接输入框
        self.link_input = TextInput(
            hint_text='请输入音乐链接',
            multiline=False,
            size_hint=(1, 0.2),
            font_name='ChineseFont',
            font_size=14
        )
        content.add_widget(self.link_input)
        
        # 底部按钮
        btn_bar = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        # 确定按钮
        confirm_btn = FancyButton(
            text='确定',
            font_name='ChineseFont',
            on_press=self.handle_link_input
        )
        btn_bar.add_widget(confirm_btn)
        
        # 取消按钮
        cancel_btn = FancyButton(
            text='取消',
            font_name='ChineseFont',
            on_press=lambda x: self.popup.dismiss()
        )
        btn_bar.add_widget(cancel_btn)
        
        content.add_widget(btn_bar)
        
        # 创建弹窗
        self.popup = Popup(
            title='导入在线音乐',
            content=content,
            size_hint=(0.8, 0.4),
            title_font='ChineseFont'
        )
        self.popup.open()

    def handle_link_input(self, instance):
        """
        处理链接输入
        :param instance: 触发事件的控件
        """
        link = self.link_input.text.strip()
        if not link:
            self.show_error_message('请输入有效的音乐链接！')
            return
        
        try:
            # 下载音频文件
            audio_file = self.download_audio(link)
            
            # 加载音频文件
            self.load_file(audio_file)
            
            # 显示成功提示
            self.show_success_message('导入成功！')
            
            # 关闭弹窗
            self.popup.dismiss()
        except Exception as e:
            self.show_error_message(f'导入失败: {str(e)}')

    def download_audio(self, link):
        """
        下载在线音乐
        :param link: 音乐链接
        :return: 下载的音频文件路径
        """
        # 解析链接并下载音频文件
        # 这里需要根据具体平台实现
        # 示例：假设链接是直接指向音频文件的URL
        import requests
        from urllib.parse import urlparse
        from pathlib import Path
        
        # 检查链接是否有效
        parsed_url = urlparse(link)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise ValueError('无效的音乐链接！')
        
        # 下载文件
        response = requests.get(link, stream=True)
        if response.status_code != 200:
            raise ValueError('无法下载音频文件！')
        
        # 保存到临时文件
        temp_dir = Path('temp')
        temp_dir.mkdir(exist_ok=True)
        file_path = temp_dir / 'downloaded_audio.mp3'
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return str(file_path)
    