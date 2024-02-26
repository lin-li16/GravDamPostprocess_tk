import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import cm
cmp = cm.get_cmap('jet')
cmp.set_under('w')
import seaborn as sns
sns.set_style('ticks')
sns.set_context('notebook')
plt.rcParams['font.sans-serif'] = 'Arial'
from functions import getContour
from kanghua3D import *


def read_joint_dat_sta(fname):
    """读取静力.dat文件中的横缝开度数据

    Args:
        fname (string): odb结果文件对应的.dat文件

    Returns:
        copen_data (list): 所有横缝的开度数据数组列表
        copen_id (list): 所有横缝的标签
    """
    with open(fname, encoding='gbk') as dat_file:
        line = dat_file.readline()
        while 'S T E P       4' not in line:  # 最后一个分析步，如果分析步更多则要修改
            line = dat_file.readline()
        copen_data = []
        copen_id = []
        while 'ANALYSIS COMPLETE' not in line:
            if 'CONTACT OUTPUT' in line:
                copen_id.append(line)
                copen = []
                for i in range(5):
                    line = dat_file.readline()
                while line not in ['\n','\r\n']:
                    line = line.replace('CL', '0').replace('OP', '1')
                    line = line.split()
                    copen.append(line)
                    line = dat_file.readline()
                copen = np.array(copen).astype(np.float64)
                copen_data.append(copen)
            else:
                line = dat_file.readline()
        dat_file.close()
    return copen_data, copen_id


def read_joint_dat_dyn(fname):
    """读取动力.dat文件中的横缝开度数据

    Args:
        fname (string): odb结果文件对应的.dat文件

    Returns:
        copen_data (list): 所有横缝的开度数据数组列表
        copen_id (list): 所有横缝的标签
    """
    with open(fname, encoding='gbk') as dat_file:
        line = dat_file.readline()
        while 'S T E P       4' not in line:
            line = dat_file.readline()
        copen_data = []
        copen_id = []
        while 'S T E P       5' not in line:
            if 'CONTACT OUTPUT' in line:
                copen_id.append(line)
                copen = []
                for i in range(5):
                    line = dat_file.readline()
                while line not in ['\n','\r\n']:
                    line = line.replace('CL', '0').replace('OP', '1')
                    line = line.split()
                    copen.append(line)
                    line = dat_file.readline()
                copen = np.array(copen).astype(np.float64)
                copen_data.append(copen)
            else:
                line = dat_file.readline()

        joint_id = 0
        increment = 0
        while True:
            if 'INCREMENT' in line and 'SUMMARY' in line:
                increment += 1
                joint_id = 0
                line = dat_file.readline()
                while 'INCREMENT' not in line or 'SUMMARY' not in line:
                    if 'CONTACT OUTPUT' in line:
                        copen = []
                        for i in range(5):
                            line = dat_file.readline()
                        while line not in ['\n', '\r\n']:
                            line = line.replace('CL', '0').replace('OP', '1')
                            line = line.split()
                            copen.append(line)
                            line = dat_file.readline()
                        copen = np.array(copen).astype(np.float64)
                        if increment == 1:
                            copen_data[joint_id] = np.stack((copen_data[joint_id], copen), axis=2)
                        else:
                            copen_data[joint_id] = np.append(copen_data[joint_id], copen[:, :, None], axis=2)
                        joint_id += 1
                    else:
                        line = dat_file.readline()
                    if not line:
                        break
            else:
                line = dat_file.readline()
            if not line:
                break
    return copen_data, copen_id


def change_coord(coordinate_nodes, nodes, all_nodes=None):
    """将结点坐标转换为在局部坐标系z向法平面的坐标

    Args:
        coordinate_nodes (numpy.array): 局部坐标系，如果为一维数组，则表示确定局部坐标系的三个结点的编号；如果为二维数组，则表示确定局部坐标系三个结点的坐标。三个结点依次为x轴上的结点、xy平面上的结点和坐标原点
        nodes (numpy.array): 需要转换坐标的结点，如果为一维数组，则表示结点编号；如果为二维数组，则表示结点坐标
        all_nodes (numpy.array(n, 4), optional): 所有结点的坐标数组，第一列表示结点编号，后面三列依次表示坐标值，默认为None，只有当前面两个参数输入的是结点编号时才需要用到

    Returns:
        numpy.array(n, 2): 转换后的坐标数组
    """
    if all_nodes is None:  # 如果没有给所有结点坐标
        nodeP = coordinate_nodes[2, :]  # 获取坐标原点坐标
        nodeQ = coordinate_nodes[0, :]  # 获取x轴上的点坐标
        nodeR = coordinate_nodes[1, :]  # 获取xy平面上的点坐标
        vec_x = (nodeQ - nodeP) / np.linalg.norm((nodeQ - nodeP))  # 获取局部坐标系的x轴方向向量
        vec_y = (nodeR - nodeP) - (nodeR - nodeP).dot(vec_x) * vec_x
        vec_y = vec_y / np.linalg.norm(vec_y)  # 获取局部坐标系的y轴方向向量
        xx, yy = (nodes - nodeP).dot(vec_x), (nodes - nodeP).dot(vec_y)  # 获取转换后的坐标
        return np.column_stack([xx, yy])
    else:  # 如果给了所有结点的坐标
        if len(coordinate_nodes.shape) == 1:  # 如果局部坐标系给的是结点编号
            nodeP = all_nodes[all_nodes[:, 0] == coordinate_nodes[2]][0, 1:]  # 获取坐标原点坐标
            nodeQ = all_nodes[all_nodes[:, 0] == coordinate_nodes[0]][0, 1:]  # 获取x轴上的点坐标
            nodeR = all_nodes[all_nodes[:, 0] == coordinate_nodes[1]][0, 1:]  # 获取xy平面上的点坐标
        else:  # 如果局部坐标系给的是结点坐标
            nodeP = coordinate_nodes[2, :]  # 获取坐标原点坐标
            nodeQ = coordinate_nodes[0, :]  # 获取x轴上的点坐标
            nodeR = coordinate_nodes[1, :]  # 获取xy平面上的点坐标
        vec_x = (nodeQ - nodeP) / np.linalg.norm((nodeQ - nodeP))  # 获取局部坐标系的x轴方向向量
        vec_y = (nodeR - nodeP) - (nodeR - nodeP).dot(vec_x) * vec_x
        vec_y = vec_y / np.linalg.norm(vec_y)  # 获取局部坐标系的y轴方向向量
        try:  # 如果需要转换结点给的是坐标值
            xx, yy = (nodes - nodeP).dot(vec_x), (nodes - nodeP).dot(vec_y)  # 获取转换后的坐标
        except:  # 如果需要转换结点给的是结点编号
            nodes_coord = np.zeros((len(nodes), all_nodes.shape[1] - 1))
            for i, id in enumerate(nodes):
                nodes_coord[i, :] = all_nodes[all_nodes[:, 0] == id][0, 1:]
            xx, yy = (nodes_coord - nodeP).dot(vec_x), (nodes_coord - nodeP).dot(vec_y)  # 获取转换后的坐标
        return np.column_stack([xx, yy])


def transform_coord(coordinate_nodes, bound_nodes, section_nodes_coord, nodes_data):
    """转换坐标系函数

    Args:
        coordinate_nodes (numpy.array(3)): 局部坐标系结点组编号，第一个结点为x轴上的点，第二个为xy平面上一点，第三个为坐标原点
        bound_nodes (numpy.array(n)): 边界结点坐标编号，按逆时针或者顺时针排列
        section_nodes_coord (numpy.array(n, 3)): 剖面上结点的坐标数组
        nodes_data (numpy.array(n, 4)): 所有结点的编号和坐标，第一列为结点编号

    Returns:
        XX (numpy.array(n)): 剖面结点在局部坐标系上的横坐标
        YY (numpy.array(n)): 剖面结点在局部坐标系上的纵坐标
        boundary (list): 边界列表，每个元素是一个元组，表示结点坐标，结点按逆时针或者顺时针排序
    """
    all_nodes_id = nodes_data[:, 0].astype(np.int64)  # 获取所有结点编号
    all_nodes_coord = nodes_data[:, 1:]  # 获取所有结点坐标
    nodeP = all_nodes_coord[all_nodes_id == coordinate_nodes[2]].ravel()  # 局部坐标系原点的结点坐标
    nodeQ = all_nodes_coord[all_nodes_id == coordinate_nodes[0]].ravel()  # 局部坐标系x轴上的结点坐标
    nodeR = all_nodes_coord[all_nodes_id == coordinate_nodes[1]].ravel()  # 局部坐标系y轴上的结点坐标
    vec_x = (nodeQ - nodeP) / np.linalg.norm((nodeQ - nodeP))  # 获取局部坐标系的x轴方向向量
    vec_y = (nodeR - nodeP) - (nodeR - nodeP).dot(vec_x) * vec_x
    vec_y = vec_y / np.linalg.norm(vec_y)  # 获取局部坐标系的y轴方向向量
    # 获取局部坐标系下的边界列表
    boundary = []
    for id in bound_nodes:
        boundA = all_nodes_coord[all_nodes_id == id].ravel()
        boundary.append(((boundA - nodeP).dot(vec_x), (boundA - nodeP).dot(vec_y)))
    # 获取局部坐标系下剖面结点的横纵坐标
    XX = np.zeros(section_nodes_coord.shape[0])
    YY = np.zeros(section_nodes_coord.shape[0])
    for i in range(XX.shape[0]):
        nodei = section_nodes_coord[i, :]
        XX[i], YY[i] = (nodei - nodeP).dot(vec_x), (nodei - nodeP).dot(vec_y)
    return XX, YY, boundary
    

def sta_disp_contour(fname, coordinate_nodes, bounds, nodes_data, direc='X', holes=None, concen=None, concen_dist=0):
    """绘制静力位移等值线图

    Args:
        fname (string): 静力位移数据文件路径
        coordinate_nodes (numpy.array): 局部坐标系，如果为一维数组，则表示确定局部坐标系的三个结点的编号；如果为二维数组，则表示确定局部坐标系三个结点的坐标。三个结点依次为x轴上的结点、xy平面上的结点和坐标原点
        bounds (list): 边界结点文件列表
        nodes_data (numpy.array(n, 4)): 所有结点的编号和坐标，第一列为结点编号
        direc (string): 位移方向，分X向、Y向和Z向，默认为'X'
        holes (string): 孔洞文件，默认为None
        concen (string): 应力集中区域文件，默认为None
        concen_dist (float): 集中点距离，默认为0

    Returns:
        fig (plt.figure): 图片句柄
        xxU (np.array(n)): 数据点的横坐标数组
        yyU (np.array(n)): 数据点的纵坐标数组
        zzU (np.array(n)): 数据点的值
        boundarys (list): 边界结点列表，用于重绘
        holes (list): 孔洞列表，用于重绘
        concen (string): 应力集中区域文件，默认为None
    """
    # 加载位移数据
    disp_data = pd.read_csv(fname, encoding='gbk')
    disp_data.rename(columns={'      结点编号': 'node', '          U-U1': 'U-U1', '          U-U2': 'U-U2', '          U-U3': 'U-U3'}, inplace=True)
    disp_data = disp_data.sort_values(by='node')  # 按结点排序
    section_nodes_coord = np.array(disp_data[['X', 'Y', 'Z']])
    if direc == 'X':
        zzU = np.array(disp_data['U-U1'] * 100)
    elif direc == 'Y':
        zzU = np.array(disp_data['U-U2'] * 100)
    else:
        zzU = np.array(disp_data['U-U3'] * 100)
    xyU = change_coord(coordinate_nodes, section_nodes_coord, nodes_data)  # 转换剖面结点坐标
    # 如果需要删除一些应力集中点
    if concen is not None:
        concen_nodes = np.loadtxt(concen)
        concen_coord = change_coord(coordinate_nodes, concen_nodes, nodes_data)
        xyU_dele, zzU_dele = [], []
        for i in range(xyU.shape[0]):
            dist = np.sqrt(np.sum((concen_coord - xyU[i, :]) ** 2, axis=1))
            if np.min(dist) > concen_dist:  # 判断该剖面结点离应力集中区域最小的距离是否大于集中点距离
                xyU_dele.append(xyU[i, :])
                zzU_dele.append(zzU[i])
        xyU = np.array(xyU_dele)
        zzU = np.array(zzU_dele)
    xxU, yyU = xyU[:, 0], xyU[:, 1]
    # 加载孔洞数据
    if holes is not None:
        holes_nodes = np.loadtxt(holes)
        holes = []
        for i in range(holes_nodes.shape[0]):
            hole_coord = change_coord(coordinate_nodes, holes_nodes[i, :], nodes_data)
            holes.append([tuple(v) for v in list(hole_coord)])

    boundarys = []
    if len(bounds) == 1:  # 如果只有一个边界
        bound_nodes = np.loadtxt(bounds[0])
        bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
        boundary = [tuple(v) for v in list(bound_coord)]
        boundarys.append(boundary)
        fig = plt.figure(figsize=(6.1, 4.4))
        try:
            X, Y, ZU, hd = getContour(xxU, yyU, zzU, boundary, dpi=100, Extrapolation=0, holes=holes)
        except:
            X, Y, ZU, hd = getContour(xxU, yyU, zzU, boundary, dpi=100, Extrapolation=1, holes=holes)
    else:  # 如果有两个边界
        zzU_max = np.max(zzU)
        zzU_min = np.min(zzU)
        numline = np.arange(zzU_min, zzU_max, (zzU_max - zzU_min) / 10)
        fig = plt.figure(figsize=(6.1, 4.4))
        for bound in bounds:
            bound_nodes = np.loadtxt(bound)
            bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
            boundary = [tuple(v) for v in list(bound_coord)]
            boundarys.append(boundary)
            try:
                X, Y, ZU, hd = getContour(xxU, yyU, zzU, boundary, numline=numline, dpi=100, Extrapolation=0, holes=holes)
            except:
                X, Y, ZU, hd = getContour(xxU, yyU, zzU, boundary, numline=numline, dpi=100, Extrapolation=1, holes=holes)
    plt.tight_layout()
    return fig, xxU, yyU, zzU, boundarys, holes, concen


def sta_stre_contour(fname, coordinate_nodes, bounds, nodes_data, component='Smax', holes=None, concen=None, concen_dist=0):
    """绘制静力应力等值线图

    Args:
        fname (string): 静力应力数据文件路径
        coordinate_nodes (numpy.array): 局部坐标系，如果为一维数组，则表示确定局部坐标系的三个结点的编号；如果为二维数组，则表示确定局部坐标系三个结点的坐标。三个结点依次为x轴上的结点、xy平面上的结点和坐标原点
        bounds (list): 边界结点文件列表
        nodes_data (numpy.array(n, 4)): 所有结点的编号和坐标，第一列为结点编号
        component (string): 应力分量，Smax表示大主应力，Smin表示小主应力，默认为Smax
        holes (string): 孔洞文件，默认为None
        concen (string): 应力集中区域文件，默认为None
        concen_dist (float): 集中点距离，默认为0

    Returns:
        fig (plt.figure): 图片句柄
        xxS (np.array(n)): 数据点的横坐标数组
        yyS (np.array(n)): 数据点的纵坐标数组
        zzS (np.array(n)): 数据点的值
        boundarys (list): 边界结点列表，用于重绘
        holes (list): 孔洞列表，用于重绘
        concen (string): 应力集中区域文件，默认为None
    """
    # 获取应力数据
    stre_data = pd.read_csv(fname, encoding='gbk')
    stre_data.rename(columns={'      结点编号': 'node'}, inplace=True)
    stre_data.drop_duplicates(subset='node', keep='first', inplace=True)
    stre_data = stre_data.sort_values(by='node')  # 按结点排序
    section_nodes_coord = np.array(stre_data[['X', 'Y', 'Z']])
    if component == 'Smax':
        zzS = np.array(stre_data['S-Max. Principal'] / 1e6)
        max_min = 'max'
    elif component == 'Smin':
        zzS = np.array(stre_data['S-Min. Principal'] / 1e6)
        max_min = 'min'
    xyS = change_coord(coordinate_nodes, section_nodes_coord, nodes_data)  # 转换剖面结点坐标
    # 如果需要删除一些应力集中点
    if concen is not None:
        concen_nodes = np.loadtxt(concen)
        concen_coord = change_coord(coordinate_nodes, concen_nodes, nodes_data)
        xys_dele, zzS_dele = [], []
        for i in range(xyS.shape[0]):
            dist = np.sqrt(np.sum((concen_coord - xyS[i, :]) ** 2, axis=1))
            if np.min(dist) > concen_dist:  # 判断该剖面结点离应力集中区域最小的距离是否大于集中点距离
                xys_dele.append(xyS[i, :])
                zzS_dele.append(zzS[i])
        xyS = np.array(xys_dele)
        zzS = np.array(zzS_dele)
    xxS, yyS = xyS[:, 0], xyS[:, 1]
    # 如果有孔洞
    if holes is not None:
        holes_nodes = np.loadtxt(holes)
        holes = []
        for i in range(holes_nodes.shape[0]):
            hole_coord = change_coord(coordinate_nodes, holes_nodes[i, :], nodes_data)
            holes.append([tuple(v) for v in list(hole_coord)])
    boundarys = []
    if len(bounds) == 1:  # 如果只有一个边界
        bound_nodes = np.loadtxt(bounds[0])
        bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
        boundary = [tuple(v) for v in list(bound_coord)]
        boundarys.append(boundary)
        fig = plt.figure(figsize=(6.1, 4.4))
        try:
            X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, dpi=100, Extrapolation=1, max_min=max_min, holes=holes)
        except:
            X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, dpi=100, Extrapolation=0, max_min=max_min, holes=holes)
    else:  # 如果有多个边界
        zzS_max = np.max(zzS)
        zzS_min = np.min(zzS)
        numline = np.arange(zzS_min, zzS_max, (zzS_max - zzS_min) / 10)
        fig = plt.figure(figsize=(6.1, 4.4))
        for bound in bounds:
            bound_nodes = np.loadtxt(bound)
            bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
            boundary = [tuple(v) for v in list(bound_coord)]
            boundarys.append(boundary)
            try:
                X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, numline=numline, dpi=100, Extrapolation=1, max_min=max_min, holes=holes)
            except:
                X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, numline=numline, dpi=100, Extrapolation=0, max_min=max_min, holes=holes)
    plt.tight_layout()
    return fig, xxS, yyS, zzS, boundarys, holes, concen


def sta_joint_contour(joint, bounds, coordinate, copen_data, copen_id, nodes, holes=None, concen=None):
    """绘制静力横缝开度分布图

    Args:
        joint (string): 横缝标志
        bounds (string): 边界结点文件
        coordinate (numpy.array): 局部坐标系结点编号
        copen_data (list): 所有横缝开度数据
        copen_id (list): 所有横缝的标志
        nodes (numpy.array(n, 4)): 所有结点坐标
        holes (list): 孔洞列表，用于重绘
        concen (string): 应力集中区域文件，默认为None

    Returns:
        fig (plt.figure): 图片句柄
        XX (np.array(n)): 数据点的横坐标数组
        YY (np.array(n)): 数据点的纵坐标数组
        joint_copen (np.array(n)): 数据点的值
        boundarys (list): 边界结点列表，用于重绘
        holes (list): 孔洞列表，用于重绘
        concen (string): 应力集中区域文件，默认为None
    """
    bound_nodes = np.loadtxt(bounds)  # 读取边界结点文件
    # 获取横缝
    for i in range(len(copen_id)):
        if joint.upper() in copen_id[i]:
            idx = i
    # 获取横缝开度数据
    joint_node_id = copen_data[idx][:, 0].ravel().astype(np.int64)
    joint_if_open = copen_data[idx][:, 1].ravel().astype(np.int64)
    joint_copen = 1000 * copen_data[idx][:, 2].ravel()
    joint_copen[joint_if_open == 0] = 0

    all_nodes_id = nodes[:, 0].astype(np.int64)
    all_nodes_coord = nodes[:, 1:]
    # 获取横缝结点坐标
    joint_node_coord = np.zeros((joint_node_id.shape[0], 3))
    for i in range(joint_node_id.shape[0]):
        joint_node_coord[i, :] = all_nodes_coord[all_nodes_id == joint_node_id[i], :]

    boundarys = []
    XX, YY, boundary = transform_coord(coordinate, bound_nodes, joint_node_coord, nodes)
    boundarys.append(boundary)
    fig = plt.figure(figsize=(6.1, 4.4))
    step = np.max([np.max(joint_copen) / 10, 0.1])
    X, Y, vCopen, hd = getContour(XX, YY, joint_copen, boundary, baseP=-10, max_min='max', dpi=100, numline=np.arange(step, np.max(joint_copen) + 2 * step, step))
    plt.tight_layout()
    return fig, XX, YY, joint_copen, boundarys, holes, concen


def dmgt_contour(fname, coordinate_nodes, bounds, nodes_data, fontsize=16, holes=None, cbar_ratio=1.0):
    """绘制损伤分布图

    Args:
        fname (string): 损伤数据文件路径
        coordinate_nodes (numpy.array): 局部坐标系，如果为一维数组，则表示确定局部坐标系的三个结点的编号；如果为二维数组，则表示确定局部坐标系三个结点的坐标。三个结点依次为x轴上的结点、xy平面上的结点和坐标原点
        bounds (list): 边界结点文件列表
        nodes_data (numpy.array(n, 4)): 所有结点的编号和坐标，第一列为结点编号
        fontsize (int, optional): 极值点数据字体大小，默认为16.
        holes (string): 孔洞文件，默认为None

    Returns:
        fig (plt.figure): 图片句柄
        xx (np.array(n)): 数据点的横坐标数组
        yy (np.array(n)): 数据点的纵坐标数组
        damage (np.array(n)): 数据点的值
    """
    # 读取损伤因子分布数据
    damage_data = pd.read_csv(fname, encoding='gbk')
    damage_data.rename(columns={'      结点编号': 'node', '       DAMAGET': 'damage'}, inplace=True)
    damage_data.drop_duplicates(subset='node', keep='first', inplace=True)
    damage = np.array(damage_data['damage'])
    damage[damage > 1.0] = 1.0  # 将损伤因子大于1的值置为1
    section_nodes_coord = np.array(damage_data[['X', 'Y', 'Z']])
    xy = change_coord(coordinate_nodes, section_nodes_coord, nodes_data)
    xx, yy = xy[:, 0], xy[:, 1]
    # 如果存在孔洞
    if holes is not None:
        holes_nodes = np.loadtxt(holes)
        holes = []
        for i in range(holes_nodes.shape[0]):
            hole_coord = change_coord(coordinate_nodes, holes_nodes[i, :], nodes_data)
            holes.append([tuple(v) for v in list(hole_coord)])
    if len(bounds) == 1:  # 如果只有一个边界
        bound_nodes = np.loadtxt(bounds[0])
        bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
        boundary = [tuple(v) for v in list(bound_coord)]
        fig = plt.figure(figsize=(6.1, 4.4))
        try:
            X, Y, vdamage = getContour(xx, yy, damage, boundary, baseP=-100, flag=0, holes=holes, Extrapolation=0)
        except:
            X, Y, vdamage = getContour(xx, yy, damage, boundary, baseP=-100, flag=0, holes=holes, Extrapolation=1)
        Cd = plt.contourf(X, Y, vdamage, vmin=0.2, cmap=cmp, levels=np.linspace(0.0, 1.0, 11))
        bd = np.array(boundary)
        plt.plot(bd[:, 0], bd[:, 1], color='k', linewidth=2)
        if holes is not None:
            for hole in holes:
                hl = np.array(hole)
                plt.plot(hl[:, 0], hl[:, 1], color='k', linewidth=1.5, zorder=3)
                plt.fill(hl[:, 0], hl[:, 1], 'w', zorder=2)
        idx = np.argmax(damage)
        plt.scatter(xx[idx], yy[idx], color='b', marker='*')
        plt.text(xx[idx], yy[idx], str('%.2f' % damage[idx]), color='b', fontsize=fontsize)
        plt.gca().set_aspect(1)
        plt.gca().set_axis_off()
        cbar = plt.colorbar(Cd, shrink=cbar_ratio)
        cbar.set_ticks(np.linspace(0.0, 1.0, 11))
    else:  # 如果有多个边界
        fig = plt.figure(figsize=(6.1, 4.4))
        for bound in bounds:
            bound_nodes = np.loadtxt(bound)
            bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
            boundary = [tuple(v) for v in list(bound_coord)]
            try:
                X, Y, vdamage = getContour(xx, yy, damage, boundary, baseP=-100, flag=0, holes=holes, Extrapolation=0)
            except:
                X, Y, vdamage = getContour(xx, yy, damage, boundary, baseP=-100, flag=0, holes=holes, Extrapolation=1)
            cd = plt.contourf(X, Y, vdamage, vmin=0.2, cmap=cmp, levels=np.linspace(0.0, 1.0, 11))
            bd = np.array(boundary)
            plt.plot(bd[:, 0], bd[:, 1], color='k', linewidth=2)
            idx = np.argmax(damage)
            plt.scatter(xx[idx], yy[idx], color='b', marker='*')
            plt.text(xx[idx], yy[idx], str('%.2f' % damage[idx]), color='b', fontsize=fontsize)
        if holes is not None:
            for hole in holes:
                hl = np.array(hole)
                plt.plot(hl[:, 0], hl[:, 1], color='k', linewidth=1.5, zorder=3)
                plt.fill(hl[:, 0], hl[:, 1], 'w', zorder=2)
        plt.gca().set_aspect(1)
        plt.gca().set_axis_off()
        cbar = plt.colorbar(cd, shrink=cbar_ratio)
        cbar.set_ticks(np.linspace(0.0, 1.0, 11))
    plt.tight_layout()
    return fig, xx, yy, damage


def acc_history(fname, node, direc, PGA=None, fontsize=16):
    """绘制加速度时程曲线

    Args:
        fname (string): 加速度数据文件路径
        node (string): 结点，分为坝顶结点、坝踵结点和其他结点，一般为坝顶结点
        direc (string): 加速度方向，分为X和Y向
        PGA (string, optional): 输入加速度的PGA，默认为None，用于绘制放大倍数曲线.
        fontsize (int, optional): 字体大小，默认为16.

    Returns:
        fig (plt.figure): 图片句柄
        t (numpy.array(n)): 时间数组
        acc (numpy.array(n)): 加速度或放大倍数数组
    """
    accdata = np.loadtxt(fname, skiprows=4)
    accdata[:, 0] -= accdata[0, 0]  # 减去初始时间（静力分析步的时间）
    accdata[:, 1:] /= 9.81  # 转换单位为g
    t = accdata[:, 0]
    if direc == 'X':
        acc = accdata[:, 1 : 4]
    elif direc == 'Y':
        acc = accdata[:, 4 : 7]
    else:
        acc = accdata[:, 7 : 10]
    if node == '坝顶结点':
        acc = acc[:, 0]
    elif node == '坝踵结点':
        acc = acc[:, 1]
    else:
        acc = acc[:, 2]
    fig = plt.figure(figsize=(6.1, 3))
    if PGA is None:  # 如果没有提供PGA，则绘制加速度时程曲线
        plt.plot(t, acc, label='%s向' % direc, color='k', linewidth=1)
        idx = np.argmax(np.abs(acc))
        acc_max = np.max(np.abs(acc))
        plt.scatter(t[idx], acc[idx], color='r', marker='*')
        plt.text(t[idx] + 1, 0.95 * acc[idx], str('%.2f' % acc[idx]), color='r', fontsize=fontsize + 2)
        plt.ylim([-1.1 * acc_max, 1.1 * acc_max])
        plt.tick_params(labelsize=fontsize - 2)
        plt.xlabel('t (s)', fontsize=fontsize)
        plt.ylabel('acc (g)', fontsize=fontsize)
        plt.legend(loc='upper right', prop={'family': 'SimHei', 'size': fontsize})
    else:  # 如果提供了PGA，绘制放大倍数曲线
        acc /= PGA
        plt.plot(t, acc, label='%s向' % direc, color='k', linewidth=1)
        idx = np.argmax(np.abs(acc))
        acc_max = np.max(np.abs(acc))
        plt.scatter(t[idx], acc[idx], color='r', marker='*')
        plt.text(t[idx] + 1, 0.95 * acc[idx], str('%.2f' % acc[idx]), color='r', fontsize=fontsize + 2)
        plt.ylim([-1.1 * acc_max, 1.1 * acc_max])
        plt.tick_params(labelsize=fontsize - 2)
        plt.xlabel('t (s)', fontsize=fontsize)
        plt.ylabel('放大倍数', font={'family':'SimHei', 'size': fontsize})
        plt.legend(loc='upper right', prop={'family': 'SimHei', 'size': fontsize})
    plt.tight_layout()
    return fig, t, acc


def dyn_disp(fname, coordinate_nodes, nodes, ref_node='0,0'):
    """动力位移数据处理

    Args:
        fname (string): 动力位移数据文件路径
        coordinate_nodes (numpy.array): 局部坐标系，如果为一维数组，则表示确定局部坐标系的三个结点的编号；如果为二维数组，则表示确定局部坐标系三个结点的坐标。三个结点依次为x轴上的结点、xy平面上的结点和坐标原点
        nodes (numpy.array(n, 3)): 所有结点的坐标
        ref_node (string, optional): 参考结点坐标或者编号，默认为'0,0'，输入一个整数则表示编号，输入一个坐标则表示坐标.

    Returns:
        disp_max (numpy.array(n, 2)): 最大位移包络数据
        disp_min (numpy.array(n, 2)): 最小位移包络数据
        xx (numpy.array(n)): 数据结点的横坐标
        yy (numpy.array(n)): 数据结点的纵坐标
    """
    disp_data = pd.read_csv(fname, encoding='gbk')
    # 获取结点数
    num_node = 0
    while disp_data.iloc[num_node]['X'] != 'X':
        num_node += 1
    # 获取帧数
    frames = int(len(disp_data) / (num_node + 1))
    # 将位移数据整理成三维数组
    disp = []
    for i in range(frames):
        a = np.array(disp_data.iloc[(num_node + 1)*i : (num_node + 1)*(i+1)-1, 4:8]).astype(float)  # 结点坐标
        b = np.array(disp_data.iloc[(num_node + 1)*i : (num_node + 1)*(i+1)-1, 11:14]).astype(float)  # 结点位移
        c = np.concatenate((a, b), axis=1)  # 按列拼接
        disp.append(c)
    disp = np.array(disp)
    section_nodes_coord = disp[0, :, 1 : 4]
    xyU = change_coord(coordinate_nodes, section_nodes_coord, nodes)  # 转换剖面结点坐标
    # 减去参考点（一般是坝踵）位移，求相对位移
    if ',' in ref_node:  # 如果输入是一个坐标（转换后的坐标）
        ref = ref_node.split(',')
        ref = [float(val) for val in ref]
        org_node = np.where((xyU[:, 0] - ref[0]) ** 2 + (xyU[:, 1] - ref[1]) ** 2 < 1)
        org_node = np.min(org_node)
        for i in range(disp.shape[0]):
            disp[i, :, 4:] -= disp[i, org_node, 4:]
    else:  # 如果输入是一个结点编号
        org_node = list(disp[0, :, 0]).index(int(ref_node))
        for i in range(disp.shape[0]):
            disp[i, :, 4:] -= disp[i, org_node, 4:]
    # 求最大最小位移包络
    disp_max = np.max(disp[:, :, 4 : 7], axis=0)
    disp_min = np.min(disp[:, :, 4 : 7], axis=0)
    xx = xyU[:, 0]
    yy = xyU[:, 1]
    return disp_max, disp_min, xx, yy


def dyn_disp_contour(xx, yy, zz, coordinate_nodes, bounds, nodes_data, holes=None, concen=None, concen_dist=0):
    """绘制动力位移等值线图

    Args:
        xx (numpy.array(n)): 数据点的横坐标
        yy (numpy.array(n)): 数据点的纵坐标
        zz (numpy.array(n)): 数据点的值
        coordinate_nodes (numpy.array): 局部坐标系，如果为一维数组，则表示确定局部坐标系的三个结点的编号；如果为二维数组，则表示确定局部坐标系三个结点的坐标。三个结点依次为x轴上的结点、xy平面上的结点和坐标原点
        bounds (list): 边界结点文件列表
        nodes_data (numpy.array(n, 4)): 所有结点的编号和坐标，第一列为结点编号
        holes (string): 孔洞文件，默认为None
        concen (string): 应力集中区域文件，默认为None
        concen_dist (float): 集中点距离，默认为0

    Returns:
        fig (plt.figure): 图片句柄
        xxU (np.array(n)): 数据点的横坐标数组
        yyU (np.array(n)): 数据点的纵坐标数组
        zzU (np.array(n)): 数据点的值
        boundarys (list): 边界结点列表，用于重绘
        holes (list): 孔洞列表，用于重绘
        concen (string): 应力集中区域文件，默认为None
    """
    # 如果需要删除一些应力集中点
    if concen is not None:
        concen_nodes = np.loadtxt(concen)
        concen_coord = change_coord(coordinate_nodes, concen_nodes, nodes_data)
        xx_dele, yy_dele, zz_dele = [], [], []
        for i in range(len(xx)):
            dist = np.sqrt((concen_coord[:, 0] - xx[i]) ** 2 + (concen_coord[:, 1] - yy[i]) ** 2)
            if np.min(dist) > concen_dist:
                xx_dele.append(xx[i])
                yy_dele.append(yy[i])
                zz_dele.append(zz[i])
        xx = np.array(xx_dele)
        yy = np.array(yy_dele)
        zz = np.array(zz_dele)
    # 加载孔洞数据
    if holes is not None:
        holes_nodes = np.loadtxt(holes)
        holes = []
        for i in range(holes_nodes.shape[0]):
            hole_coord = change_coord(coordinate_nodes, holes_nodes[i, :], nodes_data)
            holes.append([tuple(v) for v in list(hole_coord)])

    boundarys = []
    if len(bounds) == 1:  # 如果只有一个边界
        bound_nodes = np.loadtxt(bounds[0])
        bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
        boundary = [tuple(v) for v in list(bound_coord)]
        boundarys.append(boundary)
        fig = plt.figure(figsize=(6.1, 4.4))
        try:
            X, Y, ZU, hd = getContour(xx, yy, zz, boundary, dpi=100, Extrapolation=0, holes=holes)
        except:
            X, Y, ZU, hd = getContour(xx, yy, zz, boundary, dpi=100, Extrapolation=1, holes=holes)
    else:  # 如果有多个边界
        zzU_max = np.max(zz)
        zzU_min = np.min(zz)
        numline = np.arange(zzU_min, zzU_max, (zzU_max - zzU_min) / 10)
        fig = plt.figure(figsize=(6.1, 4.4))
        for bound in bounds:
            bound_nodes = np.loadtxt(bound)
            bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
            boundary = [tuple(v) for v in list(bound_coord)]
            boundarys.append(boundary)
            try:
                X, Y, ZU, hd = getContour(xx, yy, zz, boundary, numline=numline, dpi=100, Extrapolation=0, holes=holes)
            except:
                X, Y, ZU, hd = getContour(xx, yy, zz, boundary, numline=numline, dpi=100, Extrapolation=1, holes=holes)
    plt.tight_layout()
    return fig, xx, yy, zz, boundarys, holes, concen


def dyn_S_env_contour(fname, coordinate_nodes, bounds, nodes_data, component='Smax', holes=None, concen=None, concen_dist=0):
    """绘制动力应力包络等值线图

    Args:
        fname (string): 动力应力数据文件路径
        coordinate_nodes (numpy.array): 局部坐标系，如果为一维数组，则表示确定局部坐标系的三个结点的编号；如果为二维数组，则表示确定局部坐标系三个结点的坐标。三个结点依次为x轴上的结点、xy平面上的结点和坐标原点
        bounds (list): 边界结点文件列表
        nodes_data (numpy.array(n, 4)): 所有结点的编号和坐标，第一列为结点编号
        component (string): 应力分量，Smax表示大主应力，Smin表示小主应力，默认为Smax
        holes (string): 孔洞文件，默认为None
        concen (string): 应力集中区域文件，默认为None
        concen_dist (float): 集中点距离，默认为0

    Returns:
        fig (plt.figure): 图片句柄
        xxS (np.array(n)): 数据点的横坐标数组
        yyS (np.array(n)): 数据点的纵坐标数组
        zzS (np.array(n)): 数据点的值
        boundarys (list): 边界结点列表，用于重绘
        holes (list): 孔洞列表，用于重绘
        concen (string): 应力集中区域文件，默认为None
    """
    # 获取应力数据
    stre_data = pd.read_csv(fname, encoding='gbk')
    stre_data.rename(columns={'      结点编号': 'node'}, inplace=True)
    stre_data.drop_duplicates(subset='node', keep='first', inplace=True)
    stre_data = stre_data.sort_values(by='node')  # 按结点排序
    section_nodes_coord = np.array(stre_data[['X', 'Y', 'Z']])
    if component == 'Smax':
        zzS = np.array(stre_data['S_max-Max. Principal'] / 1e6)
        max_min = 'max'
    elif component == 'Smin':
        zzS = np.array(stre_data['S_min-Min. Principal'] / 1e6)
        max_min = 'min'
    xyS = change_coord(coordinate_nodes, section_nodes_coord, nodes_data)  # 转换剖面结点坐标
    # 如果需要删除一些应力集中点
    if concen is not None:
        concen_nodes = np.loadtxt(concen)
        concen_coord = change_coord(coordinate_nodes, concen_nodes, nodes_data)
        xys_dele, zzS_dele = [], []
        for i in range(xyS.shape[0]):
            dist = np.sqrt(np.sum((concen_coord - xyS[i, :]) ** 2, axis=1))
            if np.min(dist) > concen_dist:  # 判断该剖面结点离应力集中区域最小的距离是否大于集中点距离
                xys_dele.append(xyS[i, :])
                zzS_dele.append(zzS[i])
        xyS = np.array(xys_dele)
        zzS = np.array(zzS_dele)
    xxS, yyS = xyS[:, 0], xyS[:, 1]
    # 如果有孔洞
    if holes is not None:
        holes_nodes = np.loadtxt(holes)
        holes = []
        for i in range(holes_nodes.shape[0]):
            hole_coord = change_coord(coordinate_nodes, holes_nodes[i, :], nodes_data)
            holes.append([tuple(v) for v in list(hole_coord)])
    boundarys = []
    if len(bounds) == 1:  # 如果只有一个边界
        bound_nodes = np.loadtxt(bounds[0])
        bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
        boundary = [tuple(v) for v in list(bound_coord)]
        boundarys.append(boundary)
        fig = plt.figure(figsize=(6.1, 4.4))
        try:
            X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, dpi=100, Extrapolation=1, max_min=max_min, holes=holes)
        except:
            X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, dpi=100, Extrapolation=0, max_min=max_min, holes=holes)
    else:  # 如果有多个边界
        zzS_max = np.max(zzS)
        zzS_min = np.min(zzS)
        numline = np.arange(zzS_min, zzS_max, (zzS_max - zzS_min) / 10)
        fig = plt.figure(figsize=(6.1, 4.4))
        for bound in bounds:
            bound_nodes = np.loadtxt(bound)
            bound_coord = change_coord(coordinate_nodes, bound_nodes, nodes_data)
            boundary = [tuple(v) for v in list(bound_coord)]
            boundarys.append(boundary)
            try:
                X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, numline=numline, dpi=100, Extrapolation=1, max_min=max_min, holes=holes)
            except:
                X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, numline=numline, dpi=100, Extrapolation=0, max_min=max_min, holes=holes)
    plt.tight_layout()
    return fig, xxS, yyS, zzS, boundarys, holes, concen


def dyn_joint_contour(joint, bounds, coordinate, copen_data, copen_id, nodes, holes=None, concen=None):
    """绘制动力横缝开度分布图

    Args:
        joint (string): 横缝标志
        bounds (string): 边界结点文件
        coordinate (numpy.array): 局部坐标系结点编号
        copen_data (list): 所有横缝开度数据
        copen_id (list): 所有横缝的标志
        nodes (numpy.array(n, 4)): 所有结点坐标
        holes (list): 孔洞列表，用于重绘
        concen (string): 应力集中区域文件，默认为None

    Returns:
        fig (plt.figure): 图片句柄
        XX (np.array(n)): 数据点的横坐标数组
        YY (np.array(n)): 数据点的纵坐标数组
        joint_copen (np.array(n)): 数据点的值
        boundarys (list): 边界结点列表，用于重绘
        holes (list): 孔洞列表，用于重绘
        concen (string): 应力集中区域文件，默认为None
    """
    bound_nodes = np.loadtxt(bounds)  # 读取边界结点文件
    # 获取横缝
    for i in range(len(copen_id)):
        if joint.upper() in copen_id[i]:
            idx = i
    # 获取横缝开度数据
    joint_node_id = copen_data[idx][:, 0, 0].ravel().astype(np.int64)
    joint_copen = 1000 * np.max(copen_data[idx][:, 2, :],axis=1).ravel()
    joint_copen[joint_copen <= 5e-6] = 0

    all_nodes_id = nodes[:, 0].astype(np.int64)
    all_nodes_coord = nodes[:, 1:]
    # 获取横缝结点坐标
    joint_node_coord = np.zeros((joint_node_id.shape[0], 3))
    for i in range(joint_node_id.shape[0]):
        joint_node_coord[i, :] = all_nodes_coord[all_nodes_id == joint_node_id[i], :]

    boundarys = []
    XX, YY, boundary = transform_coord(coordinate, bound_nodes, joint_node_coord, nodes)
    boundarys.append(boundary)
    fig = plt.figure(figsize=(6.1, 4.4))
    X, Y, vCopen, hd = getContour(XX, YY, joint_copen, boundary, baseP=-10, max_min='max', dpi=100)
    plt.tight_layout()
    return fig, XX, YY, joint_copen, boundarys, holes, concen


def dyn_slide(KK, dt):
    """动力抗滑稳定安全系数时程图的绘制

    Args:
        KK (numpy.array(n)): 动力抗滑稳定安全系数数组
        dt (float): 时间间隔

    Returns:
        fig (plt.figure): 图片句柄
        t (numpy.array(n)): 时间序列
    """
    t = np.arange(0, dt * len(KK), dt)
    idx = np.argmin(KK)
    fig = plt.figure(figsize=(6.1, 3))
    plt.plot(t, KK, color='k', linewidth=1)  # 绘制抗滑稳定安全系数时程曲线
    plt.plot([t[0], t[-1]], [1, 1], linewidth=2, color='r')  # 绘制1的那条红线
    plt.scatter(t[idx], KK[idx], color='r', marker='*')  # 绘制最低点
    plt.text(t[idx], KK[idx], str('%.2f' % KK[idx]), color='r', fontsize=22)  # 标记最低点数值
    plt.xlabel('t (s)')
    plt.ylabel('$\gamma_d^*$')
    plt.xlim([t[0], t[-1]])
    plt.ylim([0, 10])  # 只显示安全系数10以内的内容
    plt.tight_layout()
    return fig, t