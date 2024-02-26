import numpy as np
import matplotlib.pyplot as plt
import scipy
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import time
import os
from matplotlib import cm
cmp = cm.get_cmap('jet')
cmp.set_under('w')
import seaborn as sns
sns.set_style('ticks')
sns.set_context('notebook')
plt.rcParams['font.sans-serif'] = 'Arial'


def get_current_time():
    """获取当前时间

    Returns:
        string: 当前时间，格式：年-月-日 时:分:秒
    """
    current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return current_time


def read_mesh(fpath):
    """读取网格文件，获取其中的结点集、单元集和表面集的名称

    Args:
        fpath (string): 网格文件路径

    Returns:
        Nset (list): 结点集列表
        Elset (list): 单元集列表
        Surface (list): 表面集列表
    """
    Nset, Elset, Surface = [], [], []
    if fpath.endswith('.inp'):  # 判断文件格式
        with open(fpath, encoding='gbk') as mesh_file:
            for line in mesh_file.readlines():
                # 读取结点集
                if '*NSET' in line or '*Nset' in line:
                    line = line.split('=')[1].split(',')
                    name = line[0].replace('\n', '').replace(' ', '')  # 去换行符和空格
                    Nset.append(name)
                # 读取单元集
                if '*ELSET' in line or '*Elset' in line:
                    line = line.split('=')[1].split(',')
                    name = line[0].replace(' ', '').replace('\n', '')  # 去换行符和空格
                    if name[0] != '_':  # 去除定义表面时的一些单元集
                        Elset.append(name)
                # 读取表面集
                if '*SURFACE' in line or '*Surface' in line:
                    line = line.split('=')[1].split(',')
                    name = line[0].replace('\n', '').replace(' ', '')  # 去换行符和空格
                    Surface.append(name)
    return Nset, Elset, Surface


def read_step(fpath):
    """读取分析步文件，获取其中的分析步名称

    Args:
        fpath (string): 分析步文件路径

    Returns:
        steps (list): 分析步名称集合
    """
    steps = []
    if fpath.endswith('.inp'):
        with open(fpath, encoding='gbk') as step_file:
            for line in step_file.readlines():
                if '*Step' in line or '*STEP' in line:
                    line = line.split('=')[1].split(',')
                    name = line[0].replace('\n', '').replace(' ', '')  # 去换行符和空格
                    steps.append(name)
    return steps


def read_bound(fpath):
    """读取边界结点文件，返回边界结点编号

    Args:
        fpath (string): 边界文件路径

    Returns:
        bound (np.array(n)): 边界结点编号数组
    """
    bound = np.loadtxt(fpath).astype(np.int64)
    return bound


def read_nodes(fpath, dims):
    """从网格文件中读取所有结点的坐标

    Args:
        fpath (string): 网格文件路径
        dims (int): 模型维度，分二维和三维

    Returns:
        nodes (np.array(n, 3 or 4)): 结点坐标数组，第一列为结点编号，后面几列为各节点坐标
    """
    nodes = []
    with open(fpath) as node_file:
        line = node_file.readline()
        while '*NODE' not in line.upper():
            line = node_file.readline()
        
        line = node_file.readline()
        while '*' not in line:
            line = line.replace(',', '').split()
            if dims == 2:
                nodes.append([int(line[0]), float(line[1]), float(line[2])])
            elif dims == 3:
                nodes.append([int(line[0]), float(line[1]), float(line[2]), float(line[3])])
            line = node_file.readline()
    nodes = np.array(nodes)
    nodes = nodes[np.argsort(nodes[:, 0])]
    return nodes


def read_coordinate(fpath):
    coord_all = {}
    with open(fpath) as coord_file:
        while True:
            line = coord_file.readline()
            if not line:
                break
            if '*ORIENTATION' in line:
                line = line.split(',')
                name = line[1]
                name = name.split()[-1]
                line = coord_file.readline()
                line = line.split(',')
                value = np.array([int(v) for v in line])
                coord_all[name] = value
    return coord_all


def find_csv_file(dir_path):
    csv_list = []
    flist = os.listdir(dir_path)
    for f in flist:
        if f.endswith('.csv'):
            csv_list.append(f)
    return csv_list


def find_geo_file(geo_path):
    bound_list = []
    area_list = []
    hole_list = []
    concen_list = []
    flist = os.listdir(geo_path)
    for f in flist:
        if f.endswith('.out'):
            if 'bound' in f and 'area' not in f and 'holes' not in f and 'delete' not in f:
                bound_list.append(f)
            if 'area' in f:
                area_list.append(f)
            if 'holes' in f:
                hole_list.append(f)
            if 'delete' in f:
                concen_list.append(f)
    return bound_list, area_list, hole_list, concen_list


def get_boundary(bound, nodes):
    """根据边界结点编号和所有结点坐标获取边界

    Args:
        bound (numpy.array(n)): 边界结点编号数组，结点编号需要按逆时针或者顺时针排序
        nodes (np.array(n, 3 or 4)): 结点坐标数组，第一列为结点编号，后面几列为各节点坐标

    Returns:
        boundary (list): 边界列表，每个元素是一个元组，表示结点坐标，结点按逆时针或者顺时针排序
    """
    boundary = []
    for node_id in bound:
        boundary.append(tuple(nodes[nodes[:, 0] == node_id][0, 1:]))
    return boundary


def getContour(x, y, z, boundary, vmin=None, vmax=None, dpi=100, flag=1, num_float=1, method='cubic', numline=10, max_min='abs', color=0, baseP=0, Extrapolation=1, holes=None, fontsize=14):
    """绘制等值线图

    Args:
        x (numpy.array(1, n)): 数据点的横坐标值.
        y (numpy.array(1, n)): 数据点的纵坐标值.
        z (numpy.array(1, n)): 数据点的数值大小.
        boundary (list): 等值线图边界点坐标的列表，需按顺时针或逆时针顺序排列，每个点是元组，如[(x1, y1), (x2, y2), ... , (xn, yn), (x1, y1)].
        vmin (float, optional): 等值线图中等值线最大值，默认无.
        vmax (float, optional): 等值线图中等值线最小值，默认无.
        dpi (int, optional): 插值分辨率，默认为100，即插值出来100x100的网格.
        flag (int, optional): 是否绘图，默认为1，即绘图.
        num_float (int, optional): 等值线数值中显示小数点位数，默认为1.
        method (str, optional): 插值方法，默认为'cubic'，即三次样条插值.
        numline (int or np.array(1, n), optional): 输入正整数则为等值线条数，输入数组则规定等值线数据，默认为10.
        max_min (str, optional): 标注极值点的类型，'max'为标注最大值点，'min'为标注最小值点，'abs'为标注绝对值最大值点，其他则为不标注，默认为'abs'.
        color (int, optional): 是否为等值线图上色，0为不上色，1为上色，默认为0.
        baseP (int, optional): 数据起始位置高度，默认为0.该参数是为了防止建基面上应力集中导致建基面上应力过大，绘制出来的等值线图不准确.
        Extrapolation (int, optional): 是否采用外插算法，0为不采用，1为采用，默认为1.
        holes (list, optional): 所有孔洞边界坐标点数据，列表里面的元素仍然是列表，每个列表代表一个孔洞边界；单个孔洞边界列表里是边界点元组，默认无孔洞.

    Returns:
        X (numpy.array(m, n)): 插值后网格点的横坐标.
        Y (numpy.array(m, n)): 插值后网格点的纵坐标.
        Z (numpy.array(m, n)): 插值后网格点上的数值.
        hd (matplotlib.contour.QuadContourSet): matplotlib图形句柄，只有选择绘图时才会输出.
    """
    bd = np.array(boundary)
    cmax = np.max(bd, axis=0)
    cmin = np.min(bd, axis=0)
    xi = np.linspace(cmin[0], cmax[0], dpi)
    yi = np.linspace(cmin[1], cmax[1], dpi)
    # idx = (x >= cmin[0]) * (x <= cmax[0]) * (y >= cmin[1]) * (y <= cmax[1])
    # x, y, z = x[idx], y[idx], z[idx]

    x = x[y >= baseP]
    z = z[y >= baseP]
    y = y[y >= baseP]
    # xi = np.linspace(np.min(x), np.max(x), dpi)
    # yi = np.linspace(np.min(y)+1, np.max(y), dpi)
    X, Y = np.meshgrid(xi, yi)
    if Extrapolation == 0:
        Z = scipy.interpolate.griddata((x, y), z, (X, Y), method=method)
    else:
        func = scipy.interpolate.Rbf(x,y,z,function=method)
        Z = func(X, Y)

    bound = Polygon(boundary)
    # pbar = tqdm.tqdm(range(xi.size), desc='wait', ncols=100)
    if holes is None:
        for i in range(xi.size):
            for j in range(yi.size):
                pp = Point(xi[i], yi[j])
                if not bound.contains(pp):
                    Z[j, i] = np.nan
    else:
        for i in range(xi.size):
            for j in range(yi.size):
                pp = Point(xi[i], yi[j])
                if not bound.contains(pp):
                    Z[j, i] = np.nan
                for hole in holes:
                    if Polygon(hole).contains(pp):
                        Z[j, i] = np.nan

    if flag == 1:
        hd = plt.contour(X, Y, Z, vmin=vmin, vmax=vmax, levels=numline, linestyles='-', colors='k', linewidths=1, zorder=1)
        if color == 1:
            Cd = plt.contourf(X, Y, Z, vmin=vmin, vmax=vmax, levels=numline, cmap='jet')
        plt.plot(bd[:, 0], bd[:, 1], color='k', linewidth=2)
        if holes is not None:
            for hole in holes:
                hl = np.array(hole)
                plt.plot(hl[:, 0], hl[:, 1], color='k', linewidth=1.5, zorder=3)
                plt.fill(hl[:, 0], hl[:, 1], 'w', zorder=2)
        if num_float == 1:
            plt.clabel(hd, inline=True, colors='k', fmt='%.1f', fontsize=fontsize, zorder=1)
        elif num_float == 2:
            plt.clabel(hd, inline=True, colors='k', fmt='%.2f', fontsize=fontsize, zorder=1)
        elif num_float == 0:
            plt.clabel(hd, inline=True, colors='k', fmt='%d', fontsize=fontsize, zorder=1)
        else:
            plt.clabel(hd, inline=True, colors='k', fmt='%.3f', fontsize=fontsize, zorder=1)
        if max_min == 'max':
            idx = np.argmax(z)
            plt.scatter(x[idx], y[idx], color='r', marker='*')
            plt.text(x[idx], y[idx], str('%.2f' % z[idx]), color='r', fontsize=fontsize + 2)
        elif max_min == 'min':
            idx = np.argmin(z)
            plt.scatter(x[idx], y[idx], color='r', marker='*')
            plt.text(x[idx], y[idx], str('%.2f' % z[idx]), color='r', fontsize=fontsize + 2)
        elif max_min == 'abs':
            idx = np.argmax(np.abs(z))
            plt.scatter(x[idx], y[idx], color='r', marker='*')
            plt.text(x[idx], y[idx], str('%.2f' % z[idx]), color='r', fontsize=fontsize + 2)
        plt.gca().set_aspect(1)
        plt.gca().set_axis_off()
        return X, Y, Z, hd
    else:
        return X, Y, Z