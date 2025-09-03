
# --------------------------- Louvain 社区发现完整实现 ---------------------------
# 每行都附带中文注释，帮助理解算法的关键步骤与变量含义
# -----------------------------------------------------------------------------

import collections            # 提供 defaultdict 与计数器等高效容器
import random                 # 用于打乱节点访问次序，避免算法陷入局部最优
import time                   # 计时，衡量算法运行效率

# --------------------------- 全局参数 ----------------------------------------
MAX_PHASE_I = 10              # Phase‑I（模块度局部优化）允许的最大迭代轮数
MAX_PASSS   = 10              # 整体算法最多进行多少个 pass（Phase‑I + Phase‑II）

# --------------------------- 读图函数 ----------------------------------------
def load_graph(path):                                   # path: 边列表文件
    G = collections.defaultdict(dict)                   # 邻接表：{u:{v:w}}
    with open(path) as text:                            # 逐行读取文本
        for line in text:                               # 每行形如 “u v [w]”
            vertices = line.strip().split()             # 去掉换行符并按空格切分
            v_i = int(vertices[0])                      # 顶点 u
            v_j = int(vertices[1])                      # 顶点 v
            w   = 1.0                                   # 若无权重，默认权值为 1
            if len(vertices) > 2:                       # 若第三列存在，则说明有权重
                w = float(vertices[2])                  # 读取权重
            G[v_i][v_j] = w                             # 无向图：u→v
            G[v_j][v_i] = w                             #           v→u
    print(">> total edges:", len(G))                    # 打印节点数（近似）
    return G                                            # 返回邻接表

# --------------------------- 节点对象 ----------------------------------------
class Vertex:
    def __init__(self, vid, cid, nodes, k_in=0):
        self._vid   = vid       # vid  : 顶点自身编号
        self._cid   = cid       # cid  : 顶点当前归属的社区编号
        self._nodes = nodes     # nodes: 若合并为超级节点则存原子节点集合
        self._kin   = k_in      # kin  : “内部”边权和（节点自身所在社区内部）

    def __str__(self):          # 便于打印调试
        return f"class Vertex:[vid:{self._vid}, cid:{self._cid}, nodes:{self._nodes}, kin:{self._kin}]"

    __repr__ = __str__          # 交互式环境直接显示对象信息

# --------------------------- Louvain 主类 ------------------------------------
class Louvain:
    def __init__(self, G):
        self._G            = G                       # 当前工作图（动态凝聚）
        self._m            = 0                       # 图中边权总和 (∑_e w_e)
        self._cid_vertices = {}                      # {cid : set(vid)} 社区→节点
        self._vid_vertex   = {}                      # {vid : Vertex对象}

        for vid in self._G.keys():                   # 初始化：每个点单独成社区
            self._cid_vertices[vid] = {vid}          # 社区 cid=vid，成员仅自己
            self._vid_vertex[vid]   = Vertex(vid, vid, {vid})  # 创建 Vertex
            self._m += sum([w for nbr, w in self._G[vid].items() if nbr > vid])
                                                      # 只统计一次无向边权

        print("====> m:", self._m)                   # 打印总边权

    # ----------------------- Phase‑I : 模块度局部优化 ------------------------
    def first_stage(self):
        mod_inc = False                              # 标记本 pass 内是否有模块度提升
        visit_sequence = list(self._G.keys())        # 所有顶点组成访问序列
        random.shuffle(visit_sequence)               # 打乱访问顺序

        iter_times_phaseI = 0                        # Phase‑I 的迭代计数
        while True:                                  # 循环直到无法再提升模块度
            log_max_deltaQ = 0                       # 记录本轮最大 ΔQ
            iter_times_phaseI += 1                   # +1 轮

            cluster_num = len([v for v in self._cid_vertices.values() if v])        # 当前 cluster 总数
            print(f"0=> phaseI iter:{iter_times_phaseI} (max:{MAX_PHASE_I}) | cluster_num:{cluster_num}")

            can_stop = True                          # 第一阶段是否可终止

            for v_vid in visit_sequence:             # 遍历所有顶点
                v_cid = self._vid_vertex[v_vid]._cid  # 顶点所在的社区
                k_v   = sum(self._G[v_vid].values()) + self._vid_vertex[v_vid]._kin
                                                      # 节点度（含内部边）

                cid_Q = {}                           # {候选社区: ΔQ}，存储模块度增益大于0的社区编号

                for w_vid in self._G[v_vid].keys():  # 遍历邻居
                    w_cid = self._vid_vertex[w_vid]._cid  # 邻居社区
                    if w_cid == v_cid:               # 同社区跳过
                        continue
                    if w_cid in cid_Q:               # 该社区已算过 ΔQ
                        continue

                    # ---------- 计算 ΔQ: 将 v_vid 移入 w_cid 带来的模块度增益 ----
                    tot = sum([sum(self._G[k].values()) + self._vid_vertex[k]._kin
                               for k in self._cid_vertices[w_cid]])  # 社区总度
                    k_v_in = sum([w for k, w in self._G[v_vid].items()
                                   if k in self._cid_vertices[w_cid]])  # v→社区内部边权
                    delta_Q1 = k_v_in - k_v * tot / self._m              # 简化的 ΔQ
                    # above is deltaQ(i->C)

                    # below is deltaQ(D->i)
                    k_v_in2 = sum([v for k, v in self._G[v_vid].items() if k in self._cid_vertices[v_cid]])
                    tot2 = sum(
                        [ sum(self._G[k].values()) + self._vid_vertex[k]._kin  for k in self._cid_vertices[v_cid]] )
                    delta_Q2 = (-k_v_in2 + k_v * (tot2 - k_v)) / (2 * self._m)

                    # add the 2 deltas.
                    delta_Q = delta_Q1  + delta_Q2

                    cid_Q[w_cid] = delta_Q              # 记录 ΔQ 值

                # 若无可移动的社区，则设定哨兵值
                if not cid_Q:
                    cid, max_delta_Q = 0, -1
                else:
                    cid, max_delta_Q = max(cid_Q.items(), key=lambda x: x[1])

                log_max_deltaQ = max(log_max_deltaQ, max_delta_Q)  # 更新最大 ΔQ

                # ----------- 若 ΔQ>0 且目标社区不同，则执行迁移 -----------------
                if max_delta_Q > 0.0 and cid != v_cid:
                    self._vid_vertex[v_vid]._cid = cid              # 更新节点社区
                    self._cid_vertices[cid].add(v_vid)              # 加入新社区
                    self._cid_vertices[v_cid].remove(v_vid)         # 移出旧社区
                    can_stop = False                                # 标记需继续循环
                    mod_inc  = True                                 # 整体模块度提升
                
            if iter_times_phaseI >= MAX_PHASE_I:    # 超过最大轮次则强制停止
                can_stop = True
            if can_stop:                            # 若整轮没有节点移动则退出
                break

            print(f"\tmax_delta_Q:{log_max_deltaQ}")  # 打印本轮最大 ΔQ

        return mod_inc                              # 返回是否有模块度提升

    # ----------------------- Phase‑II : 网络凝聚 ------------------------------
    def second_stage(self):
        print("== Phase II begin ==")
        cid_vertices = {}                           # 新社区→节点
        vid_vertex   = {}                           # 新节点编号→Vertex

        # —— 把每个社区收缩为一个“超级节点” ——
        for cid, vertices in self._cid_vertices.items():
            if not vertices:                        # 空社区跳过
                continue
            new_vertex = Vertex(cid, cid, set())    # 新节点 id=cid
            for vid in vertices:                   # 合并社区中所有原子节点
                new_vertex._nodes.update(self._vid_vertex[vid]._nodes)
                new_vertex._kin += self._vid_vertex[vid]._kin
                for k, w in self._G[vid].items():  # 计算内部权重
                    if k in vertices:
                        new_vertex._kin += w / 2.0 # 每条内部边仅算一次
            cid_vertices[cid] = {cid}              # 新社区的成员仅自己
            vid_vertex[cid]   = new_vertex         # 存储新节点对象

        # —— 重新构建社区间的边 ——  
        G = collections.defaultdict(dict)          # 新图
        for cid1, vertices1 in self._cid_vertices.items():
            if not vertices1:
                continue
            for cid2, vertices2 in self._cid_vertices.items():
                if cid2 <= cid1 or not vertices2:  # 只处理上三角避免重复
                    continue
                edge_weight = 0.0
                for vid in vertices1:              # 累加两个社区之间的边权
                    for k, w in self._G[vid].items():
                        if k in vertices2:
                            edge_weight += w
                if edge_weight:                    # 若权重非零则添加到新图
                    G[cid1][cid2] = edge_weight
                    G[cid2][cid1] = edge_weight

        # —— 用新图替换旧图，准备下一 pass ——
        self._cid_vertices = cid_vertices
        self._vid_vertex   = vid_vertex
        self._G            = G
        print("=====> cluster:", len(self._G))     # 打印当前社区数

    # ----------------------- 获取最终社区列表 ---------------------------------
    def get_communities(self):
        communities = []                           # 最终结果: [ [v1,v2,...], ... ]
        for vertices in self._cid_vertices.values():
            if vertices:
                c = set()
                for vid in vertices:
                    c.update(self._vid_vertex[vid]._nodes) # 展开超级节点
                communities.append(list(c))
        return communities

    # ----------------------- 算法入口 ----------------------------------------
    def execute(self):
        iter_time = 0                              # pass 计数
        while True:
            iter_time += 1
            if iter_time > MAX_PASSS:              # 防止死循环
                break
            print(f"\n>>> Pass iter_time:{iter_time} (max:{MAX_PASSS})")
            mod_inc = self.first_stage()           # Phase‑I

            if mod_inc:                            # 若模块度得到提升
                self.second_stage()                #   继续 Phase‑II
            else:                                  # 否则停止迭代
                print("-------Stop Phase II-----")
                break
        return self.get_communities()              # 返回社区划分结果

# --------------------------- 主程序 ------------------------------------------
if __name__ == '__main__':
    # -------- 1. 读取数据集 ---------------------------------------------------
    input_file = 'data/snn_df.txt'                # 边列表文件路径
    G = load_graph(input_file)                    # 载入无向加权图

    # -------- 2. 运行 Louvain 算法 ------------------------------------------
    start_time  = time.time()                     # 计时开始
    algorithm   = Louvain(G)                      # 创建算法实例
    communities = algorithm.execute()             # 执行并获得社区
    end_time    = time.time()                     # 计时结束

    # -------- 3. 输出结果 ----------------------------------------------------
    communities = sorted(communities, key=lambda x: -len(x))  # 按社区规模排序
    for idx, commun in enumerate(communities[:10], 1):        # 仅显示前 10 个
        print(f"Community {idx} :", commun)
    print("====>>>> Total clusters:", len(communities))

    # -------- 4. 保存至文件 ---------------------------------------------------
    output_file = "backup/result-impl.txt"             # 输出文件
    with open(output_file, "w") as fw:
        for cid, comm in enumerate(communities):
            for v in comm:
                fw.write(f"{v}\t{cid}\n")         # “顶点 id  社区 id”
    print("output_file:", output_file)

    # -------- 5. 打印耗时 ----------------------------------------------------
    print(f'Exec time: {round(end_time - start_time, 2)} seconds')
