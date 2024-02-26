import tkinter as tk
from functions import *
from OutData2D import OutData2D
from Static2D import Static2D
from Dynamic2D import Dynamic2D
from OutData3D import OutData3D
from Static3D import Static3D
from Dynamic3D import Dynamic3D
from Document import Document
import warnings
import webbrowser
warnings.filterwarnings("ignore")

from postprocess3D import *


class PostProcessGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        # 设置窗口名称
        self.title('重力坝抗震分析后处理程序')
        # 设置窗口大小和位置
        screen_width = self.winfo_screenwidth()  # 获取屏幕宽度
        screen_height = self.winfo_screenheight()  # 获取屏幕高度
        self.win_width = 1440  # 窗口宽度
        self.win_height = 810  # 窗口高度
        x = 0.5 * (screen_width - self.win_width)  # 窗口左边距
        y = 0.2 * (screen_height - self.win_height)  # 窗口上边距
        self.geometry('%dx%d+%d+%d' % (self.win_width, self.win_height, x, y))

        # 注册窗口变动事件
        # self.window.bind('<Configure>', self.windown_resize)

    
    def _quit(self):
        self.quit()
        self.destroy() 


    def open_url(self):
        webbrowser.open('https://www.researchgate.net/profile/Lin-Li-270')


    def set_init_window(self):
        # 设置菜单栏
        self.menubar = tk.Menu(self)  # 主菜单栏

        # 二维后处理二级菜单栏
        menu_2D = tk.Menu(self.menubar)
        menu_2D.add_command(label='导出数据', command=lambda: self.show_page(OutData2D))
        menu_2D.add_command(label='静力', command=lambda: self.show_page(Static2D))
        # menu_2D.add_command(label='反应谱法', command=lambda: self.show_page(Rps2D))
        menu_2D.add_command(label='时程法', command=lambda: self.show_page(Dynamic2D))
        # menu_2D.add_command(label='一键处理', command=lambda: self.show_page(OutAll2D))

        # 三维后处理二级菜单栏
        menu_3D = tk.Menu(self.menubar)
        menu_3D.add_command(label='导出数据', command=lambda: self.show_page(OutData3D))
        menu_3D.add_command(label='静力', command=lambda: self.show_page(Static3D))
        menu_3D.add_command(label='时程法', command=lambda: self.show_page(Dynamic3D))
        # menu_3D.add_command(label='一键处理', command=lambda: self.show_page(OutAll3D))

        # 帮助菜单栏
        menu_help = tk.Menu(self.menubar)
        menu_help.add_command(label='帮助文档', command=lambda: self.show_page(Document))
        menu_help.add_command(label='联系我们', command=self.open_url)

        # 将二级菜单链接到一级菜单
        self.menubar.add_cascade(label='二维有限元后处理', menu=menu_2D)
        self.menubar.add_cascade(label='三维有限元后处理', menu=menu_3D)
        self.menubar.add_cascade(label='帮助', menu=menu_help)
        self.config(menu=self.menubar)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (OutData2D, Static2D, Dynamic2D, OutData3D, Static3D, Dynamic3D, Document):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_page(Document)


    def show_page(self, name):
        frame = self.frames[name]
        frame.tkraise()


    # 窗口尺寸调整
    def windown_resize(self, event=None):
        if event is not None:
            if self.win_width != self.window.winfo_width() or self.win_height != self.window.winfo_height():
                self.win_width = self.window.winfo_width()
                self.win_height = self.window.winfo_height()

    
    def plot_fig(self):
        pass


# class Rps2D(tk.Frame):
#     def __init__(self, parent, root):
#         super().__init__(parent)
#         self.width = root.win_width
#         self.height = root.win_height
#         self.root = root
#         self.set_page()


#     def set_page(self):        
#         w = self.width
#         h = self.height

#         font_size1 = 16
#         font_size2 = 12

#         # 二维反应谱法功能容器框
#         func_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.42 * w), height=int(0.6 * h))
#         func_frame.place(x=0.05 * w, y=0.05 * h)
#         func_label = tk.Label(self, text='二维反应谱法', font=('黑体', font_size1))
#         func_label.place(x=0.22 * w, y=0.01 * h)
        
#         # 绘图按钮
#         plot_fig = tk.Button(self, text='绘制', font=('黑体', font_size2), bg='lightblue', width=8, height=5, command=self.root.plot_fig)
#         plot_fig.place(x=0.47 * w, y=0.3 * h)
        
#         # 图片显示容器框
#         fig_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.43 * w), height=int(0.6 * h))
#         fig_frame.place(x=0.52 * w, y=0.05 * h)
#         fig_label = tk.Label(self, text='图片显示', font=('黑体', font_size1))
#         fig_label.place(x=0.70 * w, y=0.01 * h)

#         # 日志容器框
#         log_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.9 * w), height=int(0.2 * h))
#         log_frame.place(x=0.05 * w, y=0.75 * h)
#         log_label = tk.Label(self, text='日志', font=('黑体', font_size1))
#         log_label.place(x=0.48 * w, y=0.71 * h)

# class OutAll2D(tk.Frame):
#     def __init__(self, parent, root):
#         super().__init__(parent)
#         self.width = root.win_width
#         self.height = root.win_height
#         self.root = root
#         self.set_page()


#     def set_page(self):        
#         w = self.width
#         h = self.height

#         font_size1 = 16
#         font_size2 = 12

#         # 二维一键处理功能容器框
#         func_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.42 * w), height=int(0.6 * h))
#         func_frame.place(x=0.05 * w, y=0.05 * h)
#         func_label = tk.Label(self, text='二维一键处理', font=('黑体', font_size1))
#         func_label.place(x=0.22 * w, y=0.01 * h)
        
#         # 绘图按钮
#         plot_fig = tk.Button(self, text='绘制', font=('黑体', font_size2), bg='lightblue', width=8, height=5, command=self.root.plot_fig)
#         plot_fig.place(x=0.47 * w, y=0.3 * h)
        
#         # 图片显示容器框
#         fig_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.43 * w), height=int(0.6 * h))
#         fig_frame.place(x=0.52 * w, y=0.05 * h)
#         fig_label = tk.Label(self, text='图片显示', font=('黑体', font_size1))
#         fig_label.place(x=0.70 * w, y=0.01 * h)

#         # 日志容器框
#         log_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.9 * w), height=int(0.2 * h))
#         log_frame.place(x=0.05 * w, y=0.75 * h)
#         log_label = tk.Label(self, text='日志', font=('黑体', font_size1))
#         log_label.place(x=0.48 * w, y=0.71 * h)


# class OutAll3D(tk.Frame):
#     def __init__(self, parent, root):
#         super().__init__(parent)
#         self.width = root.win_width
#         self.height = root.win_height
#         self.root = root
#         self.set_page()


#     def set_page(self):        
#         w = self.width
#         h = self.height

#         font_size1 = 16
#         font_size2 = 12

#         # 三维一键处理功能容器框
#         func_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.42 * w), height=int(0.6 * h))
#         func_frame.place(x=0.05 * w, y=0.05 * h)
#         func_label = tk.Label(self, text='三维一键处理', font=('黑体', font_size1))
#         func_label.place(x=0.22 * w, y=0.01 * h)
        
#         # 绘图按钮
#         plot_fig = tk.Button(self, text='绘制', font=('黑体', font_size2), bg='lightblue', width=8, height=5, command=self.root.plot_fig)
#         plot_fig.place(x=0.47 * w, y=0.3 * h)
        
#         # 图片显示容器框
#         fig_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.43 * w), height=int(0.6 * h))
#         fig_frame.place(x=0.52 * w, y=0.05 * h)
#         fig_label = tk.Label(self, text='图片显示', font=('黑体', font_size1))
#         fig_label.place(x=0.70 * w, y=0.01 * h)

#         # 日志容器框
#         log_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.9 * w), height=int(0.2 * h))
#         log_frame.place(x=0.05 * w, y=0.75 * h)
#         log_label = tk.Label(self, text='日志', font=('黑体', font_size1))
#         log_label.place(x=0.48 * w, y=0.71 * h)


XRDam_postprocexss = PostProcessGUI()
XRDam_postprocexss.set_init_window()
XRDam_postprocexss.protocol('WM_DELETE_WINDOW', XRDam_postprocexss._quit)
XRDam_postprocexss.mainloop()