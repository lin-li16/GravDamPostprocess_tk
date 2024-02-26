import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from Combopicker import Combopicker
import os
from functions import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import warnings
warnings.filterwarnings("ignore")

from postprocess3D import *


class Static3D(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.width = root.win_width  # 获取窗口宽度
        self.height = root.win_height  # 获取窗口高度
        self.odb_path = tk.StringVar()  # 定义odb结果文件路径
        self.mesh_path = tk.StringVar()  # 定义网格文件路径
        self.geo_path = tk.StringVar()  # 定义几何文件夹路径
        self.csv_flist = []  # 初始化结果文件列表
        self.Nset, self.Elset, self.Surface = [], [], []  # 初始化结点集、单元集和表面集
        self.coord_all = {}  # 初始化局部坐标系字典
        self.bounds = []  # 初始化边界列表
        self.areas = []  # 初始化面积文件列表
        self.holes = []  # 初始化孔洞列表
        self.concens = []  # 初始化应力集中点列表
        self.nodes = None  # 初始化结点坐标
        self.copen_data = []  # 初始化横缝开度数据，从.dat文件中读取
        self.copen_id = []  # 初始化横缝开度数据标签，从.dat文件中读取，与copen_data对应
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


    def get_geo_path(self):
        """选择几何信息文件夹，将路径赋值于self.geo_path
        """
        path = tkinter.filedialog.askdirectory(title='请选择几何信息文件夹')
        self.geo_path.set(path)


    def read_mesh_geo(self):
        """读取网格文件、几何文件夹和横缝数据文件，获取后面需要的数据
        """
        if not self.odb_path.get().endswith('.odb'):  # 判断结果文件格式是否正确
            self.write_log_to_Text('结果文件格式错误，请选择Abaqus的odb文件')
        else:
            odb_dir = os.path.dirname(self.odb_path.get())  # 获取odb文件所在的文件夹
            self.csv_flist = find_csv_file(odb_dir)  # 获取绘图用的数据文件，格式为.csv
            dat_path = self.odb_path.get().replace('.odb', '.dat')
            if os.path.exists(dat_path):
                self.copen_data, self.copen_id = read_joint_dat_sta(dat_path)  # 读取横缝数据
        if not self.mesh_path.get().endswith('.inp'):  # 判断文件格式是否正确
            self.write_log_to_Text('网格文件格式错误，请选择Abaqus的inp文件')
            self.Nset, self.Elset, self.Surface = [], [], []
            self.nodes = None
        else:
            self.nodes = read_nodes(self.mesh_path.get(), dims=3)  # 读取所有结点坐标
            self.Nset, self.Elset, self.Surface = read_mesh(self.mesh_path.get())  # 读取所有集合
            self.coord_all = read_coordinate(self.mesh_path.get())  # 读取所有局部坐标系
            self.write_log_to_Text('网格文件中共定义了%d个结点，%d个结点集，%d个单元集，%d个面，%d个局部坐标系' % (self.nodes.shape[0], len(self.Nset), len(self.Elset), len(self.Surface), len(self.coord_all)))
        if self.geo_path.get() == '':  # 判断是否输入了几何信息文件夹
            self.write_log_to_Text('请选择几何信息文件夹')
        else:
            self.bounds, self.areas, self.holes, self.concens = find_geo_file(self.geo_path.get())  # 读取几何信息文件，包括边界文件、面积文件、孔洞文件、应力集中点文件
            self.write_log_to_Text('共读取了%d个边界文件，%d个面积文件，%d个孔洞文件，%d个应力集中区域文件' % (len(self.bounds), len(self.areas), len(self.holes), len(self.concens)))

        # 更新下拉选择框
        self.renew_combobox()

    
    def get_K_value(self):
        """计算抗滑稳定安全系数
        """
        if self.odb_path.get() == '':  # 检查是否选了odb文件
            self.write_log_to_Text('没有选择结果文件，请读取结果文件')
        else:
            odb_dir = os.path.dirname(self.odb_path.get())  # 获取odb文件所在的文件夹
            plane1 = self.slide_plane1_ddl.get()  # 获取滑面1名称
            plane2 = self.slide_plane2_ddl.get()  # 获取滑面2名称
            if plane1 != '' and plane2 != '': 
                stre_data1 = get_stre_data(os.path.join(odb_dir, 'sta-slid-%s.csv' % plane1))  # 读取滑面1的应力数据
                stre_data2 = get_stre_data(os.path.join(odb_dir, 'sta-slid-%s.csv' % plane2))  # 读取滑面2的应力数据
                for key in self.coord_all.keys():
                    if plane1[3:] in key:
                        coord1 = self.coord_all[key]  # 获取滑面1的局部坐标系
                    if plane2[3:] in key:
                        coord2 = self.coord_all[key]  # 获取滑面2的局部坐标系
                for name in self.areas:
                    if plane1[3:] in name:
                        area1 = os.path.join(self.geo_path.get(), name) # 获取滑面1的面积文件
                    if plane2[3:] in name:
                        area2 = os.path.join(self.geo_path.get(), name)  # 获取滑面2的面积文件
                f1, c1 = float(self.f1_entry.get()), float(self.c1_entry.get())  # 获取滑面1的f,c值
                f2, c2 = float(self.f2_entry.get()), float(self.c2_entry.get())  # 获取滑面2的f,c值
                _, _, vec_n1 = get_vec_xyz(coord1, self.nodes)  # 获取滑面1的法向量
                _, _, vec_n2 = get_vec_xyz(coord2, self.nodes)  # 获取滑面2的法向量
                vec_t = np.cross(vec_n1, vec_n2)  # 获取滑动向量，与两个法向量垂直
                area_data1 = np.loadtxt(area1, skiprows=19, encoding='gbk')  # 求滑面1的结点面积数据
                area_data2 = np.loadtxt(area2, skiprows=19, encoding='gbk')  # 求滑面2的结点面积数据
                # 求抗滑稳定安全系数
                KK = kanghua3D_2P_static(stre_data1, stre_data2, area_data1, area_data2, vec_n1, vec_n2, vec_t, f=[f1, f2], c=[c1, c2])
                self.K_value.set('%.3f' % KK)
                self.write_log_to_Text('抗滑稳定安全系数计算完成')
            else:
                self.write_log_to_Text('没有找到抗滑稳定数据')

    
    def clear_file_entry(self):
        """清除选择的网格、分析步和odb结果文件
        """
        self.mesh_path.set('')
        self.odb_path.set('')
        self.geo_path.set('')
        self.Nset, self.Elset, self.Surface = [], [], []
        self.coord_all = {}  #初始化所有局部坐标系
        self.bounds = []  # 初始化边界列表
        self.areas = []  # 初始化所有结点面积列表
        self.holes = []  # 初始化孔洞列表
        self.concens = []  # 初始化应力集中点列表
        self.csv_flist = []  # 初始化所有结果文件列表
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
        self.disp_section_ddl.delete('0', 'end')
        self.stre_section_ddl.delete('0', 'end')
        self.stre_comp_ddl.delete('0', 'end')
        self.joint_section_ddl.delete('0', 'end')
        self.dmgt_section_ddl.delete('0', 'end')
        self.slide_plane1_ddl.delete('0', 'end')
        self.f1_entry.delete('0', 'end')
        self.c1_entry.delete('0', 'end')
        self.slide_plane2_ddl.delete('0', 'end')
        self.f2_entry.delete('0', 'end')
        self.c2_entry.delete('0', 'end')
        self.K_value.set('')
        self.write_log_to_Text('清除输入框成功')

    
    # 更新下拉框的选项
    def renew_combobox(self):
        """更新界面中用到结点、单元、表面和分析步集合的下拉选择框
        """
        # 更新位移相关的下拉选择框
        disp_sec = []
        for f in self.csv_flist:  # 根据odb文件夹中存在的位移数据来获取剖面
            if 'sta-disp-' in f:
                disp_sec.append(f.replace('sta-disp-', '').replace('.csv', ''))
        if len(disp_sec) > 1:
            disp_sec.append('全选')
        self.disp_section_ddl.values = disp_sec
        # 更新应力相关的下拉选择框
        stre_sec = []
        for f in self.csv_flist:  # 根据odb文件夹中存在的应力数据来获取剖面
            if 'sta-stre-' in f:
                stre_sec.append(f.replace('sta-stre-', '').replace('.csv', ''))
        if len(stre_sec) > 1:
            stre_sec.append('全选')
        self.stre_section_ddl.values = stre_sec
        # 更新横缝相关的下拉选择框
        joint_sec = []
        for name in self.Nset:
            if '-X1' in name and 'baduan' in name:
                joint_sec.append(name.replace('-X1', ''))
        if len(joint_sec) > 1:
            joint_sec.append('全选')
        self.joint_section_ddl.values = joint_sec
        # 更新损伤因子相关的下拉选择框
        dmgt_sec = []
        for f in self.csv_flist:
            if 'dmgt-' in f:
                f = f.split('_')[0].replace('dmgt-', '')
                if f not in dmgt_sec:
                    dmgt_sec.append(f)
        if len(dmgt_sec) > 1:
            dmgt_sec.append('全选')
        self.dmgt_section_ddl.values = dmgt_sec
        # 更新抗滑稳定相关的下拉选择框
        slide_plane = []
        for f in self.csv_flist:
            if 'sta-slid-' in f:
                slide_plane.append(f.replace('sta-slid-', '').replace('.csv', ''))
        slide_coord = []
        for f in self.coord_all.keys():
            if 'huakuai' in f:
                slide_coord.append(f)
        self.slide_plane1_ddl['value'] = slide_plane
        self.slide_plane2_ddl['value'] = slide_plane


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
                if self.geo_path is None:  # 检查是否读取了边界信息
                    self.write_log_to_Text('没有几何信息，请读取几何文件')
                else:
                    # 位移等值线图的绘制
                    disp_sec = self.disp_section_ddl.current_value  # 读取剖面
                    disp_direc = self.disp_direc_ddl.current_value  # 读取方向
                    if disp_sec != '' and disp_direc != '':
                        disp_sec = disp_sec.split(',')
                        disp_direc = disp_direc.split(',')
                        for sec in disp_sec:
                            if sec != '全选':
                                fname = os.path.join(odb_dir, 'sta-disp-%s.csv' % sec)
                                if 'downstream' in sec:  # 下游面的局部坐标系
                                    coordinate_nodes = np.array([[-1, 0, 0], [0, 0, 1], [0, 0, 0]])
                                elif 'upstream' in sec:  # 上游面的局部坐标系
                                    coordinate_nodes = np.array([[1, 0, 0], [0, 0, 1], [0, 0, 0]])
                                else:  # 其他剖面的局部坐标系
                                    coordinate_nodes = self.coord_all[sec]
                                # 获取剖面的边界文件
                                bounds = []
                                for key in self.bounds:
                                    if sec in key:
                                        bounds.append(os.path.join(self.geo_path.get(), key))
                                # 获取剖面的孔洞文件，没有则为None
                                holes = None
                                for key in self.holes:
                                    if sec in key:
                                        holes = os.path.join(self.geo_path.get(), key)
                                for direc in disp_direc:
                                    if direc != '全选':
                                        if len(bounds) > 0:  # 绘图
                                            fig, xx, yy, zz, bds, hls, ccs = sta_disp_contour(fname, coordinate_nodes, bounds, self.nodes, direc, holes)
                                            self.figs.append(fig)
                                            self.figs_data.append([xx, yy, zz, bds, hls, ccs, coordinate_nodes])
                                            self.figs_type.append('contour')
                                            self.fig_title.append('%s剖面%s向位移等值线图(cm)' % (sec, direc))
                                        else:
                                            self.write_log_to_Text('没有找到%s剖面的边界文件')
                    
                    # 应力等值线图的绘制
                    stre_sec = self.stre_section_ddl.current_value  # 读取剖面
                    stre_comp = self.stre_comp_ddl.current_value  # 去读应力分量
                    if stre_sec != '' and stre_comp != '':
                        stre_sec = stre_sec.split(',')
                        stre_comp = stre_comp.split(',')
                        for sec in stre_sec:
                            if sec != '全选':
                                fname = os.path.join(odb_dir, 'sta-stre-%s.csv' % sec)
                                if 'downstream' in sec:  # 下游面的局部坐标系
                                    coordinate_nodes = np.array([[-1, 0, 0], [0, 0, 1], [0, 0, 0]])
                                elif 'upstream' in sec:  # 上游面的局部坐标系
                                    coordinate_nodes = np.array([[1, 0, 0], [0, 0, 1], [0, 0, 0]])
                                else:  # 其他剖面的局部坐标系
                                    coordinate_nodes = self.coord_all[sec]
                                # 获取剖面的边界文件
                                bounds = []
                                for key in self.bounds:
                                    if sec in key:
                                        bounds.append(os.path.join(self.geo_path.get(), key))
                                # 获取剖面的孔洞文件，没有则为None
                                holes = None
                                for key in self.holes:
                                    if sec in key:
                                        holes = os.path.join(self.geo_path.get(), key)
                                # 获取剖面的应力集中区域文件，没有则为None
                                concen = None
                                for key in self.concens:
                                    if sec in key:
                                        concen = os.path.join(self.geo_path.get(), key)
                                for comp in stre_comp:
                                    if comp != '全选':
                                        if comp == '大主应力':
                                            comp_label = 'Smax'
                                        if comp == '小主应力':
                                            comp_label = 'Smin'
                                        if len(bounds) > 0:  # 绘图
                                            fig, xx, yy, zz, bds, hls, ccs = sta_stre_contour(fname, coordinate_nodes, bounds, self.nodes, comp_label, holes, concen=concen, concen_dist=0.01)
                                            self.figs.append(fig)
                                            self.figs_data.append([xx, yy, zz, bds, hls, ccs, coordinate_nodes])
                                            self.figs_type.append('contour')
                                            self.fig_title.append('%s剖面%s等值线图(MPa)' % (sec, comp))
                                        else:
                                            self.write_log_to_Text('没有找到%s剖面的边界文件')
                    # 横缝开度等值线图的绘制
                    joint_sec = self.joint_section_ddl.current_value  # 获取横缝
                    if joint_sec != '' :
                        joint_sec = joint_sec.split(',')
                        for sec in joint_sec:
                            if sec != '全选':
                                bounds = os.path.join(self.geo_path.get(), 'bound-%s-X1.out' % sec)  # 获取横缝边界
                                coordinate = self.coord_all[sec]  # 获取横缝局部坐标系
                                joint = sec + '-X1'
                                fig, xx, yy, zz, bds, hls, ccs = sta_joint_contour(joint, bounds, coordinate, self.copen_data, self.copen_id, self.nodes)
                                self.figs.append(fig)
                                self.figs_data.append([xx, yy, zz, bds, hls, ccs, coordinate])
                                self.figs_type.append('contour')
                                self.fig_title.append('%s横缝开度等值线图' % sec)
                  
                    # 损伤因子分布图的绘制
                    dmgt_sec = self.dmgt_section_ddl.current_value  # 获取剖面
                    if dmgt_sec != '':
                        dmgt_sec = dmgt_sec.split(',')
                        for sec in dmgt_sec:
                            if sec != '全选':
                                flist = os.listdir(odb_dir)
                                for f in flist:
                                    if 'dmgt' in f and sec in f and f.endswith('.csv'):
                                        fname = os.path.join(odb_dir, f)
                                        frame = f.split('_')[-1].replace('.csv', '')
                                        if 'downstream' in sec:  # 下游面的局部坐标系
                                            coordinate_nodes = np.array([[-1, 0, 0], [0, 0, 1], [0, 0, 0]])
                                        elif 'upstream' in sec:  # 上游面的局部坐标系
                                            coordinate_nodes = np.array([[1, 0, 0], [0, 0, 1], [0, 0, 0]])
                                        else:  # 其他剖面的局部坐标系
                                            coordinate_nodes = self.coord_all[sec]
                                        # 获取剖面边界文件
                                        bounds = []
                                        for key in self.bounds:
                                            if sec in key:
                                                bounds.append(os.path.join(self.geo_path.get(), key))
                                        # 获取剖面孔洞文件，没有则为None
                                        holes = None
                                        for key in self.holes:
                                            if sec in key:
                                                holes = os.path.join(self.geo_path.get(), key)
                                        if len(bounds) > 0:  # 绘图
                                            if 'upstream' in sec or 'downstream' in sec:
                                                fig, xx, yy, zz = dmgt_contour(fname, coordinate_nodes, bounds, self.nodes, holes=holes, cbar_ratio=0.5)
                                            else:
                                                fig, xx, yy, zz = dmgt_contour(fname, coordinate_nodes, bounds, self.nodes, holes=holes)
                                            self.figs.append(fig)
                                            self.figs_data.append([xx, yy, zz])
                                            self.figs_type.append('contourf')
                                            self.fig_title.append('%s剖面第%s帧损伤因子分布图图' % (sec, frame))
                                        else:
                                            self.write_log_to_Text('没有找到%s剖面的边界文件')
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
        self.fig_canvas = FigureCanvasTkAgg(self.current_fig, self.fig_frame)  # 创建图片画布
        self.fig_canvas.draw()  # 绘制
        self.fig_canvas.get_tk_widget().pack(side='bottom')  # 调整图片显示位置
        self.toolbar = NavigationToolbar2Tk(self.fig_canvas, self.fig_frame)  # 创建图片工具栏
        self.toolbar.update()
        self.fig_title_current.set(self.fig_title[self.figs.index(self.current_fig)])
        if self.figs_type[self.figs.index(self.current_fig)] == 'contour':
            if not self.fig_change_frame.winfo_ismapped():
                self.fig_change_frame.place(x=0.564 * self.width, y=0.66 * self.height)
        else:
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
        idx = self.figs.index(self.current_fig)  # 获取当前图片的索引
        fig_data = self.figs_data[idx]  # 获取当前图片的数据
        num_float = 1  # 等值线数值小数点位数默认值
        dele_height = 0  # 删除数据区域高度的默认值
        num_line = 10  # 等值线条数默认值
        con_dist = 0  # 集中点距离
        max_min = 'abs'  # 显示最大最小值的默认值
        contour_max = np.max(fig_data[2])  # 等值线的默认最大值
        contour_min = np.min(fig_data[2])  # 等值线的默认最小值
        if '大主应力' in self.fig_title_current.get():  # 大主应力图必须显示最大值
            max_min = 'max'
        if self.num_float_entry.get() != '':  # 根据输入框更新小数点位数
            num_float = int(self.num_float_entry.get())
        if self.dele_height_entry.get() != '':  # 根据输入框更新删除数据区域高度
            dele_height = float(self.dele_height_entry.get())
        if self.concen_dist_entry.get() != '':  # 根据输入框更新集中点距离
            con_dist = float(self.concen_dist_entry.get())
        if self.contour_step_entry.get() != '':  # 根据输入框更新等值线间距，以及等值线最大最小值
            contour_step = float(self.contour_step_entry.get())
            if self.contour_min_entry.get() != '' and self.contour_max_entry.get() != '':
                contour_min = float(self.contour_min_entry.get())
                contour_max = float(self.contour_max_entry.get())
                num_line = np.arange(contour_min, contour_max, contour_step)
            if self.contour_min_entry.get() == '' and self.contour_max_entry.get() != '':
                contour_max = float(self.contour_max_entry.get())
                num_line = np.arange(contour_min, contour_max, contour_step)
            if self.contour_min_entry.get() != '' and self.contour_max_entry.get() == '':
                contour_min = float(self.contour_min_entry.get())
                num_line = np.arange(contour_min, contour_max, contour_step)
            else:
                num_line = np.arange(contour_min, contour_max, contour_step)
        xx, yy, zz = fig_data[0], fig_data[1], fig_data[2]
        # 如果应力集中区域不为None
        if fig_data[5] is not None:  
            concen_nodes = np.loadtxt(fig_data[5])
            concen_coord = change_coord(fig_data[6], concen_nodes, self.nodes)
            xx_dele, yy_dele, zz_dele = [], [], []
            for i in range(len(xx)):
                dist = np.sqrt((concen_coord[:, 0] - xx[i]) ** 2 + (concen_coord[:, 1] - yy[i]) ** 2)
                if np.min(dist) > con_dist:
                    xx_dele.append(xx[i])
                    yy_dele.append(yy[i])
                    zz_dele.append(zz[i])
            xx = np.array(xx_dele)
            yy = np.array(yy_dele)
            zz = np.array(zz_dele)
        # 重新绘制图片
        fig = plt.figure(figsize=(6.1, 4.4))
        for boundary in fig_data[3]:
            if dele_height > 0 and con_dist > 0:  # 如果存在去除部分结点数据的情况，则采用外插
                _, _, _, _ = getContour(xx, yy, zz, boundary, holes=fig_data[4], dpi=100, Extrapolation=1, num_float=num_float, baseP=dele_height, numline=num_line, max_min=max_min)
            else:
                X, Y, ZS, hd = getContour(xx, yy, zz, boundary, holes=fig_data[4], dpi=100, Extrapolation=0, num_float=num_float, baseP=dele_height, numline=num_line, max_min=max_min)
        plt.tight_layout()
        self.figs[idx] = fig
        self.current_fig = self.figs[idx]
        self.update_fig()
        self.write_log_to_Text('重绘成功')


    def save_all_figs(self):
        """保存图框中的所有图片
        """
        if self.odb_path.get() == '':  # 检查是否选了odb文件
            self.write_log_to_Text('没有选择结果文件，请读取结果文件')
        else:
            odb_dir = os.path.dirname(self.odb_path.get())  # 获取odb文件所在的文件夹
            fig_dir = os.path.join(odb_dir, 'figures')
            if not os.path.exists(fig_dir):
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

        # 三维静力功能容器框
        func_frame = tk.Frame(self, bd=1, bg='white', relief='solid', width=int(0.42 * w), height=int(0.6 * h))
        func_frame.place(x=0.05 * w, y=0.05 * h)
        func_label = tk.Label(self, text='三维静力处理', font=('黑体', font_size1))
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

        # 几何文件夹读取组件
        geo_label = tk.Label(self, text='几何信息', bg='white', font=('黑体', font_size2))
        geo_label.place(x=0.13 * w, y=0.2 * h, anchor='e')
        geo_entry = tk.Entry(self, textvariable=self.geo_path, width=int(0.025 * w))
        geo_entry.place(x=0.14 * w, y=0.2 * h, anchor='w')
        geo_button = tk.Button(self, text='选择文件夹', command=self.get_geo_path)
        geo_button.place(x=0.33 * w, y=0.2 * h, anchor='w')

        # 读取和清除按钮
        read_button = tk.Button(self, text='读取', font=('黑体', 14), width=7, height=2, command=self.read_mesh_geo)
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
        disp_h = 0.29
        disp_label = tk.Label(self, text='位移', bg='white', font=('黑体', font_size2))
        disp_label.place(x=0.13 * w, y=disp_h * h, anchor='e')
        ## 剖面选择
        disp_section_label = tk.Label(self, text='剖面', bg='white', font=('黑体', font_size3), fg='gray')
        disp_section_label.place(x=0.17 * w, y=disp_h * h, anchor='e')
        self.disp_section_ddl = Combopicker(self, values=[], entrywidth=20)
        self.disp_section_ddl.place(x=0.17 * w, y=disp_h * h, anchor='w')
        ## 方向选择
        disp_direc_label = tk.Label(self, text='方向', bg='white', font=('黑体', font_size3), fg='gray')
        disp_direc_label.place(x=0.31 * w, y=disp_h * h, anchor='e')
        self.disp_direc_ddl = Combopicker(self, values=['X', 'Y', 'Z', '全选'], entrywidth=20)
        self.disp_direc_ddl.place(x=0.31 * w, y=disp_h * h, anchor='w')

        # 应力导出设置
        stre_h = 0.35
        stre_label = tk.Label(self, text='应力', bg='white', font=('黑体', font_size2))
        stre_label.place(x=0.13 * w, y=stre_h * h, anchor='e')
        ## 剖面选择
        stre_section_label = tk.Label(self, text='剖面', bg='white', font=('黑体', font_size3), fg='gray')
        stre_section_label.place(x=0.17 * w, y=stre_h * h, anchor='e')
        self.stre_section_ddl = Combopicker(self, values=[], entrywidth=20)
        self.stre_section_ddl.place(x=0.17 * w, y=stre_h * h, anchor='w')
        ## 分量选择
        stre_comp_label = tk.Label(self, text='分量', bg='white', font=('黑体', font_size3), fg='gray')
        stre_comp_label.place(x=0.31 * w, y=stre_h * h, anchor='e')
        self.stre_comp_ddl = Combopicker(self, values=['大主应力', '小主应力', '全选'], entrywidth=20)
        self.stre_comp_ddl.place(x=0.31 * w, y=stre_h * h, anchor='w')

        # 横缝导出设置
        joint_h = 0.41
        joint_label = tk.Label(self, text='横缝', bg='white', font=('黑体', font_size2))
        joint_label.place(x=0.13 * w, y=joint_h * h, anchor='e')
        ## 剖面选择
        joint_section_label = tk.Label(self, text='横缝', bg='white', font=('黑体', font_size3), fg='gray')
        joint_section_label.place(x=0.17 * w, y=joint_h * h, anchor='e')
        self.joint_section_ddl = Combopicker(self, values=[], entrywidth=20)
        self.joint_section_ddl.place(x=0.17 * w, y=joint_h * h, anchor='w')

        # 损伤因子导出设置
        dmgt_h = 0.47
        dmgt_label = tk.Label(self, text='损伤因子', bg='white', font=('黑体', font_size2))
        dmgt_label.place(x=0.13 * w, y=dmgt_h * h, anchor='e')
        ## 剖面选择
        dmgt_section_label = tk.Label(self, text='剖面', bg='white', font=('黑体', font_size3), fg='gray')
        dmgt_section_label.place(x=0.17 * w, y=dmgt_h * h, anchor='e')
        self.dmgt_section_ddl = Combopicker(self, values=[], entrywidth=20)
        self.dmgt_section_ddl.place(x=0.17 * w, y=dmgt_h * h, anchor='w')

        # 抗滑稳定导出设置
        slide_h = 0.53
        slide_label = tk.Label(self, text='抗滑稳定', bg='white', font=('黑体', font_size2))
        slide_label.place(x=0.13 * w, y=slide_h * h, anchor='e')
        ## 滑面1选择
        slide_plane1_label = tk.Label(self, text='滑面1', bg='white', font=('黑体', font_size3), fg='gray')
        slide_plane1_label.place(x=0.17 * w, y=slide_h * h, anchor='e')
        self.slide_plane1_ddl = ttk.Combobox(self, values=[], width=17)
        self.slide_plane1_ddl.place(x=0.17 * w, y=slide_h * h, anchor='w')
        ### f值输入
        slide_f1_label = tk.Label(self, text="f'", bg='white', font=('Arial', font_size3, 'italic'), fg='gray')
        slide_f1_label.place(x=0.29 * w, y=slide_h * h, anchor='e')
        self.f1_entry = tk.Entry(self, textvariable='', width=10, relief='raised')
        self.f1_entry.place(x=0.295 * w, y=slide_h * h, anchor='w')
        ### c值输入
        slide_c1_label = tk.Label(self, text="c'", bg='white', font=('Arial', font_size3, 'italic'), fg='gray')
        slide_c1_label.place(x=0.37 * w, y=slide_h * h, anchor='e')
        self.c1_entry = tk.Entry(self, textvariable='', width=10, relief='raised')
        self.c1_entry.place(x=0.375 * w, y=slide_h * h, anchor='w')
        ## 滑面2选择
        slide_plane2_label = tk.Label(self, text='滑面2', bg='white', font=('黑体', font_size3), fg='gray')
        slide_plane2_label.place(x=0.17 * w, y=(slide_h + 0.04) * h, anchor='e')
        self.slide_plane2_ddl = ttk.Combobox(self, values=[], width=17)
        self.slide_plane2_ddl.place(x=0.17 * w, y=(slide_h + 0.04) * h, anchor='w')
        ### f值输入
        slide_f2_label = tk.Label(self, text="f'", bg='white', font=('Arial', font_size3, 'italic'), fg='gray')
        slide_f2_label.place(x=0.29 * w, y=(slide_h + 0.04) * h, anchor='e')
        self.f2_entry = tk.Entry(self, textvariable='', width=10, relief='raised')
        self.f2_entry.place(x=0.295 * w, y=(slide_h + 0.04) * h, anchor='w')
        ### c值输入
        slide_c2_label = tk.Label(self, text="c'", bg='white', font=('Arial', font_size3, 'italic'), fg='gray')
        slide_c2_label.place(x=0.37 * w, y=(slide_h + 0.04) * h, anchor='e')
        self.c2_entry = tk.Entry(self, textvariable='', width=10, relief='raised')
        self.c2_entry.place(x=0.375 * w, y=(slide_h + 0.04) * h, anchor='w')
        ## 抗滑稳定安全系数
        K_label = tk.Label(self, text='抗滑稳定安全系数', bg='white', font=('黑体', font_size3), fg='gray')
        K_label.place(x=0.24 * w, y=(slide_h + 0.08) * h, anchor='e')
        self.K_entry = tk.Entry(self, textvariable=self.K_value, width=10, relief='raised', state='readonly')
        self.K_entry.place(x=0.24 * w, y=(slide_h + 0.08) * h, anchor='w')
        ## 抗滑稳定安全系数计算按钮
        K_value_button = tk.Button(self, text='计算', font=('黑体', font_size3), width=4, height=1, command=self.get_K_value)
        K_value_button.place(x=0.31 * w, y=(slide_h + 0.08) * h, anchor='w')

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
        num_float_label = tk.Label(self.fig_change_frame, text='小数点位数', font=('黑体', font_size3 - 2), fg='gray')
        num_float_label.grid(column=0, row=0)
        self.num_float_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.num_float_entry.grid(column=0, row=1)
        ### 建基面应力集中高度
        dele_height_label = tk.Label(self.fig_change_frame, text='数据删除高度', font=('黑体', font_size3 - 2), fg='gray')
        dele_height_label.grid(column=1, row=0)
        self.dele_height_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.dele_height_entry.grid(column=1, row=1)
        ### 等值线最小值
        contour_min_label = tk.Label(self.fig_change_frame, text='等值线最小值', font=('黑体', font_size3 - 2), fg='gray')
        contour_min_label.grid(column=2, row=0)
        self.contour_min_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.contour_min_entry.grid(column=2, row=1)
        ### 等值线最大值
        contour_max_label = tk.Label(self.fig_change_frame, text='等值线最大值', font=('黑体', font_size3 - 2), fg='gray')
        contour_max_label.grid(column=3, row=0)
        self.contour_max_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.contour_max_entry.grid(column=3, row=1)
        ### 等值线间距
        contour_step_label = tk.Label(self.fig_change_frame, text='等值线间距', font=('黑体', font_size3 - 2), fg='gray')
        contour_step_label.grid(column=4, row=0)
        self.contour_step_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.contour_step_entry.grid(column=4, row=1)
        ### 集中点距离
        concen_dist_label = tk.Label(self.fig_change_frame, text='集中点距离', font=('黑体', font_size3 - 2), fg='gray')
        concen_dist_label.grid(column=5, row=0)
        self.concen_dist_entry = tk.Entry(self.fig_change_frame, width=10, relief='raised')
        self.concen_dist_entry.grid(column=5, row=1)
        ### 重新绘制按钮
        replot_button = tk.Button(self.fig_change_frame, text='重绘', font=('黑体', font_size3), width=6, height=2, command=self.replot)
        replot_button.grid(column=6, row=0, rowspan=2)
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
 