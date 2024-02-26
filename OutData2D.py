import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from Combopicker import Combopicker
import os
from functions import *
import subprocess
import shutil


class OutData2D(tk.Frame):
    """二维数据导出的界面类

    Args:
        tk (tk.Frame): tkinter容器框
    """
    def __init__(self, parent, root):
        """类的初始化

        Args:
            parent (tk.Frame): 容器框
            root (PostProcessGUI): 父界面的类
        """
        super().__init__(parent)
        self.width = root.win_width  # 获取窗口宽度
        self.height = root.win_height  # 获取窗口高度
        self.mesh_path = tk.StringVar()  # 定义网格文件路径
        self.step_path = tk.StringVar()  # 定义分析步文件路径
        self.odb_path = tk.StringVar()  # 定义odb结果文件路径
        self.dam_top_node = tk.StringVar(value='输入结点编号')  # 定义坝顶结点
        self.dam_bottom_node = tk.StringVar(value='输入结点编号')  # 定义坝踵结点
        self.dam_other_node = tk.StringVar(value='输入结点编号')  # 定义其他结点
        self.dmgt_frames = tk.StringVar(value='例:1,2,3')  # 需要导出的损伤帧数
        self.Nset, self.Elset, self.Surface = [], [], []  # 初始化结点集、单元集和表面集
        self.steps = []  # 初始化分析步集合
        self.set_page()  # 页面设置


    def get_mesh_path(self):
        """选择网格文件，将路径赋值于self.mesh_path
        """
        path = tkinter.filedialog.askopenfilename(title='请选择网格文件')
        self.mesh_path.set(path)


    def get_step_path(self):
        """选择分析步文件，将路径赋值于self.step_path
        """
        path = tkinter.filedialog.askopenfilename(title='请选择分析步文件')
        self.step_path.set(path)


    def get_odb_path(self):
        """选择odb结果文件，将路径赋值于self.odb_path
        """
        path = tkinter.filedialog.askopenfilename(title='请选择odb结果文件')
        self.odb_path.set(path)


    def read_mesh_step(self):
        """读取网格和分析步文件，获取网格文件中的结点集、单元集和表面集的名称，分析步文件中的分析步名称，并更新对应的几个成员变量
        """
        if not self.mesh_path.get().endswith('.inp'):  # 判断文件格式是否正确
            self.write_log_to_Text('网格文件格式错误，请选择Abaqus的inp文件')
            self.Nset, self.Elset, self.Surface = [], [], []
        else:
            # 调用函数read_mesh读取网格文件
            self.Nset, self.Elset, self.Surface = read_mesh(self.mesh_path.get())
            self.write_log_to_Text('网格文件中共定义了%d个结点集，%d个单元集，%d个面' % (len(self.Nset), len(self.Elset), len(self.Surface)))

        if not self.step_path.get().endswith('.inp'):  # 判断文件格式是否正确
            self.write_log_to_Text('分析步文件格式错误，请选择Abaqus的inp文件')
            self.steps = []
        else:
            # 调用函数read_step函数读取分析步文件
            self.steps = read_step(self.step_path.get())
            self.write_log_to_Text('分析步文件共定义了%s个分析步' % (len(self.steps)))

        # 更新下拉选择框
        self.renew_combobox()

    
    def clear_entry(self):
        """清除选择的网格、分析步和odb结果文件
        """
        self.mesh_path.set('')
        self.step_path.set('')
        self.odb_path.set('')
        self.Nset, self.Elset, self.Surface = [], [], []
        self.steps = []
        self.dam_top_node.set('输入结点编号')
        self.dam_bottom_node.set('输入结点编号')
        self.dam_other_node.set('输入结点编号')
        self.acc_steps_ddl.delete('0', 'end')
        self.disp_Nset_ddl.delete('0', 'end')
        self.disp_Elset_ddl.delete('0', 'end')
        self.disp_Surface_ddl.delete('0', 'end')
        self.disp_steps_ddl.delete('0', 'end')
        self.disp_frames_ddl.delete('0', 'end')
        self.stre_Nset_ddl.delete('0', 'end')
        self.stre_Elset_ddl.delete('0', 'end')
        self.stre_Surface_ddl.delete('0', 'end')
        self.stre_steps_ddl.delete('0', 'end')
        self.stre_frames_ddl.delete('0', 'end')
        self.slid_Nset_ddl.delete('0', 'end')
        self.slid_Elset_ddl.delete('0', 'end')
        self.slid_Surface_ddl.delete('0', 'end')
        self.slid_steps_ddl.delete('0', 'end')
        self.slid_frames_ddl.delete('0', 'end')
        self.dmgt_Nset_ddl.delete('0', 'end')
        self.dmgt_Elset_ddl.delete('0', 'end')
        self.dmgt_Surface_ddl.delete('0', 'end')
        self.dmgt_steps_ddl.delete('0', 'end')
        self.dmgt_frames.set('例:1,2,3')
        self.renew_combobox()  # 更新下拉选择框
        self.write_log_to_Text('清除文件成功！')

    
    # 更新下拉框的选项
    def renew_combobox(self):
        """更新界面中用到结点、单元、表面和分析步集合的下拉选择框
        """
        self.disp_Nset_ddl.values = self.Nset
        self.disp_Elset_ddl.values = self.Elset
        self.disp_Surface_ddl.values = self.Surface
        self.disp_steps_ddl.values = self.steps
        self.stre_Nset_ddl.values = self.Nset
        self.stre_Elset_ddl.values = self.Elset
        self.stre_Surface_ddl.values = self.Surface
        self.stre_steps_ddl.values = self.steps
        self.slid_Nset_ddl.values = self.Nset
        self.slid_Elset_ddl.values = self.Elset
        self.slid_Surface_ddl.values = self.Surface
        self.slid_steps_ddl.values = self.steps
        self.dmgt_Nset_ddl.values = self.Nset
        self.dmgt_Elset_ddl.values = self.Elset
        self.dmgt_Surface_ddl.values = self.Surface
        self.dmgt_steps_ddl.values = self.steps
        self.acc_steps_ddl.values = self.steps


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


    def click_left(self, event, entry, text):
        """当鼠标点击输入框时，默认文本自动清除

        Args:
            event (event): 键盘鼠标事件
            entry (tk.Entry): 文本输入框
            text (string): 默认文本
        """
        if entry.get() == text:
            entry.delete('0','end')  #做这个判断，是为了避免清除用户自己输入的数据


    def move_mouse(self, event, entry, text):
        """当鼠标点击其他组件时，输入款自动显示默认文本

        Args:
            event (event): 键盘鼠标事件
            entry (tk.Entry): 文本输入框
            text (string): 默认文本
        """
        if entry.get() == '':
            entry.insert('0',text)  #做这个判断，同样是为了避免影响用户自己输入的数据


    def handler_adaptor(self, fun, **kwds):
        """中介函数进行command设置

        Args:
            fun (function): 命令对应的函数

        Returns:
            function: 命令对应的函数
        """
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)
    

    def out_data(self):
        """导出数据函数
        """
        if self.odb_path.get() != '':  # 判断是否选择了odb结果文件
            odb_dir = os.path.dirname(self.odb_path.get())  # 获取odb文件所在的文件夹
            odb_name = self.odb_path.get().split('/')[-1]  # 获取odb文件的名称
            shutil.copy('OutputOdb2D.py', os.path.join(odb_dir, 'OutputOdb2D.py'))  # 将预定义的Abaqus数据导出函数复制到odb结果文件夹
            
            # 开始写导出数据主文件代码
            with open(os.path.join(odb_dir, 'outputData.py'), 'w') as out_py:
                out_py.write('from OutputOdb2D import *\n\n\n')
                out_py.write("odb_name = '%s'\n" % odb_name)
                out_py.write('odb = session.openOdb(odb_name)\n')

                # 写导出加速度数据代码
                node_list = [self.dam_top_node.get(), self.dam_bottom_node.get(), self.dam_other_node.get()]
                if node_list[0] != '' and node_list[1] != '' and node_list[2] != '':  # 判断是否输入了三个结点的编号
                    if self.acc_steps_ddl.current_value != '':  # 判断是否选择了分析步
                        out_py.write("out_acc_data(odb, '%s', %s, 'accdata')\n" % (self.acc_steps_ddl.current_value, node_list))

                # 写导出位移数据代码
                if self.disp_steps_ddl.current_value != '':  # 判断是否选了分析步
                    steps = self.disp_steps_ddl.current_value.split(',')
                    for step in steps:
                        if self.disp_frames_ddl.current_value == '最后一帧':  # 选择最后一帧时，一般适用于静力分析步
                            # 导出结点集数据的代码
                            if self.disp_Nset_ddl.current_value != '':  # 判断是否选了结点集
                                Nsets = self.disp_Nset_ddl.current_value.split(',')
                                for nset in Nsets:
                                    fpath = 'sta-disp-' + nset
                                    out_py.write("output_disp_data_last_frame(odb, '%s', 'Nset', '%s', '%s')\n" % (nset.upper(), step, fpath))
                            # 导出单元集数据的代码
                            if self.disp_Elset_ddl.current_value != '':  # 判断是否选了单元集
                                Elsets = self.disp_Elset_ddl.current_value.split(',')
                                for elset in Elsets:
                                    fpath = 'sta-disp-' + elset
                                    out_py.write("output_disp_data_last_frame(odb, '%s', 'Elset', '%s', '%s')\n" % (elset.upper(), step, fpath))
                            # 导出表面集数据的代码
                            if self.disp_Surface_ddl.current_value != '':  # 判断是否选了表面集
                                Surfaces = self.disp_Surface_ddl.current_value.split(',')
                                for surf in Surfaces:
                                    fpath = 'sta-disp-' + surf
                                    out_py.write("output_disp_data_last_frame(odb, '%s', 'Surface', '%s', '%s')\n" % (surf.upper(), step, fpath))
                        if self.disp_frames_ddl.current_value == '所有帧':  # 选择所有帧时，适用于动力分析步
                            # 导出结点集数据的代码
                            if self.disp_Nset_ddl.current_value != '':  # 判断是否选了结点集
                                Nsets = self.disp_Nset_ddl.current_value.split(',')
                                for nset in Nsets:
                                    fpath = 'dyn-disp-' + nset
                                    out_py.write("output_disp_data_all_frame(odb, '%s', 'Nset', '%s', '%s')\n" % (nset.upper(), step, fpath))
                            # 导出单元集数据的代码
                            if self.disp_Elset_ddl.current_value != '':  # 判断是否选了单元集
                                Elsets = self.disp_Elset_ddl.current_value.split(',')
                                for elset in Elsets:
                                    fpath = 'dyn-disp-' + elset
                                    out_py.write("output_disp_data_all_frame(odb, '%s', 'Elset', '%s', '%s')\n" % (elset.upper(), step, fpath))
                            # 导出表面集数据的代码
                            if self.disp_Surface_ddl.current_value != '':  # 判断是否选了表面集
                                Surfaces = self.disp_Surface_ddl.current_value.split(',')
                                for surf in Surfaces:
                                    fpath = 'dyn-disp-' + surf
                                    out_py.write("output_disp_data_all_frame(odb, '%s', 'Surface', '%s', '%s')\n" % (surf.upper(), step, fpath))
                # 写导出应力数据代码
                if self.stre_steps_ddl.current_value != '':  # 判断是否选了分析步
                    steps = self.stre_steps_ddl.current_value.split(',')
                    for step in steps:
                        if self.stre_frames_ddl.current_value == '最后一帧':  # 选择最后一帧时，一般适用于静力分析步
                            # 导出结点集数据的代码
                            if self.stre_Nset_ddl.current_value != '':  # 判断是否选了结点集
                                Nsets = self.stre_Nset_ddl.current_value.split(',')
                                for nset in Nsets:
                                    fpath = 'sta-stre-' + nset
                                    out_py.write("output_stre_data_last_frame(odb, '%s', 'Nset', '%s', '%s')\n" % (nset.upper(), step, fpath))
                            # 导出单元集数据的代码
                            if self.stre_Elset_ddl.current_value != '':  # 判断是否选了单元集
                                Elsets = self.stre_Elset_ddl.current_value.split(',')
                                for elset in Elsets:
                                    fpath = 'sta-stre-' + elset
                                    out_py.write("output_stre_data_last_frame(odb, '%s', 'Elset', '%s', '%s')\n" % (elset.upper(), step, fpath))
                            # 导出表面集数据的代码
                            if self.stre_Surface_ddl.current_value != '':  # 判断是否选了表面集
                                Surfaces = self.stre_Surface_ddl.current_value.split(',')
                                for surf in Surfaces:
                                    fpath = 'sta-stre-' + surf
                                    out_py.write("output_stre_data_last_frame(odb, '%s', 'Surface', '%s', '%s')\n" % (surf.upper(), step, fpath))
                        if self.stre_frames_ddl.current_value == '包络帧':  # 选择了包络帧时，适用于动力分析步
                            # 导出结点集数据的代码
                            if self.stre_Nset_ddl.current_value != '':  # 判断是否选了结点集
                                Nsets = self.stre_Nset_ddl.current_value.split(',')
                                for nset in Nsets:
                                    fpath = 'dyn-stre-env-' + nset
                                    out_py.write("output_stre_data_env(odb, '%s', 'Nset', '%s', '%s')\n" % (nset.upper(), step, fpath))
                                    out_py.write('odb.close()\n')
                                    out_py.write('odb = session.openOdb(odb_name)\n')
                            # 导出单元集数据的代码
                            if self.stre_Elset_ddl.current_value != '':  # 判断是否选了单元集
                                Elsets = self.stre_Elset_ddl.current_value.split(',')
                                for elset in Elsets:
                                    fpath = 'dyn-stre-env-' + elset
                                    out_py.write("output_stre_data_env(odb, '%s', 'Elset', '%s', '%s')\n" % (elset.upper(), step, fpath))
                                    out_py.write('odb.close()\n')
                                    out_py.write('odb = session.openOdb(odb_name)\n')
                            # 导出表面集数据的代码
                            if self.stre_Surface_ddl.current_value != '':  # 判断是否选了表面集
                                Surfaces = self.stre_Surface_ddl.current_value.split(',')
                                for surf in Surfaces:
                                    fpath = 'dyn-stre-env-' + surf
                                    out_py.write("output_stre_data_env(odb, '%s', 'Surface', '%s', '%s')\n" % (surf.upper(), step, fpath))
                                    out_py.write('odb.close()\n')
                                    out_py.write('odb = session.openOdb(odb_name)\n')
                # 写导出抗滑稳定数据的代码
                if self.slid_steps_ddl.current_value != '':  # 判断是否选了分析步
                    steps = self.slid_steps_ddl.current_value.split(',')
                    for step in steps:
                        if self.slid_frames_ddl.current_value == '最后一帧':  # 选择最后一帧时，一般适用于静力分析步
                            # 导出结点集数据的代码
                            if self.slid_Nset_ddl.current_value != '':  # 判断是否选了结点集
                                Nsets = self.slid_Nset_ddl.current_value.split(',')
                                for nset in Nsets:
                                    fpath = 'sta-slid-' + nset
                                    out_py.write("output_slide_data_last_frame(odb, '%s', 'Nset', '%s', '%s')\n" % (nset.upper(), step, fpath))
                            # 导出单元集数据的代码
                            if self.slid_Elset_ddl.current_value != '':  # 判断是否选了单元集
                                Elsets = self.slid_Elset_ddl.current_value.split(',')
                                for elset in Elsets:
                                    fpath = 'sta-slid-' + elset
                                    out_py.write("output_slide_data_last_frame(odb, '%s', 'Elset', '%s', '%s')\n" % (elset.upper(), step, fpath))
                            # 导出表面集数据的代码
                            if self.slid_Surface_ddl.current_value != '':  # 判断是否选了表面集
                                Surfaces = self.slid_Surface_ddl.current_value.split(',')
                                for surf in Surfaces:
                                    fpath = 'sta-slid-' + surf
                                    out_py.write("output_slide_data_last_frame(odb, '%s', 'Surface', '%s', '%s')\n" % (surf.upper(), step, fpath))
                        if self.slid_frames_ddl.current_value == '所有帧':  # 选择所有帧时，适用于动力分析步
                            # 导出结点集数据的代码
                            if self.slid_Nset_ddl.current_value != '':  # 判断是否选了结点集
                                Nsets = self.slid_Nset_ddl.current_value.split(',')
                                for nset in Nsets:
                                    fpath = 'dyn-slid-' + nset
                                    out_py.write("output_slide_data_all_frame(odb, '%s', 'Nset', '%s', '%s')\n" % (nset.upper(), step, fpath))
                            # 导出单元集数据的代码
                            if self.slid_Elset_ddl.current_value != '':  # 判断是否选了单元集
                                Elsets = self.slid_Elset_ddl.current_value.split(',')
                                for elset in Elsets:
                                    fpath = 'dyn-slid-' + elset
                                    out_py.write("output_slide_data_all_frame(odb, '%s', 'Elset', '%s', '%s')\n" % (elset.upper(), step, fpath))
                            # 导出表面集数据的代码
                            if self.slid_Surface_ddl.current_value != '':  # 判断是否选了表面集
                                Surfaces = self.slid_Surface_ddl.current_value.split(',')
                                for surf in Surfaces:
                                    fpath = 'dyn-slid-' + surf
                                    out_py.write("output_slide_data_all_frame(odb, '%s', 'Surface', '%s', '%s')\n" % (surf.upper(), step, fpath))
                # 写导出损伤数据的代码
                if self.dmgt_steps_ddl.current_value != '':  # 判断是否选了step
                    steps = self.dmgt_steps_ddl.current_value.split(',')
                    for step in steps:
                        if self.dmgt_frames.get() != '例:1,2,3' and self.dmgt_frames.get() != '':
                            frames = self.dmgt_frames.get().split(',')
                            frames = [int(v) for v in frames]
                            # 导出结点集数据的代码
                            if self.dmgt_Nset_ddl.current_value != '':  # 判断是否选了结点集
                                Nsets = self.dmgt_Nset_ddl.current_value.split(',')
                                for nset in Nsets:
                                    fpath = 'dmgt-' + nset
                                    out_py.write("out_dmgt_data(odb, '%s', 'Nset', '%s', %s, '%s')\n" % (nset.upper(), step, frames, fpath))
                            # 导出单元集数据的代码
                            if self.dmgt_Elset_ddl.current_value != '':  # 判断是否选了单元集
                                Elsets = self.dmgt_Elset_ddl.current_value.split(',')
                                for elset in Elsets:
                                    fpath = 'dmgt-' + elset
                                    out_py.write("out_dmgt_data(odb, '%s', 'Elset', '%s', %s, '%s')\n" % (elset.upper(), step, frames, fpath))
                            # 导出表面集数据的代码
                            if self.dmgt_Surface_ddl.current_value != '':  # 判断是否选了表面集
                                Surfaces = self.dmgt_Surface_ddl.current_value.split(',')
                                for surf in Surfaces:
                                    fpath = 'dmgt-' + surf
                                    out_py.write("out_dmgt_data(odb, '%s', 'Surface', '%s', %s, '%s')\n" % (surf.upper(), step, frames, fpath))
                out_py.write('odb.close()')
                self.write_log_to_Text('导出数据代码已写入outputData.py文件')

            # 运行导出数据代码
            abq_ver = self.Abaqus_version.get()
            if abq_ver == '':
                abq_ver = 'abq2021'
            command = 'call %s cae noGUI=outputData.py' % abq_ver
            self.write_log_to_Text('导出数据开始！')
            p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=odb_dir)
            curline = p.stdout.readline()
            while (curline != b''):
                self.write_log_to_Text(curline)
                curline = p.stdout.readline()
            p.kill()
            p.wait()
            self.write_log_to_Text('导出数据完毕！')
        else:
            self.write_log_to_Text('请读取相关文件')


    def set_page(self):
        """界面设计
        """
        w = self.width  # 获取窗口宽度，简化代码
        h = self.height # 获取窗口高度，简化代码

        # 三种字体大小
        font_size1 = 16  # 框架标题
        font_size2 = 16  # 重要选项说明文字
        font_size3 = 12  # 次要文字说明

        # 二维导出数据的容器框
        out_data_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.9 * w), height=int(0.6 * h))
        out_data_frame.place(x=0.05 * w, y=0.05 * h)
        out_data_label = tk.Label(self, text='二维数据导出', font=('黑体', font_size1))
        out_data_label.place(x=0.45 * w, y=0.01 * h)

        # 网格读取组件
        mesh_label = tk.Label(self, text='网格文件', bg='white', font=('黑体', font_size2))
        mesh_label.place(x=0.15 * w, y=0.15 * h, anchor='e')
        mesh_entry = tk.Entry(self, textvariable=self.mesh_path, width=int(0.03 * w))
        mesh_entry.place(x=0.17 * w, y=0.15 * h, anchor='w')
        mesh_button = tk.Button(self, text='选择文件', command=self.get_mesh_path)
        mesh_button.place(x=0.4 * w, y=0.15 * h, anchor='w')

        # 分析步读取组件
        step_label = tk.Label(self, text='分析步文件', bg='white', font=('黑体', font_size2))
        step_label.place(x=0.15 * w, y=0.2 * h, anchor='e')
        step_entry = tk.Entry(self, textvariable=self.step_path, width=int(0.03 * w))
        step_entry.place(x=0.17 * w, y=0.2 * h, anchor='w')
        step_button = tk.Button(self, text='选择文件', command=self.get_step_path)
        step_button.place(x=0.4 * w, y=0.2 * h, anchor='w')

        # 结果读取组件
        odb_label = tk.Label(self, text='结果文件', bg='white', font=('黑体', font_size2))
        odb_label.place(x=0.15 * w, y=0.25 * h, anchor='e')
        odb_entry = tk.Entry(self, textvariable=self.odb_path, width=int(0.03 * w))
        odb_entry.place(x=0.17 * w, y=0.25 * h, anchor='w')
        odb_button = tk.Button(self, text='选择文件', command=self.get_odb_path)
        odb_button.place(x=0.4 * w, y=0.25 * h, anchor='w')

        # 读取和清除按钮
        read_button = tk.Button(self, text='读取', font=('黑体', font_size2), width=5, height=2, command=self.read_mesh_step)
        read_button.place(x=0.47 * w, y=0.175 * h, anchor='w')
        clear_buttom = tk.Button(self, text='清除', font=('黑体', font_size2), width=5, height=2, command=self.clear_entry)
        clear_buttom.place(x=0.53 * w, y=0.175 * h, anchor='w')

        # Abaqus版本选择
        Abaqus_version_label = tk.Label(self, text='Abaqus版本', bg='white', font=('Times New Roman', font_size2 - 2))
        Abaqus_version_label.place(x=0.47 * w, y=0.25 * h, anchor='w')
        self.Abaqus_version = ttk.Combobox(self, values=['abq2021', 'abq2020', 'abq2019', 'abq2018', 'abq2017', 'abq2016'], width=17)
        self.Abaqus_version.place(x=0.55 * w, y=0.25 * h, anchor='w')

        # 分割线
        canvas = tk.Canvas(self, bg='white', highlightthickness=0, width=0.6 * w, height=5)
        canvas.create_line(0, 2.5, 0.9 * w, 2.5, width=1, fill='gray', dash=(2, 2))
        canvas.place(x=0.051 * w, y=0.3 * h, anchor='w')

        # 加速度导出设置
        acc_label = tk.Label(self, text='加速度', bg='white', font=('黑体', font_size2))
        acc_label.place(x=0.15 * w, y=0.35 * h, anchor='e')
        ## 坝顶结点
        dam_top_label = tk.Label(self, text='坝顶结点:', bg='white', font=('黑体', font_size3), fg='gray')
        dam_top_label.place(x=0.23 * w, y=0.35 * h, anchor='e')
        dam_top_entry = tk.Entry(self, textvariable=self.dam_top_node, width=12, relief='raised')
        dam_top_entry.place(x=0.23 * w, y=0.35 * h, anchor='w')
        dam_top_entry.bind('<Button-1>', func=self.handler_adaptor(self.click_left, entry=dam_top_entry, text='输入结点编号'))
        ## 坝踵结点
        dam_bottom_label = tk.Label(self, text='坝踵结点:', bg='white', font=('黑体', font_size3), fg='gray')
        dam_bottom_label.place(x=0.38 * w, y=0.35 * h, anchor='e')
        dam_bottom_entry = tk.Entry(self, textvariable=self.dam_bottom_node, width=12, relief='raised')
        dam_bottom_entry.place(x=0.38 * w, y=0.35 * h, anchor='w')
        dam_bottom_entry.bind('<Button-1>', func=self.handler_adaptor(self.click_left, entry=dam_bottom_entry, text='输入结点编号'))
        ## 其他结点
        dam_other_label = tk.Label(self, text='其他结点:', bg='white', font=('黑体', font_size3), fg='gray')
        dam_other_label.place(x=0.53 * w, y=0.35 * h, anchor='e')
        dam_other_entry = tk.Entry(self, textvariable=self.dam_other_node, width=12, relief='raised')
        dam_other_entry.place(x=0.53 * w, y=0.35 * h, anchor='w')
        dam_other_entry.bind('<Button-1>', func=self.handler_adaptor(self.click_left, entry=dam_other_entry, text='输入结点编号'))
        ## 加速度导出选择分析步
        acc_steps_label = tk.Label(self, text='分析步', bg='white', font=('黑体', font_size3), fg='gray')
        acc_steps_label.place(x=0.65 * w, y=0.35 * h, anchor='e')
        self.acc_steps_ddl = Combopicker(self, values=self.steps, entrywidth=20)
        self.acc_steps_ddl.place(x=0.65 * w, y=0.35 * h, anchor='w')

        # 位移导出设置
        disp_label = tk.Label(self, text='位移', bg='white', font=('黑体', font_size2))
        disp_label.place(x=0.15 * w, y=0.4 * h, anchor='e')
        ## 结点集位移导出
        disp_Nset_label = tk.Label(self, text='结点集', bg='white', font=('黑体', font_size3), fg='gray')
        disp_Nset_label.place(x=0.21 * w, y=0.4 * h, anchor='e')
        self.disp_Nset_ddl = Combopicker(self, values=self.Nset, entrywidth=20)
        self.disp_Nset_ddl.place(x=0.21 * w, y=0.4 * h, anchor='w')
        ## 单元集位移导出
        disp_Elset_label = tk.Label(self, text='单元集', bg='white', font=('黑体', font_size3), fg='gray')
        disp_Elset_label.place(x=0.37 * w, y=0.4 * h, anchor='e')
        self.disp_Elset_ddl = Combopicker(self, values=self.Elset, entrywidth=20)
        self.disp_Elset_ddl.place(x=0.37 * w, y=0.4 * h, anchor='w')
        ## 表面集位移导出
        disp_Surface_label = tk.Label(self, text='表面集', bg='white', font=('黑体', font_size3), fg='gray')
        disp_Surface_label.place(x=0.53 * w, y=0.4 * h, anchor='e')
        self.disp_Surface_ddl = Combopicker(self, values=self.Surface, entrywidth=20)
        self.disp_Surface_ddl.place(x=0.53 * w, y=0.4 * h, anchor='w')
        ## 位移导出选择分析步
        disp_steps_label = tk.Label(self, text='分析步', bg='white', font=('黑体', font_size3), fg='gray')
        disp_steps_label.place(x=0.69 * w, y=0.4 * h, anchor='e')
        self.disp_steps_ddl = Combopicker(self, values=self.steps, entrywidth=20)
        self.disp_steps_ddl.place(x=0.69 * w, y=0.4 * h, anchor='w')
        ## 位移导出选择帧种类
        disp_frames_label = tk.Label(self, text='帧', bg='white', font=('黑体', font_size3), fg='gray')
        disp_frames_label.place(x=0.83 * w, y=0.4 * h, anchor='e')
        self.disp_frames_ddl = Combopicker(self, values=['最后一帧', '所有帧'], entrywidth=20)
        self.disp_frames_ddl.place(x=0.83 * w, y=0.4 * h, anchor='w')

        # 应力导出设置
        stre_label = tk.Label(self, text='应力', bg='white', font=('黑体', font_size2))
        stre_label.place(x=0.15 * w, y=0.45 * h, anchor='e')
        ## 结点集应力导出
        stre_Nset_label = tk.Label(self, text='结点集', bg='white', font=('黑体', font_size3), fg='gray')
        stre_Nset_label.place(x=0.21 * w, y=0.45 * h, anchor='e')
        self.stre_Nset_ddl = Combopicker(self, values=self.Nset, entrywidth=20)
        self.stre_Nset_ddl.place(x=0.21 * w, y=0.45 * h, anchor='w')
        ## 单元集应力导出
        stre_Elset_label = tk.Label(self, text='单元集', bg='white', font=('黑体', font_size3), fg='gray')
        stre_Elset_label.place(x=0.37 * w, y=0.45 * h, anchor='e')
        self.stre_Elset_ddl = Combopicker(self, values=self.Elset, entrywidth=20)
        self.stre_Elset_ddl.place(x=0.37 * w, y=0.45 * h, anchor='w')
        ## 表面集应力导出
        stre_Surface_label = tk.Label(self, text='表面集', bg='white', font=('黑体', font_size3), fg='gray')
        stre_Surface_label.place(x=0.53 * w, y=0.45 * h, anchor='e')
        self.stre_Surface_ddl = Combopicker(self, values=self.Surface, entrywidth=20)
        self.stre_Surface_ddl.place(x=0.53 * w, y=0.45 * h, anchor='w')
        ## 应力导出选择分析步
        stre_steps_label = tk.Label(self, text='分析步', bg='white', font=('黑体', font_size3), fg='gray')
        stre_steps_label.place(x=0.69 * w, y=0.45 * h, anchor='e')
        self.stre_steps_ddl = Combopicker(self, values=self.steps, entrywidth=20)
        self.stre_steps_ddl.place(x=0.69 * w, y=0.45 * h, anchor='w')
        ## 应力导出选择帧种类
        stre_frames_label = tk.Label(self, text='帧', bg='white', font=('黑体', font_size3), fg='gray')
        stre_frames_label.place(x=0.83 * w, y=0.45 * h, anchor='e')
        self.stre_frames_ddl = Combopicker(self, values=['最后一帧', '包络帧'], entrywidth=20)
        self.stre_frames_ddl.place(x=0.83 * w, y=0.45 * h, anchor='w')

        # 抗滑稳定导出设置
        slid_label = tk.Label(self, text='抗滑稳定', bg='white', font=('黑体', font_size2))
        slid_label.place(x=0.15 * w, y=0.5 * h, anchor='e')
        ## 结点集抗滑稳定导出
        slid_Nset_label = tk.Label(self, text='结点集', bg='white', font=('黑体', font_size3), fg='gray')
        slid_Nset_label.place(x=0.21 * w, y=0.5 * h, anchor='e')
        self.slid_Nset_ddl = Combopicker(self, values=self.Nset, entrywidth=20)
        self.slid_Nset_ddl.place(x=0.21 * w, y=0.5 * h, anchor='w')
        ## 单元集抗滑稳定导出
        slid_Elset_label = tk.Label(self, text='单元集', bg='white', font=('黑体', font_size3), fg='gray')
        slid_Elset_label.place(x=0.37 * w, y=0.5 * h, anchor='e')
        self.slid_Elset_ddl = Combopicker(self, values=self.Elset, entrywidth=20)
        self.slid_Elset_ddl.place(x=0.37 * w, y=0.5 * h, anchor='w')
        ## 表面集抗滑稳定导出
        slid_Surface_label = tk.Label(self, text='表面集', bg='white', font=('黑体', font_size3), fg='gray')
        slid_Surface_label.place(x=0.53 * w, y=0.5 * h, anchor='e')
        self.slid_Surface_ddl = Combopicker(self, values=self.Surface, entrywidth=20)
        self.slid_Surface_ddl.place(x=0.53 * w, y=0.5 * h, anchor='w')
        ## 抗滑稳定导出选择分析步
        slid_steps_label = tk.Label(self, text='分析步', bg='white', font=('黑体', font_size3), fg='gray')
        slid_steps_label.place(x=0.69 * w, y=0.5 * h, anchor='e')
        self.slid_steps_ddl = Combopicker(self, values=self.steps, entrywidth=20)
        self.slid_steps_ddl.place(x=0.69 * w, y=0.5 * h, anchor='w')
        ## 抗滑稳定导出选择帧种类
        slid_frames_label = tk.Label(self, text='帧', bg='white', font=('黑体', font_size3), fg='gray')
        slid_frames_label.place(x=0.83 * w, y=0.5 * h, anchor='e')
        self.slid_frames_ddl = Combopicker(self, values=['最后一帧', '所有帧'], entrywidth=20)
        self.slid_frames_ddl.place(x=0.83 * w, y=0.5 * h, anchor='w')

        # 损伤导出设置
        dmgt_label = tk.Label(self, text='损伤因子', bg='white', font=('黑体', font_size2))
        dmgt_label.place(x=0.15 * w, y=0.55 * h, anchor='e')
        ## 结点集损伤导出
        dmgt_Nset_label = tk.Label(self, text='结点集', bg='white', font=('黑体', font_size3), fg='gray')
        dmgt_Nset_label.place(x=0.21 * w, y=0.55 * h, anchor='e')
        self.dmgt_Nset_ddl = Combopicker(self, values=self.Nset, entrywidth=20)
        self.dmgt_Nset_ddl.place(x=0.21 * w, y=0.55 * h, anchor='w')
        ## 单元集损伤导出
        dmgt_Elset_label = tk.Label(self, text='单元集', bg='white', font=('黑体', font_size3), fg='gray')
        dmgt_Elset_label.place(x=0.37 * w, y=0.55 * h, anchor='e')
        self.dmgt_Elset_ddl = Combopicker(self, values=self.Elset, entrywidth=20)
        self.dmgt_Elset_ddl.place(x=0.37 * w, y=0.55 * h, anchor='w')
        ## 表面集损伤导出
        dmgt_Surface_label = tk.Label(self, text='表面集', bg='white', font=('黑体', font_size3), fg='gray')
        dmgt_Surface_label.place(x=0.53 * w, y=0.55 * h, anchor='e')
        self.dmgt_Surface_ddl = Combopicker(self, values=self.Surface, entrywidth=20)
        self.dmgt_Surface_ddl.place(x=0.53 * w, y=0.55 * h, anchor='w')
        ## 损伤导出选择分析步
        dmgt_steps_label = tk.Label(self, text='分析步', bg='white', font=('黑体', font_size3), fg='gray')
        dmgt_steps_label.place(x=0.69 * w, y=0.55 * h, anchor='e')
        self.dmgt_steps_ddl = Combopicker(self, values=self.steps, entrywidth=20)
        self.dmgt_steps_ddl.place(x=0.69 * w, y=0.55 * h, anchor='w')
        ## 损伤导出选择帧
        dmgt_frames_label = tk.Label(self, text='帧', bg='white', font=('黑体', font_size3), fg='gray')
        dmgt_frames_label.place(x=0.83 * w, y=0.55 * h, anchor='e')
        dmgt_frames_entry = tk.Entry(self, textvariable=self.dmgt_frames, width=14, font=('Time New Roman', 14), highlightcolor='lightblue', relief='solid')
        dmgt_frames_entry.bind('<Button-1>', func=self.handler_adaptor(self.click_left, entry=dmgt_frames_entry, text='例:1,2,3'))
        dmgt_frames_entry.place(x=0.83 * w, y=0.55 * h, anchor='w')

        # 数据导出按钮
        output_button = tk.Button(self, text='导出数据', font=('黑体', 30), width=10, height=2, command=self.out_data)
        output_button.place(x=0.77 * w, y=0.22 * h, anchor='w')

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
        