from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path
import os

# 添加字体支持
resource_add_path(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts'))
LabelBase.register('ChineseFont', 'SourceHanSansCN-Regular.otf')

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        Window.size = (800, 600)
        Window.title = '音乐分析程序'
        
        # 设置默认字体
        self.default_font = 'ChineseFont'
        
        # 顶部工具栏
        self.add_widget(self.create_toolbar())
        
        # 主内容区域
        self.main_content = TabbedPanel(do_default_tab=False)
        self.add_widget(self.main_content)
        
        # 添加分析页面
        self.add_analysis_tab()
        
        # 添加关于页面
        self.add_about_tab()

    def create_toolbar(self):
        """创建顶部工具栏"""
        toolbar = BoxLayout(size_hint=(1, 0.1))
        toolbar.add_widget(Button(
            text='文件', 
            font_name=self.default_font,
            on_press=self.show_file_chooser
        ))
        toolbar.add_widget(Button(
            text='分析', 
            font_name=self.default_font,
            on_press=self.start_analysis
        ))
        toolbar.add_widget(Button(
            text='设置', 
            font_name=self.default_font,
            on_press=self.show_settings
        ))
        return toolbar

    def add_analysis_tab(self):
        """添加分析页面"""
        analysis_tab = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 标题
        analysis_tab.add_widget(Label(
            text='音乐分析', 
            font_size=24,
            font_name=self.default_font
        ))
        
        # 文件选择区域
        file_box = BoxLayout(size_hint=(1, 0.1))
        self.file_label = Label(
            text='未选择文件', 
            size_hint=(0.8, 1),
            font_name=self.default_font
        )
        file_box.add_widget(self.file_label)
        file_box.add_widget(Button(
            text='选择文件', 
            size_hint=(0.2, 1), 
            font_name=self.default_font,
            on_press=self.show_file_chooser
        ))
        analysis_tab.add_widget(file_box)
        
        # 波形显示区域
        self.waveform_image = Image(
            source='', 
            size_hint=(1, 0.4),
            allow_stretch=True
        )
        analysis_tab.add_widget(self.waveform_image)
        
        # 分析结果区域
        result_scroll = ScrollView(size_hint=(1, 0.4))
        self.result_grid = GridLayout(cols=1, size_hint_y=None)
        self.result_grid.bind(minimum_height=self.result_grid.setter('height'))
        result_scroll.add_widget(self.result_grid)
        analysis_tab.add_widget(result_scroll)
        
        # 进度条
        self.progress_bar = ProgressBar(max=100, size_hint=(1, 0.05))
        analysis_tab.add_widget(self.progress_bar)
        
        self.main_content.add_widget(analysis_tab)

    def add_about_tab(self):
        """添加关于页面"""
        about_tab = BoxLayout(orientation='vertical', padding=20)
        about_tab.add_widget(Label(
            text='音乐分析程序 v1.0', 
            font_size=24,
            font_name=self.default_font
        ))
        about_tab.add_widget(Label(
            text='开发者：你的名字',
            font_name=self.default_font
        ))
        about_tab.add_widget(Label(
            text='使用说明：\n1. 选择音乐文件\n2. 点击分析按钮\n3. 查看分析结果',
            font_name=self.default_font
        ))
        self.main_content.add_widget(about_tab)

    def show_file_chooser(self, instance):
        """显示文件选择器"""
        self.file_chooser = FileChooserListView()
        self.file_chooser.bind(on_submit=self.select_file)
        self.popup = Popup(
            title='选择音乐文件', 
            content=self.file_chooser, 
            size_hint=(0.9, 0.9),
            title_font=self.default_font
        )
        self.popup.open()

    def select_file(self, instance, selection, *args):
        """选择文件后的回调"""
        if selection:
            self.selected_file = selection[0]
            self.file_label.text = f'已选择文件: {os.path.basename(self.selected_file)}'
            self.popup.dismiss()
            self.update_waveform()

    def update_waveform(self):
        """更新波形显示"""
        # TODO: 实现波形显示
        self.waveform_image.source = 'assets/waveform_placeholder.png'

    def start_analysis(self, instance):
        """开始分析"""
        if hasattr(self, 'selected_file'):
            self.progress_bar.value = 0
            self.analyze_audio()
        else:
            self.show_message('请先选择音乐文件！')

    def analyze_audio(self):
        """分析音频"""
        # TODO: 实现分析逻辑
        self.progress_bar.value = 100
        self.show_message('分析完成！')

    def show_message(self, message):
        """显示消息"""
        self.result_grid.add_widget(Label(
            text=message, 
            size_hint_y=None, 
            height=40,
            font_name=self.default_font
        ))

    def show_settings(self, instance):
        """显示设置窗口"""
        # TODO: 实现设置功能
        self.show_message('设置功能开发中...')