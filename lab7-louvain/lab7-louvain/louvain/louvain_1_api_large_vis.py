import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

# 读取社区检测结果
node_community = {}
# 从文件 result-api-large.txt 中读取社区划分结果，格式为 节点ID\t社区编号
with open('backup/result-api-large.txt', 'r') as f:
    for line in f:
        node, comm = map(int, line.strip().split())
        node_community[node] = comm

# 创建图并添加边（假设原始图数据可用）
# 若需完整可视化，需加载原始图的边数据文件
# 这里用随机边数据演示（需替换为真实数据）
G = nx.Graph()
G.add_nodes_from(node_community.keys()) # 添加所有节点

# 添加随机边（示例用，需替换为真实边数据）
#import random
#for node in G.nodes():
#    G.add_edge(node, random.choice(list(G.nodes()))  # 随机连接
def load_edges(path):
    with open(path) as f:
        for line in f:
            u, v, w = line.strip().split() #从文件 snn_df.txt 加载边数据（格式为 起点 终点 权重）
            G.add_edge(int(u), int(v), weight=float(w))
load_edges('data/snn_df.txt')  # 替换为你的边数据文件

# 生成布局（力导向布局模拟UMAP效果）
pos = nx.spring_layout(G, seed=42, iterations=50)
# iterations=50：控制布局迭代次数，值越大布局越稳定。
# 字典 pos，键为节点ID，值为坐标 (x, y)。

# 按社区分配颜色
community_colors = defaultdict(list)
for node, comm in node_community.items():
    community_colors[comm].append(node)

# community_colors 结构示例：{0: [0, 1, 3], 1: [2, 4, 5]}

# 绘制图形
plt.figure(figsize=(12, 8))
for comm, nodes in community_colors.items():
    nx.draw_networkx_nodes(
        G, pos,
        nodelist=nodes,
        node_size=20,
        node_color=plt.cm.tab20(comm % 20), # 使用 tab20 颜色映射，支持最多20种不同颜色（超过则循环使用）
        label=f'Community {comm}'
    )
nx.draw_networkx_edges(G, pos, alpha=0.1, width=0.5)
plt.title('Louvain Community Detection Visualization')
plt.legend(scatterpoints=1, frameon=False, fontsize=8) #显示图例
plt.axis('off') # 隐藏坐标轴
plt.savefig('louvain_1_api_large_vis.png', dpi=300, bbox_inches='tight') # 保存高清图片
plt.close()

print("可视化结果已保存为 louvain_1_api_large_vis.png")