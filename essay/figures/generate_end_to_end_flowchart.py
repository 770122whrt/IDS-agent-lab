"""
系统端到端业务流程图生成器

生成一张从用户输入到最终审查报告的完整业务链路图，
保存为 SVG（矢量）和 PNG（位图）两种格式。

用法:
    python essay/figures/generate_end_to_end_flowchart.py

输出:
    essay/figures/figure_end_to_end_flow.svg
    essay/figures/figure_end_to_end_flow.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# 设置中文字体（Windows常见字体）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 画布尺寸 (cm -> inches)
FIG_W = 16 / 2.54
FIG_H = 20 / 2.54
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
ax.set_xlim(0, 16)
ax.set_ylim(0, 20)
ax.axis('off')

# 颜色定义（学术风格）
C_INPUT = '#F5F5F5'      # 浅灰 - 用户输入
C_PIPE = '#E3F2FD'       # 浅蓝 - IDS生成管道
C_CORE = '#BBDEFB'       # 中蓝 - 核心步骤
C_MID = '#FFF3E0'        # 浅橙 - 中间产物
C_REVIEW = '#E8F5E9'     # 浅绿 - 审查流程
C_OUTPUT = '#FFEBEE'     # 浅红 - 最终输出
C_TEXT = '#212121'       # 深灰黑 - 文字
C_ARROW = '#424242'      # 箭头颜色


def draw_round_box(ax, cx, cy, w, h, text, facecolor, fontsize=9,
                   text_color=C_TEXT, bold=False, edgecolor='black',
                   linewidth=1, alpha=1.0):
    """绘制圆角矩形框并居中文字"""
    box = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.2,rounding_size=0.25",
        facecolor=facecolor, edgecolor=edgecolor,
        linewidth=linewidth, alpha=alpha, zorder=2
    )
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(cx, cy, text, ha='center', va='center',
            fontsize=fontsize, color=text_color, weight=weight, zorder=3)
    return box


def draw_arrow(ax, x1, y1, x2, y2, style='->', color=C_ARROW, lw=1.8, label=''):
    """绘制带箭头的连接线"""
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle=style, mutation_scale=15,
        color=color, linewidth=lw, zorder=1
    )
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.3, my, label, fontsize=8, color='#616161',
                ha='left', va='center', style='italic', zorder=4)


def draw_container(ax, cx, cy, w, h, title, inner_boxes, facecolor, title_fs=10):
    """绘制带标题的大容器，内部横向排列小框"""
    # 容器背景（浅色半透明）
    container = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.2,rounding_size=0.3",
        facecolor=facecolor, edgecolor='black',
        linewidth=1.2, alpha=0.35, zorder=0
    )
    ax.add_patch(container)
    # 容器标题（左上角）
    ax.text(cx - w/2 + 0.4, cy + h/2 - 0.35, title,
            fontsize=title_fs, color=C_TEXT, weight='bold',
            ha='left', va='center', zorder=4)
    # 内部小框
    n = len(inner_boxes)
    gap = 0.35
    box_w = (w - 2 * gap - (n - 1) * gap) / n
    box_h = h - 1.1
    start_x = cx - w/2 + gap + box_w/2
    for i, (text, color) in enumerate(inner_boxes):
        bx = start_x + i * (box_w + gap)
        by = cy - 0.15
        is_core = (color == C_CORE)
        draw_round_box(ax, bx, by, box_w, box_h, text, color,
                       fontsize=8, bold=is_core,
                       edgecolor='#1565C0' if is_core else 'black',
                       linewidth=1.5 if is_core else 0.8)
        # 框之间的小箭头
        if i < n - 1:
            ax.annotate('', xy=(bx + box_w/2 + gap/2, by), xytext=(bx + box_w/2, by),
                        arrowprops=dict(arrowstyle='->', color=C_ARROW, lw=1.2),
                        zorder=5)


# ========== 绘图开始 ==========

# 1. 主标题
ax.text(8, 19.3, '系统端到端业务流程图', fontsize=16, weight='bold',
        ha='center', va='center', color=C_TEXT)
ax.plot([3, 13], [18.7, 18.7], color='#BDBDBD', linewidth=1, zorder=1)

# 2. 用户输入
draw_round_box(ax, 8, 17.5, 10, 1.2, '用户输入自然语言规范描述', C_INPUT,
               fontsize=11, bold=True, edgecolor='#616161', linewidth=1.5)
draw_arrow(ax, 8, 17.0, 8, 16.3)

# 3. 五阶段IDS生成管道
pipe_boxes = [
    ('① 结构化\n解析', C_PIPE),
    ('② 方面\n分类', C_PIPE),
    ('③ 知识库\n映射[核心]', C_CORE),
    ('④ 约束\n提取', C_PIPE),
    ('⑤ IDS\n构建', C_PIPE),
]
draw_container(ax, 8, 14.3, 14, 3.2, 'IDS生成五阶段管道', pipe_boxes, C_PIPE, title_fs=11)
draw_arrow(ax, 8, 12.7, 8, 11.8)

# 4. IDS规则文件（中间产物）
draw_round_box(ax, 8, 11.2, 8, 1.0, 'IDS规则文件（XML格式）', C_MID,
               fontsize=10, bold=True, edgecolor='#E65100', linewidth=1.5)
# 标注：符合buildingSMART IDS标准
ax.text(8, 10.7, '符合 buildingSMART IDS 1.0 标准', fontsize=8,
        ha='center', va='top', color='#757575', style='italic')
draw_arrow(ax, 8, 10.3, 8, 9.6)

# 5. IFC模型 + IDS规则输入（审查阶段输入）
# 左侧：IFC模型
# 右侧：IDS规则（复用上一步产物）
draw_round_box(ax, 5.5, 8.9, 5.5, 1.0, 'IFC模型文件\n(用户上传)', '#F1F8E9',
               fontsize=9, bold=False, edgecolor='black', linewidth=1)
draw_round_box(ax, 10.5, 8.9, 5.5, 1.0, 'IDS规则文件\n(系统生成)', C_MID,
               fontsize=9, bold=False, edgecolor='black', linewidth=1)
# 汇聚箭头
draw_arrow(ax, 8, 8.4, 8, 7.7)

# 6. ifctester审查流程
review_boxes = [
    ('加载IDS\n规则', C_REVIEW),
    ('遍历IFC\n实体', C_REVIEW),
    ('执行合规\n检验', '#C8E6C9'),
]
draw_container(ax, 8, 6.0, 12, 2.6, 'ifctester 自动化合规审查', review_boxes, C_REVIEW, title_fs=11)
draw_arrow(ax, 8, 4.7, 8, 4.0)

# 7. 审查报告输出
draw_round_box(ax, 8, 3.3, 10, 1.1, '合规审查报告', C_OUTPUT,
               fontsize=11, bold=True, edgecolor='#C62828', linewidth=1.5)
# 三种格式子标注
fmt_x = [5.5, 8.0, 10.5]
fmt_text = ['JSON', 'HTML', 'BCF']
fmt_color = ['#EF9A9A', '#EF9A9A', '#EF9A9A']
for fx, ft, fc in zip(fmt_x, fmt_text, fmt_color):
    draw_round_box(ax, fx, 2.3, 2.2, 0.6, ft, fc, fontsize=8,
                   edgecolor='#B71C1C', linewidth=0.8)
    # 小箭头从主输出框连接到格式框
    ax.annotate('', xy=(fx, 2.6), xytext=(fx, 2.75),
                arrowprops=dict(arrowstyle='->', color='#B71C1C', lw=0.8), zorder=5)

# 8. 右侧标注：完整闭环
ax.text(15.5, 10.5, '"规则生成 →\n审查执行 →\n结果反馈"\n完整闭环',
        fontsize=9, ha='center', va='center', color='#1565C0',
        weight='bold', style='italic',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#E3F2FD', edgecolor='#1565C0', alpha=0.8))

# 9. 底部标注
ax.text(8, 0.5, '图1.X  系统端到端业务流程图（用户输入→IDS生成→合规审查→报告输出）',
        fontsize=10, ha='center', va='center', color=C_TEXT, weight='bold')

# 保存
out_svg = 'essay/figures/figure_end_to_end_flow.svg'
out_png = 'essay/figures/figure_end_to_end_flow.png'
plt.savefig(out_svg, format='svg', bbox_inches='tight', dpi=300, facecolor='white')
plt.savefig(out_png, format='png', bbox_inches='tight', dpi=300, facecolor='white')
print(f'[OK] 流程图已保存:')
print(f'      SVG: {out_svg}')
print(f'      PNG: {out_png}')
