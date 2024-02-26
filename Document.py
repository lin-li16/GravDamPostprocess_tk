import tkinter as tk
from PIL import ImageTk, Image


class Document(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.width = root.win_width  # 获取窗口宽度
        self.height = root.win_height  # 获取窗口高度

        self.fig3_1 = Image.open('figs/fig3-1.png')
        self.fig3_1 = self.fig3_1.resize((1000, 600))
        self.fig3_1_tk = ImageTk.PhotoImage(image=self.fig3_1)
        self.fig3_2 = Image.open('figs/fig3-2.png')
        self.fig3_2 = self.fig3_2.resize((1000, 600))
        self.fig3_2_tk = ImageTk.PhotoImage(image=self.fig3_2)
        self.fig3_3 = Image.open('figs/fig3-3.png')
        self.fig3_3 = self.fig3_3.resize((200, 500))
        self.fig3_3_tk = ImageTk.PhotoImage(image=self.fig3_3)
        self.fig3_4 = Image.open('figs/fig3-4.png')
        self.fig3_4 = self.fig3_4.resize((1000, 600))
        self.fig3_4_tk = ImageTk.PhotoImage(image=self.fig3_4)
        self.fig3_5 = Image.open('figs/fig3-5.png')
        self.fig3_5 = self.fig3_5.resize((600, 290))
        self.fig3_5_tk = ImageTk.PhotoImage(image=self.fig3_5)
        self.fig3_6 = Image.open('figs/fig3-6.png')
        self.fig3_6 = self.fig3_6.resize((500, 460))
        self.fig3_6_tk = ImageTk.PhotoImage(image=self.fig3_6)
        self.fig3_7 = Image.open('figs/fig3-7.png')
        self.fig3_7 = self.fig3_7.resize((1000, 600))
        self.fig3_7_tk = ImageTk.PhotoImage(image=self.fig3_7)
        self.fig3_8 = Image.open('figs/fig3-8.png')
        self.fig3_8 = self.fig3_8.resize((1000, 600))
        self.fig3_8_tk = ImageTk.PhotoImage(image=self.fig3_8)
        self.set_page()


    def set_page(self):
        text = tk.Text(self, width=140, height=50, font=('宋体', 14), spacing2=12)
        text.pack(padx=10, pady=10, side='left')
        text.tag_config('title', font=('黑体', 22, 'bold'), justify='center')
        text.tag_config('title1', font=('黑体', 18), spacing2=12)
        text.tag_config('title2', font=('黑体', 16), spacing2=12)
        text.tag_config('title3', font=('黑体', 14), spacing2=12)
        text.tag_config('figs', font=('黑体', 12), spacing2=12)

        text.insert('insert', '\n')
        text.insert('insert', '重力坝抗震分析后处理程序使用说明\n\n', 'title')


        text.insert('insert', '1. 软件简介\n\n', 'title1')

        txt = '    在使用Abaqus进行重力坝静动力计算后，需要进行计算结果的后处理。然而，Abaqus后处理模块操作较为繁琐，使用门槛较高，且无法绘制工程上需要的位移、应力等数据的等值线图。因此，用户常使用Abaqus CAE界面将结果文件中的数据导出成一定格式，再通过其他第三方程序或者自行编写程序进行结果后处理。这大大降低了用户的工作效率，尤其是在计算工况较多，需要处理的数据较为繁杂的时候。\n\n'
        text.insert('insert', txt)

        txt = '    本软件基于python环境，使用tkinter库编写用户界面，将导出Abaqus结果文件数据和数据的后处理集于一体，使得重力坝抗震分析的后处理变得极为简洁高效。该软件包含了二维和三维重力坝抗震分析的后处理，能够从Abaqus的odb结果文件中导出需要的数据，绘制加速度时程曲线、典型剖面位移和应力的等值线图和损伤因子分布图、横缝的开度等值线图，以及进行二维和三维的抗滑稳定分析，基本涵盖了重力坝抗震分析所需要的内容。\n\n'
        text.insert('insert', txt)

        text.insert('insert', '2. 软硬件环境要求\n\n', 'title1')

        txt = '    硬件环境要求：普通PC机（正常完整配置即可）。\n\n'
        text.insert('insert', txt)

        txt = '    软件环境要求：Windows10及以上，安装有Abaqus软件。\n\n'
        text.insert('insert', txt)
        
        text.insert('insert', '3. 用户使用说明\n\n', 'title1')

        text.insert('insert', '3.1 软件打开与关闭\n\n', 'title2')

        txt = '    软件打开：双击该软件的.exe程序即可打开软件界面。\n\n'
        text.insert('insert', txt)

        txt = '    软件关闭：单击界面右上角的“×”关闭按钮。\n\n'
        text.insert('insert', txt)

        text.insert('insert', '3.2 界面说明\n\n', 'title2')

        txt = '    打开软件后，菜单栏将显示三个功能模块：二维有限元后处理，三维有限元后处理，帮助。点击每个功能模块，在下拉菜单栏中将显示每个功能模块的子模块。其中“二维有限元后处理”和“三维有限元后处理”模块包含“导出数据”、“静力”和“时程法”三个子模块，“帮助”模块包含“帮助文档”和“联系我们”两个子模块，各子模块的主要功能如下：\n\n'
        text.insert('insert', txt)

        txt = '（1） 导出数据：根据用户所选内容，从Abaqus的odb结果文件中导出后处理需要的数据；\n\n'
        text.insert('insert', txt)
        txt = '（2） 静力：根据用户需求，进行静力工况的后处理\n\n'
        text.insert('insert', txt)
        txt = '（3） 时程法：根据用户需求，进行时程法动力工况的后处理\n\n'
        text.insert('insert', txt)
        txt = '（4） 帮助文档：显示软件的使用说明\n\n'
        text.insert('insert', txt)
        txt = '（5） 联系我们：显示开发者的联系方式\n\n'
        text.insert('insert', txt)

        text.insert('insert', '3.3 二维有限元处理模块\n\n', 'title2')

        txt = '    本模块针对重力坝二维抗震分析后处理问题，实现了从Abaqus的odb结果文件导出数据、绘制动力加速度响应时程曲线、坝体静动力位移和应力等值线图及损伤因子分布图、二维多层面抗滑稳定分析功能。\n\n'
        text.insert('insert', txt)

        text.insert('insert', '3.3.1 “导出数据”模块\n\n', 'title3')

        txt = '    二维“导出数据”模块的主界面如图3-1所示，主要分为数据导出操作命令区域和日志显示区域。操作命令区域用于用户选择相关的文件和需要导出的数据，日志显示区域将实时显示用户的一些操作和程序运行结果提示。\n\n'
        text.insert('insert', txt)


        txt = '    首先，用户需要选择网格文件、分析步文件和结果文件。网格文件为Abaqus模型输入文件，后缀为“inp”，里面需要包含所有结点的编号和坐标信息、后处理需要用到的结点集（Nset）、单元集（Elset）和表面（Surface）；分析步文件为Abaqus计算输入文件，后缀为“inp”，里面需要包含计算的所有分析步信息；结果文件为Abaqus的计算结果文件，后缀为“odb”，为之前两个文件对应的结果文件。分别点击三个文件组件右边的“选择文件”按钮后，可打开文件选择对话框，选择对应文件即可。选择完毕后，点击“读取”按钮，软件将读取文件中的相关信息，并将所有结点集、单元集、表面、分析步显示在下方对应的下拉选择框中。点击“清除”按钮，可清除已选择的相关文件和下方下拉选择框的内容。\n\n'
        text.insert('insert', txt)

        txt = '    然后用户需要在“Abaqus版本”选择组件中选择odb结果文件计算所使用的Abaqus版本，目前支持Abaqus2016-2021，允许用户安装多个版本的Abaqus，但务必选择odb文件所对应的版本。\n\n'
        text.insert('insert', txt)

        txt = '    接着用户可根据自己的需求在下方选择需要输出的数据，可供输出的数据类型有加速度、位移、应力、抗滑稳定、损伤因子数据，每种类型数据均可选择输出需要的结点集、单元集、表面，并且可选择输出对应的分析步上的数据，这些集合和分析步将在读取上述三个文件后自动显示在下拉选择框中。在“帧”选择中，位移和抗滑稳定导出模块中可选择“最后一帧”和“所有帧”，应力导出模块可选择“最后一帧”和“包络帧”，损伤因子导出模块可直接输入需要导出的帧数，以便观察损伤因子分布的演化状态。“最后一帧”一般适用于静力分析，导出静力分析步的最后一帧数据；“所有帧”和“包络帧”一般适用于动力分析，“所有帧”能导出动力分析步中所有时间点上的数据，“包络帧”则计算动力分析全时程中，最大或最小值的包络数据。\n\n'
        text.insert('insert', txt)

        txt = '    选择需要输出的数据完成后，点击“导出数据”按钮，软件将从odb中导出相关数据，数据文件将保存在odb结果文件所在的文件夹下，数据文件后缀为“.csv”或“.out”。导出数据时需要一定的时间，尤其是导出动力数据，请耐心等待，导出完毕后日志框将有信息提示。\n\n'
        text.insert('insert', txt)

        text.image_create('insert', image=self.fig3_1_tk)
        text.insert('insert', '\n图3-1 二维数据导出主界面', 'figs')
        text.insert('insert', '\n\n')

        text.insert('insert', '3.3.2 “静力”模块\n\n', 'title3')

        txt = '    二维“静力”模块的主界面如图3-2所示，主要分为操作命令区域、图片显示区域和日志显示区域。操作命令区域用于用户选择需要进行的后处理操作，图片显示区域将显示后处理绘制的图片，日志显示区域将实时显示用户的一些操作和程序运行结果提示。\n\n'
        text.insert('insert', txt)

        txt = '    首先，用户需要选择结果文件、网格文件和边界文件，结果文件和网格文件说明同3.3.1节，边界文件为坝体边界关键结点编号，格式为文本文件，每行为一个结点编号，结点需要按顺时针或者逆时针顺序排列，且首尾结点相同，如图3-3所示，软件将根据这个文件确定坝体边界。文件选择完毕后，点击右侧“读取”按钮，软件将读取文件中的相关信息。点击“清除”按钮，可清除已选择的相关文件。\n\n'
        text.insert('insert', txt)

        txt = '    接着用户可根据自己的需求在下方选择处理的数据。“位移”处理选项中，可选择绘制X向和Y向的静力位移等值线图；“应力”处理选项中，可选择绘制大主应力和小主应力等值线图；“损伤因子”处理选项中，可选择是否绘制坝体损伤因子分布图；“抗滑稳定”处理选项中，可选择处理的层面，然后输入对应的抗剪断参数f’和c’，点击下方的计算按钮，将显示抗滑稳定安全系数，大于1代表抗滑稳定校核通过，小于1则不通过。点击操作命令区域右下角的“清除”按钮，可一键清除选择框和输入框中的内容。\n\n'
        text.insert('insert', txt)

        txt = '    后处理选择结束后，点击操作命令区域和图片显示区域中间的“绘制”按钮，软件将绘制用户所选择的图片，并全部显示在图片显示区域。图片标题将显示在原“图片显示”文字处，点击左右两侧的按钮可进行图片切换，有图片时图框内左上角将显示图片工具栏，可对图片进行移动、放大缩小、保存等操作，点击“全部导出”按钮还可将图框内所有图片一键导出成’.svg’矢量图格式，保存在odb结果文件夹中的’figures’子文件夹（如果没有这个文件夹，程序将自动创建）。对于等值线图，图框下方还有微调选项，“小数点位数”为等值线数值的小数点位数，“数据删除高程”可用于删除坝基面往上一定高度处的数据点，以缓解坝基面应力集中严重的问题，等值线最小值、等值线最大值、等值线间距可用于调整等值线图中的等值线的数值。参数输入完毕后，点击“重绘”按钮，软件将重新绘制当前图窗中的图片，并显示在图窗中。\n\n'
        text.insert('insert', txt)

        text.image_create('insert', image=self.fig3_2_tk)
        text.insert('insert', '\n图3-2 二维静力处理界面', 'figs')
        text.insert('insert', '\n\n')

        text.image_create('insert', image=self.fig3_3_tk)
        text.insert('insert', '\n图3-3 边界文件样例', 'figs')
        text.insert('insert', '\n\n')

        text.insert('insert', '3.3.3 “时程法”模块\n\n', 'title3')

        txt = '    二维“时程法”模块的主界面如图3-4所示，基本布局同二维“静力”模块，仅在后处理选择上有所不同。“加速度”处理选项中，可选择绘制坝顶结点、坝踵结点和坝基面结点（“导出数据”时选择的结点）的X向和Y向时程曲线，如果在“PGA”输入框中写入输入地震动的PGA（单位：g），软件还将绘制各结点加速度放大倍数曲线。“位移”处理选项中，可选择坝体X向和Y向的最大正向和负向的相对位移包络等值线图，需要填写参考节点，可写结点编号，也可写结点坐标（“x,y”的格式）。“应力”处理选项中，可选择坝体大主应力和小主应力的包络等值线图。“损伤因子”处理选项中，可选择绘制不同帧下的坝体损伤因子分布图。“抗滑稳定”处理选项中，可选择处理的层面，然后输入对应的抗剪断参数f’和c’，点击“绘制”后软件将绘制抗滑稳定安全系数时程曲线，并显示全时程中，抗滑稳定安全校核不通过时长。\n\n'
        text.insert('insert', txt)

        text.image_create('insert', image=self.fig3_4_tk)
        text.insert('insert', '\n图3-4 二维时程法处理界面', 'figs')
        text.insert('insert', '\n\n')

        text.insert('insert', '3.4 三维有限元处理模块\n\n', 'title2')

        txt = '    本模块针对重力坝三维抗震分析后处理问题，实现了从Abaqus的odb结果文件导出数据、绘制动力加速度响应时程曲线、坝体静动力位移和应力等值线图及损伤因子分布图、横缝开度等值线图、三维双滑面块体抗滑稳定分析功能。\n\n'
        text.insert('insert', txt)

        txt = '    由于三维后处理涉及多个剖面或表面的处理，因此该软件在后处理相关文件命名上做出一定要求，以保证软件能找到每个剖面对应的几何文件。剖面名称以网格文件中的集合名称为基准，每个剖面有其对应的边界结点文件、局部坐标系名称，局部坐标系名称也在网格文件中有定义，软件会自行读取。有些剖面还有孔洞结点文件、应力集中结点文件、结点面积文件。这些文件的命名都必须含有剖面名称，边界结点文件以“bound-”开头，孔洞结点名称以“holes-”开头，应力集中结点文件以“delete-”开头，结点面积文件以“area-”开头。边界结点文件格式同二维中的边界结点文件；孔洞结点文件每一行为一个孔洞的结点编号，按顺时针或逆时针排列，首位一样，每个结点以“tab”键分隔；应力集中结点文件为集中点的结点编号，每行为一个结点编号；结点面积文件为Abaqus中反力场输出的文件格式。各个文件格式样例如图3-5-图3-6所示，这些集合文件需要放在同一个文件夹中。\n\n'
        text.insert('insert', txt)

        text.image_create('insert', image=self.fig3_5_tk)
        text.insert('insert', '\n图3-5 边界结点文件、孔洞结点文件和应力集中结点文件样例（从左到右顺序）', 'figs')
        text.insert('insert', '\n\n')

        text.image_create('insert', image=self.fig3_6_tk)
        text.insert('insert', '\n图3-6 结点面积文件样例', 'figs')
        text.insert('insert', '\n\n')

        text.insert('insert', '3.4.1 “导出数据”模块\n\n', 'title3')

        txt = '    三维“导出数据”模块和二维“导出数据”模块用法一样，参考3.3.1节。\n\n'
        text.insert('insert', txt)

        text.insert('insert', '3.4.2 “静力”模块\n\n', 'title3')

        txt = '    三维“静力”模块的主界面如图3-5所示，基本布局同二维“静力”模块。“几何信息”选择中，用户需要选择后处理所需的几何文件所在的文件夹，文件夹中包含边界结点文件、孔洞结点文件、应力集中结点文件、结点面积文件。在“位移”、“应力”、“损伤因子”处理选项中的剖面选项中，可选择需要绘制的剖面的相关等值线图，剖面选项将根据导出数据中已导出的数据文件来决定。“横缝”处理选项中，可选择横缝进行该横缝的开度等值线图绘制，此时需要把包含横缝开度数据的与odb同名的“.dat”文件放在odb结果文件夹中。“抗滑稳定”处理选项中，需要选择块体两个滑面，以及输入这两个滑面对应的抗剪断参数。当图片显示区域显示的是等值线图时，三维模块中图片调整组件多了一个集中点距离选项，该选项针对某些面（如上下游表面）需要去除部分应力集中区域的问题，可输入一个数x，在距离这些应力集中点x米的结点数据将不被用于等值线图的绘制，而是采用外插算法补充数，以此来缓解应力集中导致等值线部分区域过密的问题。\n\n'
        text.insert('insert', txt)

        text.image_create('insert', image=self.fig3_7_tk)
        text.insert('insert', '\n图3-7 三维静力处理界面', 'figs')
        text.insert('insert', '\n\n')

        text.insert('insert', '3.4.3 “时程法”模块\n\n', 'title3')

        txt = '    三维“时程法”处理模块主界面如图 3 8所示，基本布局同三维“静力”模块，仅在后处理选择上有所不同。“加速度”处理选项中，可选择绘制坝顶结点、坝踵结点和坝基面结点（“导出数据”时选择的结点）的X向、Y向和Z向时程曲线，如果在“PGA”输入框中写入输入地震动的PGA（单位：g），软件还将绘制各结点加速度放大倍数曲线。“位移”处理选项中，可选择不同剖面X向和Y向的最大相对位移包络等值线图，需要填写参考节点，可写结点编号，也可写结点坐标（“x,y”的格式）。“应力”处理选项中，可选择坝体大主应力和小主应力的包络等值线图。“抗滑稳定”处理选项中，可选择处理的层面，然后输入对应的抗剪断参数f’和c’，点击“绘制”后软件将绘制抗滑稳定安全系数时程曲线，并显示全时程中，抗滑稳定安全校核不通过时长。\n\n'
        text.insert('insert', txt)

        text.image_create('insert', image=self.fig3_8_tk)
        text.insert('insert', '\n图3-8 三维时程法处理界面', 'figs')
        text.insert('insert', '\n\n')


        scrollbar = tk.Scrollbar(self, command=text.yview)
        scrollbar.pack(side='right', fill='y')
        text.config(yscrollcommand=scrollbar.set, state='disabled')