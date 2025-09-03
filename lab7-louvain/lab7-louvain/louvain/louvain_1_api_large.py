# --------------------------- Louvain算法完整示例 ----------------------------
# 导入所需的第三方库
import time
import pandas as pd                    # 用于数据整理与统计分析
import matplotlib.pyplot as plt        # 用于绘图与可视化
import networkx as nx                  # NetworkX：创建与操作复杂网络
from community import community_louvain  # community_louvain：实现 Louvain 社区发现

# 这个包的输入要求顶点列表、边列表。
def load_graph(path):
    nodes=set()
    edges=[]
    with open(path) as text:
        for line in text:
            vertices = line.strip().split() #去掉换行符，按空格切分
            v_i = int(vertices[0]) # 起点节点
            v_j = int(vertices[1]) # 终点节点
            w = 1.0
            # 数据集有权重的话则读取数据集中的权重
            if len(vertices) > 2:
                w = float(vertices[2])
            nodes.add(v_i)
            nodes.add(v_j)
            # weighted edge
            edges.append([v_i,v_j, w]) # 添加带权边
    return nodes, edges

nodes, edges=load_graph("data/snn_df.txt")

# prepare the input of Louvain py
G=nx.Graph() #创建 networkx 的无向图 G
G.add_nodes_from(list(nodes)) # 添加所有节点
G.add_weighted_edges_from(edges) # 添加带权边

# begin community detection
start_time = time.time()
partition = community_louvain.best_partition(G, resolution=0.7) #图对象 G，参数 resolution 控制社区划分粒度（值越大社区越小）
end_time = time.time()

# save to file: 顶点id 社区id
output_file="backup/result-api-large.txt";
fw=open(output_file, "w") #将社区划分结果写入文件，每行格式为 节点ID\t社区编号
for k,v in partition.items():
	fw.write(f"{k}\t{v}"+"\n")
fw.close()

print( set( partition.values() ) ) # 输出所有社区编号（去重）

print("saved to file:", output_file)
print(f'Exec time: { round(end_time - start_time, 2)} seconds')
