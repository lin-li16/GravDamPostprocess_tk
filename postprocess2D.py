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


def kanghua(data, f, c, phi, gamma_0, gamma_d, gamma_f, gamma_c):
    """计算二维层面抗滑稳定安全系数

    Args:
        data (pandas.Dataframe): 抗滑稳定数据表格
        f (float): 抗剪断参数f'
        c (float): 抗剪断参数c'
        phi (float): 设计状况系数，持久状况取1.0，偶然状况取0.85.
        gamma_0 (float): 结构重要性系数,分级I级取1.1.
        gamma_d (float): 抗滑稳定结构系数，静力工况取1.5，动力工况取0.65.
        gamma_f (float): 摩擦系数材料性能分项系数，取1.7.
        gamma_c (float): 粘聚力材料性能分项系数，取2.0.

    Returns:
        result (float): 抗滑稳定安全系数，大于1表示校核通过.
    """
    f /= gamma_f
    c /= gamma_c    
    data.drop_duplicates(subset='node', keep='first', inplace=True)
    data['X'] = pd.to_numeric(data['X'])
    data = data.sort_values(by='X')
    X = np.array(data['X']).astype(np.float64)
    S22 = np.array(data['S-S22']).astype(np.float64)
    S12 = np.array(data['S-S12']).astype(np.float64)
    A = np.zeros_like(X)
    A[1 : -1] = (X[2:] - X[:-2]) / 2
    A[0] = (X[1] - X[0]) / 2
    A[-1] = (X[-1] - X[-2]) / 2
    R = np.sum(S22 * A)
    S = np.sum(S12 * A)
    R = c * np.sum(A) * 1.0e6 - f * np.min([0.0, R])
    result = R / (np.abs(S) * gamma_0 * phi * gamma_d)
    return result
    

def sta_disp_contour(fname, boundary, direc='X'):
    """绘制静力位移等值线图

    Args:
        fname (string): 静力位移数据文件路径
        boundary (list): 边界列表，每个元素是一个元组，表示结点坐标，结点按逆时针或者顺时针排序
        direc (string): 位移方向，分X向和Y向，默认为'X'.

    Returns:
        fig (plt.figure): 图片句柄
        xxU (np.array(n)): 数据点的横坐标数组
        yyU (np.array(n)): 数据点的纵坐标数组
        zzU (np.array(n)): 数据点的值
    """
    disp_data = pd.read_csv(fname, encoding='gbk')
    disp_data.rename(columns={'      结点编号': 'node', '          U-U1': 'U-U1', '          U-U2': 'U-U2'}, inplace=True)
    xxU = np.array(disp_data['X'])
    yyU = np.array(disp_data['Y'])
    if direc == 'X':
        zzU = np.array(disp_data['U-U1'] * 100)
    else:
        zzU = np.array(disp_data['U-U2'] * 100)
    fig = plt.figure(figsize=(6.1, 4.4))
    try:
        X, Y, ZU, hd = getContour(xxU, yyU, zzU, boundary, dpi=100, Extrapolation=0)
    except:
        X, Y, ZU, hd = getContour(xxU, yyU, zzU, boundary, dpi=100, Extrapolation=1)
    plt.tight_layout()
    return fig, xxU, yyU, zzU


def sta_stre_contour(fname, boundary, component='Smax', max_min='abs'):
    """绘制静力应力等值线图

    Args:
        fname (string): 静力应力数据文件路径
        boundary (list): 边界列表，每个元素是一个元组，表示结点坐标，结点按逆时针或者顺时针排序
        component (string): 应力分量，Smax表示大主应力，Smin表示小主应力，默认为Smax
        max_min (string): 极值点显示类别，abs表示显示绝对值最大，max表示最大值，min表示最小值，默认为abs

    Returns:
        fig (plt.figure): 图片句柄
        xxS (np.array(n)): 数据点的横坐标数组
        yyS (np.array(n)): 数据点的纵坐标数组
        zzS (np.array(n)): 数据点的值
    """
    stre_data = pd.read_csv(fname, encoding='gbk')
    stre_data.rename(columns={'      结点编号': 'node'}, inplace=True)
    stre_data.drop_duplicates(subset='node', keep='first', inplace=True)
    xxS = np.array(stre_data['X'])
    yyS = np.array(stre_data['Y'])
    if component == 'Smax':
        zzS = np.array(stre_data['S-Max. In-Plane Principal'] / 1e6)
        max_min = 'max'
    elif component == 'Smin':
        zzS = np.array(stre_data['S-Min. In-Plane Principal'] / 1e6)
        max_min = 'min'
    fig = plt.figure(figsize=(6.1, 4.4))
    try:
        X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, dpi=100, Extrapolation=1, max_min=max_min)
    except:
        X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, dpi=100, Extrapolation=0, max_min=max_min)
    plt.tight_layout()
    return fig, xxS, yyS, zzS


def sta_slide(fname, ff, cc, phi=1.0, gamma_0=1.1, gamma_d=1.5, gamma_f=1.7, gamma_c=2.0):
    """静力抗滑稳定安全系数计算

    Returns:
        result (float): 抗滑稳定安全系数，大于1表示校核通过.

    Args:
        fname (string): 静力抗滑稳定数据文件路径
        ff (float): 抗剪断参数f'
        cc (float): 抗剪断参数c'
        phi (float): 设计状况系数，持久状况取1.0，偶然状况取0.85.
        gamma_0 (float): 结构重要性系数,分级I级取1.1.
        gamma_d (float): 抗滑稳定结构系数，静力工况取1.5，动力工况取0.65.
        gamma_f (float): 摩擦系数材料性能分项系数，取1.7.
        gamma_c (float): 粘聚力材料性能分项系数，取2.0.

    Returns:
        result (float): 抗滑稳定安全系数，大于1表示校核通过.
    """
    data0 = pd.read_csv(fname, encoding='gbk')
    data0.rename(columns={'      结点编号': 'node', '         S-S22': 'S-S22', '         S-S12': 'S-S12'}, inplace=True)
    result = kanghua(data=data0, f=ff, c=cc, phi=phi, gamma_0=gamma_0, gamma_d=gamma_d, gamma_f=gamma_f, gamma_c=gamma_c)
    return result


def dmgt_contour(fname, boundary, fontsize=16):
    """绘制损伤分布图

    Args:
        fname (string): 损伤数据文件路径
        boundary (list): 边界列表，每个元素是一个元组，表示结点坐标，结点按逆时针或者顺时针排序
        fontsize (int, optional): 极值点数据字体大小，默认为16.

    Returns:
        fig (plt.figure): 图片句柄
        xx (np.array(n)): 数据点的横坐标数组
        yy (np.array(n)): 数据点的纵坐标数组
        damage (np.array(n)): 数据点的值
    """
    damage_data = pd.read_csv(fname, encoding='gbk')
    damage_data.rename(columns={'      结点编号': 'node', '       DAMAGET': 'damage'}, inplace=True)
    damage_data.drop_duplicates(subset='node', keep='first', inplace=True)
    xx = np.array(damage_data['X'])
    yy = np.array(damage_data['Y'])
    damage = np.array(damage_data['damage'])
    damage[damage > 1.0] = 1.0

    fig = plt.figure(figsize=(6.1, 4.4))
    X, Y, vdamage = getContour(xx, yy, damage, boundary, baseP=-100, flag=0)
    Cd = plt.contourf(X, Y, vdamage, vmin=0.2, cmap=cmp, levels=np.linspace(0.0, 1.0, 11))
    bd = np.array(boundary)
    cmax = np.max(bd, axis=0)
    cmin = np.min(bd, axis=0)
    plt.plot(bd[:, 0], bd[:, 1], color='k', linewidth=2)
    idx = np.argmax(damage)
    plt.scatter(xx[idx], yy[idx], color='r', marker='*')
    plt.text(xx[idx], yy[idx], str('%.2f' % damage[idx]), color='r', fontsize=fontsize)
    plt.xlim([cmin[0], cmax[0]])
    plt.ylim([cmin[1], cmax[1]])
    plt.gca().set_aspect(1)
    plt.gca().set_axis_off()
    cbar = plt.colorbar(Cd, shrink=1.0)
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
    else:
        acc = accdata[:, 4 : 7]
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


def dyn_disp(fname, ref_node='0,0', nodes=None):
    """动力位移数据处理

    Args:
        fname (string): 动力位移数据文件路径
        ref_node (string, optional): 参考结点坐标或者编号，默认为'0,0'，输入一个整数则表示编号，输入一个坐标则表示坐标.
        nodes (numpy.array(n, 3), optional): 所有结点的坐标，默认为None，当ref_node为结点编号时才需要用到.

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
        a = np.array(disp_data.iloc[(num_node + 1)*i : (num_node + 1)*(i+1)-1, 4:7]).astype(float)
        b = np.array(disp_data.iloc[(num_node + 1)*i : (num_node + 1)*(i+1)-1, 11:13]).astype(float)
        c = np.concatenate((a, b), axis=1)
        disp.append(c)
    disp = np.array(disp)
    # 减去参考点（一般是坝踵）位移，求相对位移
    if nodes is not None and ',' in ref_node:  # 如果输入是一个坐标
        ref = ref_node.split(',')
        ref = [float(val) for val in ref]
        org_node = np.where((disp[0, :, 1] - ref[0]) ** 2 + (disp[0, :, 2] - ref[1]) ** 2 < 1)
        org_node = np.min(org_node)
        for i in range(disp.shape[0]):
            disp[i, :, 3:] -= disp[i, org_node, 3:]
    else:  # 如果输入是一个结点编号
        ref = nodes[nodes[:, 0] == int(ref_node)][0, 1:]
        org_node = np.where((disp[0, :, 1] - ref[0]) ** 2 + (disp[0, :, 2] - ref[1]) ** 2 < 1)
        org_node = np.min(org_node)
        for i in range(disp.shape[0]):
            disp[i, :, 3:] -= disp[i, org_node, 3:]
    # 求最大最小位移包络
    disp_max = np.max(disp[:, :, 3 : 5], axis=0)
    disp_min = np.min(disp[:, :, 3 : 5], axis=0)
    xx = disp[0, :, 1]
    yy = disp[0, :, 2]
    return disp_max, disp_min, xx, yy


def dyn_S_env_contour(fname, boundary, component='Smax', max_min='abs'):
    """绘制动力大小主应力包络图

    Args:
        fname (string): 动力应力包络数据文件路径
        boundary (list): 边界列表，每个元素是一个元组，表示结点坐标，结点按逆时针或者顺时针排序
        component (string, optional): 应力分量，Smax表示大主应力，Smin表示小主应力，默认为Smax
        max_min (string, optional): 极值点显示类别，abs表示显示绝对值最大，max表示最大值，min表示最小值，默认为abs

    Returns:
        fig (plt.figure): 图片句柄
        xxS (np.array(n)): 数据点的横坐标数组
        yyS (np.array(n)): 数据点的纵坐标数组
        zzS (np.array(n)): 数据点的值
    """
    stre_data = pd.read_csv(fname, encoding='gbk')
    stre_data.rename(columns={'      结点编号': 'node'}, inplace=True)
    stre_data.drop_duplicates(subset='node', keep='first', inplace=True)
    xxS = np.array(stre_data['X'])
    yyS = np.array(stre_data['Y'])
    if component == 'Smax':
        zzS = np.array(stre_data['S_max-Max. In-Plane Principal'] / 1e6)
    elif component == 'Smin':
        zzS = np.array(stre_data['S_min-Min. In-Plane Principal'] / 1e6)
    fig = plt.figure(figsize=(6.1, 4.4))
    try:
        X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, dpi=100, Extrapolation=1, max_min=max_min)
    except:
        X, Y, ZS, hd = getContour(xxS, yyS, zzS, boundary, dpi=100, Extrapolation=0, max_min=max_min)
    plt.tight_layout()
    return fig, xxS, yyS, zzS


def dyn_slide(fname, ff, cc, phi=0.85, gamma_0=1.1, gamma_d=0.65, gamma_f=1.7, gamma_c=2.0, dt=0.01, fontsize=16):
    """静力抗滑稳定安全系数计算

    Returns:
        result (float): 抗滑稳定安全系数，大于1表示校核通过.

    Args:
        fname (string): 静力抗滑稳定数据文件路径
        ff (float): 抗剪断参数f'
        cc (float): 抗剪断参数c'
        phi (float, optional): 设计状况系数，持久状况取1.0，偶然状况取0.85.
        gamma_0 (float, optional): 结构重要性系数,分级I级取1.1.
        gamma_d (float, optional): 抗滑稳定结构系数，静力工况取1.5，动力工况取0.65.
        gamma_f (float, optional): 摩擦系数材料性能分项系数，取1.7.
        gamma_c (float, optional): 粘聚力材料性能分项系数，取2.0.

    Returns:
        result (float): 抗滑稳定安全系数，大于1表示校核通过.
    """
    """动力抗滑稳定安全系数时程曲线绘制

    Args:
        fname (string): 动力抗滑稳定数据文件路径
        ff (float): 抗剪断参数f'
        cc (float): 抗剪断参数c'
        phi (float, optional): 设计状况系数，持久状况取1.0，偶然状况取0.85.
        gamma_0 (float, optional): 结构重要性系数,分级I级取1.1.
        gamma_d (float, optional): 抗滑稳定结构系数，静力工况取1.5，动力工况取0.65.
        gamma_f (float, optional): 摩擦系数材料性能分项系数，取1.7.
        gamma_c (float, optional): 粘聚力材料性能分项系数，取2.0.
        dt (float, optional): 时间间隔，默认为0.01.
        fontsize (int, optional): 字体大小，默认为16.

    Returns:
        fig (plt.figure): 图片句柄
        t (numpy.array(n)): 时间数组
        yd (numpy.array(n)): 抗滑稳定安全系数数组
        fail_time (float): 抗滑稳定安全校核不通过时长
    """
    data = pd.read_csv(fname, encoding='gbk')
    data.rename(columns={'      结点编号': 'node', '         S-S22': 'S-S22', '         S-S12': 'S-S12'}, inplace=True)
    # 获取层面结点数量
    i = 0
    while data.iloc[i]['X'] != 'X':
        i += 1
    numnode = i
    # 获取帧数
    numstep = int((len(data) + 1) / (numnode + 1))
    yd = []
    fail_time = 0
    for step in range(numstep):
        datai = data.iloc[step * (numnode + 1) : (step + 1) * (numnode + 1) - 1]  # 当前帧的数据表格
        ydi = kanghua(data=datai, f=ff, c=cc, phi=phi, gamma_0=gamma_0, gamma_d=gamma_d, gamma_f=gamma_f, gamma_c=gamma_c)
        if ydi < 1.0:
            fail_time += 1
        yd.append(ydi)
    fail_time *= dt
    t = np.arange(0, dt * numstep, dt)
    idx = np.argmin(yd)
    # 绘图
    fig = plt.figure(figsize=(6.1, 3))
    plt.plot(t, yd, color='k', linewidth=1)
    plt.plot([t[0], t[-1]], [1, 1], linewidth=2, color='r')
    plt.scatter(t[idx], yd[idx], color='r', marker='*')
    plt.text(t[idx], yd[idx], str('%.2f' % yd[idx]), color='r', fontsize=22)
    plt.tick_params(labelsize=fontsize - 2)
    plt.xlabel('t (s)', fontsize=fontsize)
    plt.ylabel('$\gamma_d^*$', fontsize=fontsize)
    plt.xlim([t[0], t[-1]])
    plt.ylim([0, 10])
    plt.tight_layout()
    return fig, t, yd, fail_time