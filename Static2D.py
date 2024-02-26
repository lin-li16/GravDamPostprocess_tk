import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from Combopicker import Combopicker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.backends.backend_svg
import os
from functions import *
from postprocess2D import *


class Static2D(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.width = root.win_width  # 获取窗口宽度
        self.height = root.win_height  # 获取窗口高度
        self.odb_path = tk.StringVar()  # 定义odb结果文件路径
        self.mesh_path = tk.StringVar()  # 定义网格文件路径
        self.bound_path = tk.StringVar()  # 定义边界文件路径
        self.Nset, self.Elset, self.Surface = [], [], []  # 初始化结点集、单元集和表面集
        self.cengmian = []  # 初始化层面集合
        self.nodes = None  # 初始化结点坐标
        self.bound = None  # 初始化边界结点
        self.slide_f = tk.StringVar()  # 初始化抗剪断参数f
        self.slide_c = tk.StringVar()  # 初始化抗剪断参数c
        self.K_value = tk.StringVar()  # 初始化抗滑稳定安全系数K
        self.figs = []  # 初始化图片列表
        self.figs_type = []  # 初始化图片类型列表
        self.figs_data = []  # 初始化图片数据
        self.current_fig = None  # 初始化当前显示的图片
        self.fig_title = []  # 初始化图片标题列表
        self.fig_title_current = tk.StringVar(value='图片显示')  # 初始化当前图片标题
        self.set_page()  # 页面设置


    def get_odb_path(self):
        """选择odb结果文件，将路径赋值于self.odb_path
        """
        path = tkinter.filedialog.askopenfilename(title='请选择odb结果文件')
        self.odb_path.set(path)


    def get_mesh_path(self):
        """选择网格文件，将路径赋值于self.mesh_path
        """
        path = tkinter.filedialog.askopenfilename(title='请选择网格文件')
        self.mesh_path.set(path)


    def get_bound_path(self):
        """选择边界文件，将路径赋值于self.bound_path
        """
        path = tkinter.filedialog.askopenfilename(title='请选择边界文件')
        self.bound_path.set(path)


    def read_mesh_bound(self):
        """读取网格和分析步文件，获取网格文件中的结点集、单元集和表面集的名称，分析步文件中的分析步名称，并更新对应的几个成员变量
        """
        if not self.odb_path.get().endswith('.odb'):  # 判断结果文件格式是否正确
            self.write_log_to_Text('结果文件格式错误，请选择Abaqus的odb文件')
        if not self.mesh_path.get().endswith('.inp'):  # 判断文件格式是否正确
            self.write_log_to_Text('网格文件格式错误，请选择Abaqus的inp文件')
            self.Nset, self.Elset, self.Surface = [], [], []
            self.nodes = None
        else:
            self.nodes = read_nodes(self.mesh_path.get(), dims=2)  # 读取所有结点坐标
            self.Nset, self.Elset, self.Surface = read_mesh(self.mesh_path.get())  # 读取所有集合
            for ns in self.Nset:
                if 'cengmian' in ns.lower() and ns not in self.cengmian:  # 读取层面
                    self.cengmian.append(ns)
            self.write_log_to_Text('网格文件中共定义了%d个结点，%d个结点集，%d个单元集，%d个面' % (self.nodes.shape[0], len(self.Nset), len(self.Elset), len(self.Surface)))
        if self.bound_path.get() == '':
            self.write_log_to_Text('请选择边界文件')
            self.bound = None
        else:
            self.bound = read_bound(self.bound_path.get())
            self.write_log_to_Text('边界文件共有%d个结点' % len(self.bound))

        # 更新下拉选择框
        self.renew_combobox()

    
    def get_K_value(self):
        """计算抗滑稳定安全系数
        """
        if self.odb_path.get() == '':  # 检查是否选了odb文件
            self.write_log_to_Text('没有选择结果文件，请读取结果文件')
        else:
            odb_dir = os.path.dirname(self.odb_path.get())  # 获取odb文件所在的文件夹
            cengmian = self.slide_cengmian_ddl.get()  # 获取选择的层面
            ff = float(self.slide_f.get())  # 获取f'值
            cc = float(self.slide_c.get())  # 获取c'值
            slide_data_path = os.path.join(odb_dir, 'sta-slid-%s.csv' % cengmian)
            if os.path.exists(slide_data_path):
                result = sta_slide(slide_data_path, ff, cc)
                self.K_value.set('%.3f' % result)
                self.write_log_to_Text('抗滑稳定安全系数计算完成')
            else:
                self.write_log_to_Text('没有找到抗滑稳定数据')

    
    def clear_file_entry(self):
        """清除选择的网格、分析步和odb结果文件
        """
        self.mesh_path.set('')
        self.odb_path.set('')
        self.bound_path.set('')
        self.Nset, self.Elset, self.Surface = [], [], []
        self.cengmian = []
        self.nodes = None
        self.bound = None  
        self.renew_combobox()  # 更新下拉选择框
        self.write_log_to_Text('清除文件成功！')
        # 清除图片显示框
        self.figs = []  # 初始化图片列表
        self.figs_type = []  # 初始化图片类型列表
        self.figs_data = []  # 初始化图片数据
        self.current_fig = None  # 初始化当前显示的图片
        self.fig_title = []  # 初始化图片标题列表
        self.fig_title_current.set('图片显示')  # 初始化当前图片标题
        for widget in self.fig_frame.winfo_children():
            widget.destroy()
        if self.fig_change_frame.winfo_ismapped():
            self.fig_change_frame.place_forget()


    def clear_select_entry(self):
        """清除绘图选择框和输入框
        """
        self.disp_direc_ddl.delete('0', 'end')
        self.stre_direc_ddl.delete('0', 'end')
        self.dmgt_direc_ddl.delete('0', 'end')
        self.slide_cengmian_ddl.delete('0', 'end')
        self.slide_f.set('')
        self.slide_c.set('')
        self.K_value.set('')
        self.write_log_to_Text('清除输入框成功')

    
    # 更新下拉框的选项
    def renew_combobox(self):
        """更新界面中用到结点、单元、表面和分析步集合的下拉选择框
        """
        self.slide_cengmian_ddl['value'] = self.cengmian


    def write_log_to_Text(self,logmsg):
        """日志动态打印

        Args:
            logmsg (string): 需要打印的字符串
        """
        current_time = get_current_time()  # 获取当前时间
        logmsg_in = str(current_time) +" " + str(logmsg) + "\n"
        self.log_data_Text.insert('end', logmsg_in)
        self.log_data_Text.see(tk.END)  # 使最新一行显示在窗口

    
    def log_clear(self):
        """清除日志框的内容
        """
        self.log_data_Text.delete('1.0', 'end')
    

    def plot_figs(self):
        """绘制所有图片
        """
        if self.odb_path.get() == '':  # 检查是否选了odb文件
            self.write_log_to_Text('没有选择结果文件，请读取结果文件')
        else:
            odb_dir = os.path.dirname(self.odb_path.get())  # 获取odb文件所在的文件夹
            if self.nodes is None:  # 检查是否读取了结点信息
                self.write_log_to_Text('没有结点坐标信息，请读取网格文件')
            else:
                if self.bound is None:  # 检查是否读取了边界信息
                    self.write_log_to_Text('没有边界结点信息，请读取边界文件')
                else:
                    boundary = get_boundary(self.bound, self.nodes)  # 获取用于绘图的边界
                    # 位移等值线图的绘制
                    disp_data_path = os.path.join(odb_dir, 'sta-disp-dam.csv')
                    if os.path.exists(disp_data_path):  # 检查是否存在位移数据文件
                        disp_comp = self.disp_direc_ddl.current_value
                        if disp_comp != '':
                            disp_comp = disp_comp.split(',')
                            for comp in disp_comp:
                                if comp != '全选':
                                    fig, xx, yy, zz = sta_disp_contour(disp_data_path, boundary, direc=comp)
                                    self.figs.append(fig)
                                    self.figs_data.append([xx, yy, zz])
                                    self.figs_type.append('contour')
                                    self.fig_title.append('%s向位移等值线图(cm)' % comp)
                    # 应力等值线图的绘制
                    stre_data_path = os.path.join(odb_dir, 'sta-stre-dam.csv')
                    if os.path.exists(stre_data_path):  # 检查是否存在应力数据文件
                        stre_comp = self.stre_direc_ddl.current_value
                        if stre_comp != '':
                            stre_comp = stre_comp.split(',')
                            for comp in stre_comp:
                                if comp != '全选':
                                    if comp == '大主应力':
                                        fig, xx, yy, zz = sta_stre_contour(stre_data_path, boundary, component='Smax')
                                    if comp == '小主应力':
                                        fig, xx, yy, zz = sta_stre_contour(stre_data_path, boundary, component='Smin')
                                    self.figs.append(fig)
                                    self.figs_data.append([xx, yy, zz])
                                    self.figs_type.append('contour')
                                    self.fig_title.append('%s等值线图(MPa)' % comp)
                    # 损伤因子分布图的绘制
                    dmgt_data_path = os.path.join(odb_dir, 'dmgt-dam1.csv')
                    if os.path.exists(dmgt_data_path):  # 检查是否存在损伤因子数据文件
                        if self.dmgt_direc_ddl.get() == '是':
                            fig, xx, yy, zz = dmgt_contour(dmgt_data_path, boundary)
                            self.figs.append(fig)
                            self.figs_data.append([xx, yy, zz])
                            self.figs_type.append('contourf')
                            self.fig_title.append('损伤因子分布图')
        # 默认显示第一张图片
        if len(self.figs) > 0:
            self.current_fig = self.figs[0]
            self.update_fig()
            self.write_log_to_Text('绘图完成，共绘制了%d张图片' % len(self.figs))

    
    def update_fig(self):
        """更新图片显示框的图片
        """
        # 将原来图片显示框的部件全部删除
        for widget in self.fig_frame.winfo_children():
            widget.destroy()
        self.fig_canvas = FigureCanvasTkAgg(self.current_fig, self.fig_frame)  # 创建图片画布，将当前图片显示在其中
        self.fig_canvas.draw()  # 绘制
        self.fig_canvas.get_tk_widget().pack(side='bottom')  # 调整图片显示位置
        self.toolbar = NavigationToolbar2Tk(self.fig_canvas, self.fig_frame)  # 创建图片工具栏
        self.toolbar.update()
        self.fig_title_current.set(self.fig_title[self.figs.index(self.current_fig)])  # 显示当前图片的标题
        # 如果当前图片是等值线图，显示图片调整组件
        if self.figs_type[self.figs.index(self.current_fig)] == 'contour':
            if not self.fig_change_frame.winfo_ismapped():
                self.fig_change_frame.place(x=0.578 * self.width, y=0.66 * self.height)
        else:  # 隐藏图片调整组件
            if self.fig_change_frame.winfo_ismapped():
                self.fig_change_frame.place_forget()


    def next_fig(self):
        """下一张图片
        """
        if len(self.figs) == 0:
            self.write_log_to_Text('图窗中没有图片')
        else:
            idx = np.min([self.figs.index(self.current_fig) + 1, len(self.figs) - 1])  # 获取当前图片下一张图片的索引
            self.current_fig = self.figs[idx]  # 将当前图片设置为下一张图片
            self.update_fig()  # 更新图片显示框的图片
            if idx == len(self.figs) - 1:  # 判断是否到达最后一张图片
                self.write_log_to_Text('已到最后一张图片')
            else:
                self.write_log_to_Text('下一张图片')

    
    def previous_fig(self):
        """上一张图片
        """
        if len(self.figs) == 0:
            self.write_log_to_Text('图窗中没有图片')
        else:
            idx = np.max([self.figs.index(self.current_fig) - 1, 0])  # 获取当前图片上一张图片的索引
            self.current_fig = self.figs[idx]  # 将当前图片设置为上一张图片
            self.update_fig()  # 更新图片显示框的图片
            if idx == 0:  # 判断是否到达第一张图片
                self.write_log_to_Text('已到第一张图片')
            else:
                self.write_log_to_Text('上一张图片')


    def replot(self):
        """重新绘制当前的图片
        """
        boundary = get_boundary(self.bound, self.nodes)  # 获取用于绘图的边界
        idx = self.figs.index(self.current_fig)  # 获取当前图片的索引
        fig_data = self.figs_data[idx]  # 获取当前图片的数据
        num_float = 1  # 等值线数值小数点位数默认值
        dele_height = 0  # 删除数据区域高度的默认值
        num_line = 10  # 等值线条数默认值
        max_min = 'abs'  # 显示最大最小值的默认值
        contour_max = np.max(fig_data[2])  # 等值线的默认最大值
        contour_min = np.min(fig_data[2])  # 等值线的默认最小值
        if '大主应力' in self.fig_title_current.get():  # 大主应力图必须显示最大值
            max_min = 'max'
        if self.num_float_entry.get() != '':  # 根据输入框更新小数点位数
            num_float = int(self.num_float_entry.get())
        if self.dele_height_entry.get() != '':  # 根据输入框更新删除数据区域高度
            dele_height = float(self.dele_height_entry.get())
        if self.contour_step_entry.get() != '':  # 根据输入框更新等值线间距，以及等值线最大最小值
            contour_step = float(self.contour_step_entry.get())
            if self.contour_min_entry.get() != '' and self.contour_max_entry.get() != '':
                contour_min = float(self.contour_min_entry.get())
                contour_max = float(self.contour_max_entry.get())
                num_line = np.arange(contour_min, contour_max, contour_step)
            elif self.contour_min_entry.get() == '' and self.contour_max_entry.get() != '':
                contour_max = float(self.contour_max_entry.get())
                num_line = np.arange(contour_min, contour_max, contour_step)
            elif self.contour_min_entry.get() != '' and self.contour_max_entry.get() == '':
                contour_min = float(self.contour_min_entry.get())
                num_line = np.arange(contour_min, contour_max, contour_step)
            else:
                num_line = np.arange(contour_min, contour_max, contour_step)
        # 重新绘制图片
        fig = plt.figure(figsize=(6.1, 4.4))
        if dele_height > 0:
            X, Y, ZS, hd = getContour(fig_data[0], fig_data[1], fig_data[2], boundary, dpi=100, Extrapolation=1, num_float=num_float, baseP=dele_height, numline=num_line, max_min=max_min)
        else:
            X, Y, ZS, hd = getContour(fig_data[0], fig_data[1], fig_data[2], boundary, dpi=100, Extrapolation=0, num_float=num_float, baseP=dele_height, numline=num_line, max_min=max_min)
        plt.tight_layout()
        self.figs[idx] = fig
        self.current_fig = self.figs[idx]
        self.update_fig()
        self.write_log_to_Text('重绘成功')


    def save_all_figs(self):
        """保存图片显示框里的所有图片
        """
        if self.odb_path.get() == '':  # 检查是否选了odb文件
            self.write_log_to_Text('没有选择结果文件，请读取结果文件')
        else:
            odb_dir = os.path.dirname(self.odb_path.get())  # 获取odb文件所在的文件夹
            fig_dir = os.path.join(odb_dir, 'figures')
            if not os.path.exists(fig_dir):  # 如果文件夹中没有figures文件夹，则创建
                os.makedirs(fig_dir)
            for idx, fig in enumerate(self.figs):
                fig.savefig(os.path.join(fig_dir, '静力%s.svg' % self.fig_title[idx]), bbox_inches='tight')
        self.write_log_to_Text('所有图片导出成功，共导出了%d张图片' % len(self.figs))


    def set_page(self):        
        """界面设计
        """
        w = self.width  # 获取窗口宽度，简化代码
        h = self.height # 获取窗口高度，简化代码

        # 三种字体大小
        font_size1 = 16  # 框架标题
        font_size2 = 16  # 重要选项说明文字
        font_size3 = 12  # 次要文字说明

        # 二维静力功能容器框
        func_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.42 * w), height=int(0.6 * h))
        func_frame.place(x=0.05 * w, y=0.05 * h)
        func_label = tk.Label(self, text='二维静力处理', font=('黑体', font_size1))
        func_label.place(x=0.22 * w, y=0.01 * h)

        # 结果读取组件
        odb_label = tk.Label(self, text='结果文件', bg='white', font=('黑体', font_size2))
        odb_label.place(x=0.13 * w, y=0.1 * h, anchor='e')
        odb_entry = tk.Entry(self, textvariable=self.odb_path, width=int(0.025 * w))
        odb_entry.place(x=0.14 * w, y=0.1 * h, anchor='w')
        odb_button = tk.Button(self, text='选择文件', command=self.get_odb_path)
        odb_button.place(x=0.33 * w, y=0.1 * h, anchor='w')

        # 网格读取组件
        mesh_label = tk.Label(self, text='网格文件', bg='white', font=('黑体', font_size2))
        mesh_label.place(x=0.13 * w, y=0.15 * h, anchor='e')
        mesh_entry = tk.Entry(self, textvariable=self.mesh_path, width=int(0.025 * w))
        mesh_entry.place(x=0.14 * w, y=0.15 * h, anchor='w')
        mesh_button = tk.Button(self, text='选择文件', command=self.get_mesh_path)
        mesh_button.place(x=0.33 * w, y=0.15 * h, anchor='w')

        # 边界读取组件
        bound_label = tk.Label(self, text='边界文件', bg='white', font=('黑体', font_size2))
        bound_label.place(x=0.13 * w, y=0.2 * h, anchor='e')
        bound_entry = tk.Entry(self, textvariable=self.bound_path, width=int(0.025 * w))
        bound_entry.place(x=0.14 * w, y=0.2 * h, anchor='w')
        bound_button = tk.Button(self, text='选择文件', command=self.get_bound_path)
        bound_button.place(x=0.33 * w, y=0.2 * h, anchor='w')

        # 读取和清除按钮
        read_button = tk.Button(self, text='读取', font=('黑体', 14), width=7, height=2, command=self.read_mesh_bound)
        read_button.place(x=0.39 * w, y=0.115 * h, anchor='w')
        clear_file_button = tk.Button(self, text='清除', font=('黑体', 14), width=7, height=2, command=self.clear_file_entry)
        clear_file_button.place(x=0.39 * w, y=0.187 * h, anchor='w')
        
        # 绘图按钮
        plot_fig = tk.Button(self, text='绘制', font=('黑体', 18), width=5, height=2, bg='lightblue', command=self.plot_figs)
        plot_fig.place(x=0.471 * w, y=0.3 * h)

        # 分割线
        canvas = tk.Canvas(self, bg='white', highlightthickness=0, width=0.38 * w, height=5)
        canvas.create_line(0, 2.5, 0.8 * w, 2.5, width=1, fill='gray', dash=(2, 2))
        canvas.place(x=0.065 * w, y=0.25 * h, anchor='w')

        # 位移导出设置
        disp_h = 0.32
        disp_label = tk.Label(self, text='位移', bg='white', font=('黑体', font_size2))
        disp_label.place(x=0.13 * w, y=disp_h * h, anchor='e')
        ## 位移方向选择
        disp_direc_label = tk.Label(self, text='方向', bg='white', font=('黑体', font_size3), fg='gray')
        disp_direc_label.place(x=0.17 * w, y=disp_h * h, anchor='e')
        self.disp_direc_ddl = Combopicker(self, values=['X', 'Y', '全选'], entrywidth=20)
        self.disp_direc_ddl.place(x=0.17 * w, y=disp_h * h, anchor='w')

        # 应力导出设置
        stre_h = 0.39
        stre_label = tk.Label(self, text='应力', bg='white', font=('黑体', font_size2))
        stre_label.place(x=0.13 * w, y=stre_h * h, anchor='e')
        ## 应力分量选择
        stre_direc_label = tk.Label(self, text='分量', bg='white', font=('黑体', font_size3), fg='gray')
        stre_direc_label.place(x=0.17 * w, y=stre_h * h, anchor='e')
        self.stre_direc_ddl = Combopicker(self, values=['大主应力', '小主应力', '全选'], entrywidth=20)
        self.stre_direc_ddl.place(x=0.17 * w, y=stre_h * h, anchor='w')

        # 损伤因子导出设置
        dmgt_h = 0.46
        dmgt_label = tk.Label(self, text='损伤因子', bg='white', font=('黑体', font_size2))
        dmgt_label.place(x=0.13 * w, y=dmgt_h * h, anchor='e')
        ## 是否绘制损伤因子分布图
        dmgt_direc_label = tk.Label(self, text='绘制', bg='white', font=('黑体', font_size3), fg='gray')
        dmgt_direc_label.place(x=0.17 * w, y=dmgt_h * h, anchor='e')
        self.dmgt_direc_ddl = ttk.Combobox(self, values=['是', '否'], width=17)
        self.dmgt_direc_ddl.place(x=0.17 * w, y=dmgt_h * h, anchor='w')

        # 抗滑稳定导出设置
        slide_h = 0.53
        slide_label = tk.Label(self, text='抗滑稳定', bg='white', font=('黑体', font_size2))
        slide_label.place(x=0.13 * w, y=slide_h * h, anchor='e')
        ## 层面选择
        slide_cengmian_label = tk.Label(self, text='层面', bg='white', font=('黑体', font_size3), fg='gray')
        slide_cengmian_label.place(x=0.17 * w, y=slide_h * h, anchor='e')
        self.slide_cengmian_ddl = ttk.Combobox(self, values=self.cengmian, width=17)
        self.slide_cengmian_ddl.place(x=0.17 * w, y=slide_h * h, anchor='w')
        ## f值输入
        slide_f_label = tk.Label(self, text="f'", bg='white', font=('Arial', font_size3, 'italic'), fg='gray')
        slide_f_label.place(x=0.30 * w, y=slide_h * h, anchor='e')
        f_entry = tk.Entry(self, textvariable=self.slide_f, width=10, relief='raised')
        f_entry.place(x=0.30 * w, y=slide_h * h, anchor='w')
        ## c值输入
        slide_c_label = tk.Label(self, text="c'", bg='white', font=('Arial', font_size3, 'italic'), fg='gray')
        slide_c_label.place(x=0.38 * w, y=slide_h * h, anchor='e')
        c_entry = tk.Entry(self, textvariable=self.slide_c, width=10, relief='raised')
        c_entry.place(x=0.38 * w, y=slide_h * h, anchor='w')
        ## 抗滑稳定安全系数
        K_label = tk.Label(self, text='抗滑稳定安全系数', bg='white', font=('黑体', font_size3), fg='gray')
        K_label.place(x=0.235 * w, y=(slide_h + 0.05) * h, anchor='e')
        self.K_entry = tk.Entry(self, textvariable=self.K_value, width=10, relief='raised', state='readonly')
        self.K_entry.place(x=0.235 * w, y=(slide_h + 0.05) * h, anchor='w')
        ## 抗滑稳定安全系数计算按钮
        K_value_button = tk.Button(self, text='计算', font=('黑体', font_size3), width=4, height=1, command=self.get_K_value)
        K_value_button.place(x=0.31 * w, y=(slide_h + 0.05) * h, anchor='w')

        # 清除输入按钮
        clear_entry_button = tk.Button(self, text='清除', font=('黑体', 14), width=7, height=1, command=self.clear_select_entry)
        clear_entry_button.place(x=0.39 * w, y=0.61 * h, anchor='w')
        
        # 图片显示容器框
        fig_frame0 = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.43 * w), height=int(0.6 * h))
        fig_frame0.place(x=0.52 * w, y=0.05 * h)
        ## 绘图框
        self.fig_frame = tk.Frame(self, bd=0, bg='white', relief='solid', width=int(0.428 * w), height=int(0.596 * h))
        self.fig_frame.place(x=0.521 * w, y=0.052 * h)
        fig_label = tk.Label(self, textvariable=self.fig_title_current, font=('黑体', font_size1))
        fig_label.place(x=0.735 * w, y=0.01 * h, anchor='n')
        ## 上一张按钮
        previous_fig_button = tk.Button(self, text='<', font=('黑体', font_size3), width=1, height=3, relief='groove', command=self.previous_fig)
        previous_fig_button.place(x=0.508 * w, y=0.45 * h, anchor='w')
        ## 下一张按钮
        next_fig_button = tk.Button(self, text='>', font=('黑体', font_size3), width=1, height=3, relief='groove', command=self.next_fig)
        next_fig_button.place(x=0.962 * w, y=0.45 * h, anchor='e')
        ## 图片调整容器框
        self.fig_change_frame = tk.Frame(self, bd=0, relief='solid')
        ### 小数点位数
        num_float_label = tk.Label(self.fig_change_frame, text='小数点位数', font=('黑体', font_size3), fg='gray')
        num_float_label.grid(column=0, row=0)
        self.num_float_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.num_float_entry.grid(column=0, row=1)
        ### 建基面应力集中高度
        dele_height_label = tk.Label(self.fig_change_frame, text='数据删除高度', font=('黑体', font_size3), fg='gray')
        dele_height_label.grid(column=1, row=0)
        self.dele_height_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.dele_height_entry.grid(column=1, row=1)
        ### 等值线最小值
        contour_min_label = tk.Label(self.fig_change_frame, text='等值线最小值', font=('黑体', font_size3), fg='gray')
        contour_min_label.grid(column=2, row=0)
        self.contour_min_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.contour_min_entry.grid(column=2, row=1)
        ### 等值线最大值
        contour_max_label = tk.Label(self.fig_change_frame, text='等值线最大值', font=('黑体', font_size3), fg='gray')
        contour_max_label.grid(column=3, row=0)
        self.contour_max_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.contour_max_entry.grid(column=3, row=1)
        ### 等值线间距
        contour_step_label = tk.Label(self.fig_change_frame, text='等值线间距', font=('黑体', font_size3), fg='gray')
        contour_step_label.grid(column=4, row=0)
        self.contour_step_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.contour_step_entry.grid(column=4, row=1)
        ### 重新绘制按钮
        replot_button = tk.Button(self.fig_change_frame, text='重绘', font=('黑体', font_size3), width=6, height=2, command=self.replot)
        replot_button.grid(column=5, row=0, rowspan=2)
        ## 全部导出按钮
        save_all_button = tk.Button(self, text='全部导出', font=('黑体', font_size3), width=8, height=1, command=self.save_all_figs)
        save_all_button.place(x=0.52 * w, y=0.05 * h, anchor='sw')


        # 日志容器框
        log_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.9 * w), height=int(0.2 * h))
        log_frame.place(x=0.05 * w, y=0.75 * h)
        log_label = tk.Label(self, text='日志', font=('黑体', font_size1))
        log_label.place(x=0.48 * w, y=0.7 * h)
        ## 日志文本显示框
        self.log_data_Text = tk.Text(self, width=181, height=12, bd=0)  # 日志框
        self.log_data_Text.place(x=0.052 * w, y=0.754 * h)
        ## 日志文本显示框滚动条设置
        scrollbar = tk.Scrollbar(self, command=self.log_data_Text.yview)
        scrollbar.place(x=0.937 * w, y=0.755 * h, height=0.19 * h, anchor='nw')
        self.log_data_Text.config(yscrollcommand=scrollbar.set)
        ## 日志清理按钮
        log_clear_button = tk.Button(self, text='清除', font=('黑体', font_size3), width=4, height=1, command=self.log_clear)
        log_clear_button.place(x=0.05 * w, y=0.75 * h, anchor='sw')
