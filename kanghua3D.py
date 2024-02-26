import numpy as np
import tqdm
import pandas as pd


def nodes2xyz(nodeP, nodeQ, nodeR):
    """由三个点的坐标求坐标系的三个基准单位向量.

    Args:
        nodeP (numpy.array(1, 3)): 原点坐标.
        nodeQ (numpy.array(1, 3)): x轴上一点的坐标.
        nodeR (numpy.array(1, 3)): xy平面上一点的坐标.

    Returns:
        vec_x (numpy.array(1, 3)): 坐标系的x方向单位向量.
        vec_y (numpy.array(1, 3)): 坐标系的y方向单位向量.
        vec_z (numpy.array(1, 3)): 坐标系的z方向单位向量.
    """
    vec_x = (nodeQ - nodeP) / np.linalg.norm((nodeQ - nodeP))
    vec_y = (nodeR - nodeP) - (nodeR - nodeP).dot(vec_x) * vec_x
    vec_y = vec_y / np.linalg.norm(vec_y)
    vec_z = np.cross(vec_x, vec_y)
    return vec_x, vec_y, vec_z


def get_vec_xyz(node_id, nodes_data):
    """根据坐标系结点编号，从总结点坐标列表里求坐标系三个基准单位向量.

    Args:
        node_id (numpy.array(1, 3)): 坐标系结点编号，三个结点，分别为x轴上的结点，xy平面上的结点，原点.
        nodes_data (numpy.array(n, 4)): 总结点坐标列表，第一列为结点编号，后三列分别为xyz坐标值.

    Returns:
        numpy.array(1, 3): 坐标系的三个基准单位向量.
    """
    nodeP = nodes_data[nodes_data[:, 0] == node_id[2]][0, 1:]
    nodeQ = nodes_data[nodes_data[:, 0] == node_id[0]][0, 1:]
    nodeR = nodes_data[nodes_data[:, 0] == node_id[1]][0, 1:]
    return nodes2xyz(nodeP, nodeQ, nodeR)


def get_area_norm(area, vec_n):
    """根据平面结点三方向反力和法向量求解结点面积.

    Args:
        area (numpy.array(n, 4)): 结点反力数组，第一列为结点编号，后三列分别为三方向反力值.
        vec_n (numpy.array(1, 3)): 该平面的法向量.

    Returns:
        area_norm (numpy.array(n, 2)): 结点面积数组，第一列为结点编号，第二列为结点面积.
    """
    area = area[np.argsort(area[:, 0])]
    area_norm = np.zeros((area.shape[0], 2))
    for i in range(area.shape[0]):
        area_norm[i, 0] = area[i, 0]
        area_norm[i, 1] = np.abs(vec_n.dot(area[i, 1:]))
    return area_norm


def get_SF_WP(stre_data, area,  vec_n, vec_t):
    """根据某个平面上各点的应力，求作用在该平面上的法向反力和沿着平面上某个向量方向的反力.

    Args:
        stre_data (pandas.Dataframe): 应力数据表.
        area (numpy.array(n, 2)): 结点面积数组，第一列为结点编号，第二列为法向面积.
        vec_n (numpy.array(1, 3)): 该平面的单位法向量.
        vec_t (numpy.array(1, 3)): 该平面上的一个单位向量.

    Returns:
        W (float): 作用在该平面上的法向反力.
        P (float): 作用在该平面上沿某个向量方向的反力.
    """
    W, P = 0, 0
    for i in range(area.shape[0]):
        sigma = np.array([[stre_data.iloc[i]['S11'], stre_data.iloc[i]['S12'], stre_data.iloc[i]['S13']],
                        [stre_data.iloc[i]['S12'], stre_data.iloc[i]['S22'], stre_data.iloc[i]['S23']],
                        [stre_data.iloc[i]['S13'], stre_data.iloc[i]['S23'], stre_data.iloc[i]['S33']]])
        A = area[area[:, 0] == stre_data.iloc[i]['node']][0, 1]
        sigma_e = vec_n.dot(sigma)
        sigma_n = sigma_e.dot(vec_n)
        sigma_t = (sigma_e - sigma_n * vec_n).dot(vec_t)
        W -= sigma_n * A
        P += sigma_t * A
    return W, P


def get_stre_data(file_path):
    """将表格数据读取为pandas.Dataframe，并按结点编号排序.

    Args:
        file_path (string): 表格文件的路径.

    Returns:
        pandas.Dataframe: 按结点编号排序后的表格数据.
    """
    stre_data = pd.read_csv(file_path, encoding='gbk')
    stre_data.rename(columns={'      结点编号': 'node', '         S-S11': 'S11', '         S-S22': 'S22', '         S-S33': 'S33', '         S-S12': 'S12', '         S-S13': 'S13', '         S-S23': 'S23'}, inplace=True)
    stre_data.drop_duplicates(subset='node', keep='first', inplace=True)
    return stre_data.sort_values(by='node')


def kanghua(W, P, A, f, c, phi=1.0, gamma_0=1.1, gamma_d=1.5, gamma_f=1.7, gamma_c=2.0):
    """根据法向力和切向力以及抗滑参数计算抗滑稳定安全系数.

    Args:
        W (float or numpy.array(1, 2)): 两个滑面的法向作用力.
        P (float or numpy.array(1, 2)): 切向作用力.
        A (float or numpy.array(1, 2)): 面积.
        f (float or numpy.array(1, 2)): 摩擦系数.
        c (float or numpy.array(1, 2)): 凝聚力系数.
        phi (float): 设计状况系数，持久状况取1.0，偶然状况取0.85.
        gamma_0 (float): 结构重要性系数,分级I级取1.1.
        gamma_d (float): 抗滑稳定结构系数，静力工况取1.5，动力工况取0.65.
        gamma_f (float): 摩擦系数材料性能分项系数，取1.7.
        gamma_c (float): 粘聚力材料性能分项系数，取2.0.

    Returns:
        result (float): 抗滑稳定安全系数，大于1表示校核通过.
    """
    ff = f / gamma_f
    cc = c / gamma_c    
    R = 1e6 * cc * A + ff * (W > 0) * W
    # result = np.sum(R) / (np.abs(np.sum(P)) * gamma_0 * phi * gamma_d)
    result = np.sum(R) / (np.sum(np.abs(P)) * gamma_0 * phi * gamma_d)
    return result


def kanghua3D_2P_static(stre_data1, stre_data2, area_data1, area_data2, vec_n1, vec_n2, vec_t, f, c, phi=1.0, gamma_0=1.1, gamma_d=1.5, gamma_f=1.7, gamma_c=2.0):
    """求解静力工况三维滑块双滑面抗滑稳定安全系数.

    Args:
        stre_data1 (pandas.Dataframe): 滑面1结点应力数据表.
        stre_data2 (pandas.Dataframe): 滑面2结点应力数据表.
        area_data1 (numpy.array(n, 4)): 滑面1结点面积数组，第一列为结点编号，后三列分别为三方向面积值.
        area_data2 (numpy.array(n, 4)): 滑面2结点面积数组，第一列为结点编号，后三列分别为三方向面积值.
        vec_n1 (numpy.array(1, 3)): 滑面1单位法向量.
        vec_n2 (numpy.array(1, 3)): 滑面2单位法向量.
        vec_t (numpy.array(1, 3)): 滑块滑动方向单位向量.
        f (float or numpy.array(1, 2)): 摩擦系数，如果传入两个值，则分别代表滑面1、2的摩擦系数.
        c (float or numpy.array(1, 2)): 凝聚力系数，如果传入两个值，则分别代表滑面1、2的凝聚力系数.
        phi (float): 设计状况系数，持久状况取1.0，偶然状况取0.85.
        gamma_0 (float): 结构重要性系数,分级I级取1.1.
        gamma_d (float): 抗滑稳定结构系数，静力工况取1.5，动力工况取0.65.
        gamma_f (float): 摩擦系数材料性能分项系数，取1.7.
        gamma_c (float): 粘聚力材料性能分项系数，取2.0.

    Returns:
        K (float): 抗滑稳定安全系数，大于1表示校核通过.
    """
    area1 = get_area_norm(area_data1, vec_n1)
    area2 = get_area_norm(area_data2, vec_n2)
    W1, P1 = get_SF_WP(stre_data1, area1, vec_n1, vec_t)
    W2, P2 = get_SF_WP(stre_data2, area2, vec_n2, vec_t)
    W = np.array([W1, W2])
    P = np.array([P1, P2])
    A = np.array([np.sum(area1[:, 1]), np.sum(area2[:, 1])])
    f = np.array(f)
    c = np.array(c)
    K = kanghua(W, P, A, f , c, phi, gamma_0, gamma_d, gamma_f, gamma_c)
    return K


def kanghua3D_2P_dyn(stre_data1, stre_data2, area_data1, area_data2, vec_n1, vec_n2, vec_t, f, c, phi=0.85, gamma_0=1.1, gamma_d=0.65, gamma_f=1.7, gamma_c=2.0):
    """求解动力工况三维滑块双滑面抗滑稳定安全系数.

    Args:
        stre_data1 (pandas.Dataframe): 滑面1结点应力数据表.
        stre_data2 (pandas.Dataframe): 滑面2结点应力数据表.
        area_data1 (numpy.array(n, 4)): 滑面1结点面积数组，第一列为结点编号，后三列分别为三方向面积值.
        area_data2 (numpy.array(n, 4)): 滑面2结点面积数组，第一列为结点编号，后三列分别为三方向面积值.
        vec_n1 (numpy.array(1, 3)): 滑面1单位法向量.
        vec_n2 (numpy.array(1, 3)): 滑面2单位法向量.
        vec_t (numpy.array(1, 3)): 滑块滑动方向单位向量.
        f (float or numpy.array(1, 2)): 摩擦系数，如果传入两个值，则分别代表滑面1、2的摩擦系数.
        c (float or numpy.array(1, 2)): 凝聚力系数，如果传入两个值，则分别代表滑面1、2的凝聚力系数.
        phi (float): 设计状况系数，持久状况取1.0，偶然状况取0.85.
        gamma_0 (float): 结构重要性系数,分级I级取1.1.
        gamma_d (float): 抗滑稳定结构系数，静力工况取1.5，动力工况取0.65.
        gamma_f (float): 摩擦系数材料性能分项系数，取1.7.
        gamma_c (float): 粘聚力材料性能分项系数，取2.0.

    Returns:
        K (numpy.array(1, n)): 抗滑稳定安全系数，大于1表示校核通过.
        falit_time (int): 不通过的数据点个数.
    """
    f = np.array(f)
    c = np.array(c)
    area1 = get_area_norm(area_data1, vec_n1)
    area2 = get_area_norm(area_data2, vec_n2)
    A = np.array([np.sum(area1[:, 1]), np.sum(area2[:, 1])])

    i = 0
    while stre_data1.iloc[i]['X'] != 'X':
        i += 1
    numnode1 = i
    numstep1 = int((len(stre_data1) + 1) / (numnode1 + 1))

    i = 0
    while stre_data2.iloc[i]['X'] != 'X':
        i += 1
    numnode2 = i
    numstep2 = int((len(stre_data2) + 1) / (numnode2 + 1))

    if numstep1 != numstep2:
        print('不同面的计算步数不一样！')

    K_list = []
    fail_time = 0
    # pbar = tqdm.tqdm(range(numstep1), desc='Calculate', ncols=100)
    name_list = ['node', 'S11', 'S22', 'S33', 'S12', 'S13', 'S23']
    for step in range(numstep1):
        stre1 = stre_data1.iloc[step * (numnode1 + 1) : (step + 1) * (numnode1 + 1) - 1]
        stre1.drop_duplicates(subset='node', keep='first', inplace=True)
        stre2 = stre_data2.iloc[step * (numnode2 + 1) : (step + 1) * (numnode2 + 1) - 1]
        stre2.drop_duplicates(subset='node', keep='first', inplace=True)
        for name in name_list:
            stre1[name] = pd.to_numeric(stre1[name])
            stre2[name] = pd.to_numeric(stre2[name])
        W1, P1 = get_SF_WP(stre1, area1, vec_n1, vec_t)
        W2, P2 = get_SF_WP(stre2, area2, vec_n2, vec_t)
        W = np.array([W1, W2])
        P = np.array([P1, P2])
        K = kanghua(W, P, A, f, c, phi, gamma_0, gamma_d, gamma_f, gamma_c)
        K_list.append(K)
        if K < 1.0:
            fail_time += 1
    return np.array(K_list), fail_time