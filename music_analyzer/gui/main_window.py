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

# 添加字体支持
resource_add_path(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts'))
LabelBase.register(
    name='ChineseFont', 
    fn_regular='SourceHanSansCN-Regular.otf', 
    fn_bold='SourceHanSansCN-Regular.otf'
)

class FancyButton(Button):
    """自定义带动画效果的按钮"""
    def on_touch_down(self, touch):
        """
        当按钮被点击时触发动画效果
        :param touch: 触摸事件
        """
        if self.collide_point(*touch.pos):
            anim = Animation(opacity=0.7, duration=0.1) + Animation(opacity=1, duration=0.1)
            anim.start(self)
        return super().on_touch_down(touch)

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        """
        初始化主窗口
        """
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 15
        Window.size = (1000, 700)
        Window.title = '音乐分析程序'
        
        # 设置默认字体
        self.default_font = 'ChineseFont'
        
        # 顶部工具栏
        self.add_widget(self.create_toolbar())
        
        # 主内容区域
        self.main_content = TabbedPanel(do_default_tab=False, background_color=(0.95, 0.95, 0.95, 1))
        self.add_widget(self.main_content)
        
        # 添加分析页面
        self.add_analysis_tab()
        
        # 添加关于页面
        self.add_about_tab()

    def create_toolbar(self):
        """
        创建顶部工具栏
        :return: 工具栏布局
        """
        toolbar = BoxLayout(size_hint=(1, 0.08), spacing=10)
        buttons = [
            ('文件', self.show_file_chooser),
            ('分析', self.start_analysis),
            ('设置', self.show_settings)
        ]
        
        for text, callback in buttons:
            btn = FancyButton(
                text=text,
                font_name=self.default_font,
                background_color=(0.2, 0.6, 1, 1),
                on_press=callback
            )
            toolbar.add_widget(btn)
        return toolbar

    def add_analysis_tab(self):
        """
        添加分析页面
        """
        analysis_tab = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # 文件标签
        self.file_label = Label(
            text='未选择文件',
            size_hint=(1, 0.1),
            font_name=self.default_font,
            font_size=14
        )
        analysis_tab.add_widget(self.file_label)
        
        # 波形图占位符
        self.waveform_image = Image(
            source='assets/waveform_placeholder.png',
            size_hint=(1, 0.5)
        )
        analysis_tab.add_widget(self.waveform_image)
        
        # 进度条
        self.progress_bar = ProgressBar(
            max=100,
            size_hint=(1, 0.05)
        )
        analysis_tab.add_widget(self.progress_bar)
        
        # 结果展示区域
        self.result_grid = GridLayout(cols=1, size_hint_y=None)
        self.result_grid.bind(minimum_height=self.result_grid.setter('height'))
        
        scroll_view = ScrollView(size_hint=(1, 0.35))
        scroll_view.add_widget(self.result_grid)
        analysis_tab.add_widget(scroll_view)
        
        # 添加到主内容区域
        self.main_content.add_widget(analysis_tab)

    def add_about_tab(self):
        """
        添加关于页面
        """
        about_tab = BoxLayout(orientation='vertical', spacing=10, padding=10)
        about_label = Label(
            text='音乐分析程序\n版本 1.0\n作者: 你的名字',
            font_name=self.default_font,
            font_size=16,
            halign='center'
        )
        about_tab.add_widget(about_label)
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
            size_hint=(0.2, 1),
            font_name=self.default_font,
            on_press=self.update_file_chooser_path
        )
        
        # 路径导航栏
        path_bar = BoxLayout(size_hint=(1, 0.1), spacing=10)
        path_bar.add_widget(self.path_input)
        path_bar.add_widget(refresh_btn)
        
        # 文件选择器
        self.file_chooser = FileChooserListView(
            path=self.path_input.text,
            filters=['*.mp3', '*.wav'],
            size_hint=(1, 0.8),
            font_name=self.default_font
        )
        self.file_chooser.bind(path=self.update_path_input)
        self.file_chooser.bind(selection=self.select_file)
        
        # 底部按钮
        btn_bar = BoxLayout(size_hint=(1, 0.1), spacing=10)
        cancel_btn = FancyButton(
            text='取消',
            font_name=self.default_font,
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
            title_font=self.default_font
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
            self.selected_file = selection[0]
            self.file_label.text = f'已选择文件: {os.path.basename(self.selected_file)}'
            self.popup.dismiss()
            self.update_waveform()

    def update_waveform(self):
        """
        更新波形显示
        """
        # TODO: 实现波形显示
        self.waveform_image.source = 'assets/waveform_placeholder.png'

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

    def analyze_audio(self):
        """
        分析音频
        """
        # TODO: 实现分析逻辑
        self.progress_bar.value = 100
        self.show_message('分析完成！')

    def show_message(self, message):
        """
        显示消息
        :param message: 要显示的消息内容
        """
        self.result_grid.add_widget(Label(
            text=message, 
            size_hint_y=None, 
            height=40,
            font_name=self.default_font
        ))

    def show_settings(self, instance):
        """
        显示设置窗口
        :param instance: 触发事件的控件
        """
        # TODO: 实现设置功能
        self.show_message('设置功能开发中...')