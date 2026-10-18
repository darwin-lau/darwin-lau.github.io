"""Regenerate the four sourced article figures; SVG text is stored as paths."""

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Circle, Rectangle


ROOT = Path(__file__).resolve().parents[2]
DATA = Path(__file__).parent / "data"
OUTPUT = ROOT / "src/assets/images"
PREVIEW = Path("/tmp/darwin-agent-figures")
# shortcut: this local renderer uses macOS CJK fonts; select an installed CJK font on other systems.
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"
font_manager.fontManager.addfont(FONT)
plt.rcParams.update({
    "font.family": font_manager.FontProperties(fname=FONT).get_name(),
    "font.weight": 300,
    "svg.fonttype": "path",
    "svg.hashsalt": "darwin-agent-cases-2026-10-18",
    "axes.unicode_minus": False,
})
BG, INK, MUTED, GREEN = "#fafbf9", "#292e2a", "#59635c", "#285c48"
LINE, LIGHT = "#bdc5be", "#edf3ee"


def canvas(height):
    fig = plt.figure(figsize=(740 / 96, height / 96), facecolor=BG)
    ax = fig.add_axes((0, 0, 1, 1), xlim=(0, 1), ylim=(0, 1))
    ax.set_axis_off()
    return fig, ax


def text(ax, x, y, content, size=14, color=INK, **kwargs):
    return ax.text(x, y, content, fontsize=size, color=color, va="center", zorder=4,
                   **kwargs)


def node(ax, y, content, *, x=.46, width=.70, height=.068, agent=False):
    ax.add_patch(Rectangle((x - width / 2, y - height / 2), width, height,
                           facecolor=LIGHT if agent else BG,
                           edgecolor=GREEN if agent else LINE, linewidth=1.2,
                           zorder=3))
    text(ax, x, y, content, size=14, color=GREEN if agent else INK,
         ha="center", linespacing=1.6)


def arrow(ax, start, end, *, color=MUTED, dashed=False):
    ax.annotate("", xy=end, xytext=start,
                arrowprops={"arrowstyle": "->", "color": color,
                            "lw": 1.25, "linestyle": "--" if dashed else "-",
                            "shrinkA": 0, "shrinkB": 0})


def save(fig, name, title, description):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    svg = OUTPUT / f"{name}.svg"
    fig.savefig(svg, metadata={
        "Title": title, "Description": description,
        "Creator": "Darwin blog research figures",
        "Date": "2026-10-18",
    })
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    fig.savefig(PREVIEW / f"{name}.png", dpi=96)
    plt.close(fig)


def harness_benchmark():
    with (DATA / "harness-benchmark.csv").open() as source:
        rows = list(csv.DictReader(source))
    scores = [float(row["score_percent"]) for row in rows]
    assert scores == [52.8, 66.5] and all(0 <= score <= 100 for score in scores)
    assert {row["model"] for row in rows} == {"gpt-5.2-codex"}
    assert round(scores[1] - scores[0], 1) == 13.7
    fig, ax = canvas(620)
    text(ax, .07, .94, "同一模型，Harness 调整前后", size=20)
    text(ax, .07, .875, "GPT-5.2-Codex · Terminal-Bench 2.0", color=MUTED)
    text(ax, .07, .775, "+13.7 个百分点", size=22, color=GREEN)
    for row, score, y, color in zip(rows, scores, [.60, .425], [MUTED, GREEN]):
        text(ax, .07, y + .075, row["variant"])
        ax.add_patch(Rectangle((.07, y - .024), .80 * score / 100, .048,
                               color=color, linewidth=0))
        text(ax, .085 + .80 * score / 100, y, f"{score:.1f}%", size=16,
             color=color)
    ax.plot([.07, .87], [.335, .335], color=LINE, lw=1)
    for value in [0, 25, 50, 75, 100]:
        x = .07 + .80 * value / 100
        ax.plot([x, x], [.335, .326], color=LINE, lw=1)
        text(ax, x, .296, str(value), size=11.5, color=MUTED, ha="center")
    text(ax, .07, .235, "任务完成得分（%）", size=12, color=MUTED)
    text(ax, .07, .165, "整体 Harness 调整，含推理配置；非单因素同预算实验。",
         size=12, color=INK)
    text(ax, .07, .112, "未提供重复次数与置信区间。", size=12, color=MUTED)
    text(ax, .07, .047, "来源：LangChain · 2026-02-17 · 厂商自测", size=12,
         color=MUTED)
    save(fig, "harness-benchmark", "同一模型，Harness 调整前后",
         "LangChain self-reported Terminal-Bench 2.0 scores: 52.8% and 66.5%. "
         "Whole-harness changes include reasoning configuration; not a single-factor, "
         "equal-budget experiment. " + rows[0]["source_url"])


def stripe_minions_flow():
    fig, ax = canvas(1040)
    text(ax, .07, .961, "Stripe Minions：自主实现，固定交付", size=19)
    text(ax, .07, .917, "淡绿：Agent 自主节点    灰框：固定代码 / 流程", size=12,
         color=MUTED)
    node(ax, .851, "工单 / Slack 讨论线程", height=.056)
    node(ax, .752, "预热且隔离的 devbox\n装配相关规则与上下文", height=.082)
    node(ax, .642, "Agent 实现任务\n核心基于 Goose fork", height=.082, agent=True)
    node(ax, .532, "固定代码\n本地 lint → push → 第一轮 CI", height=.082)
    node(ax, .433, "失败：先自动修复可修的问题", height=.056)
    node(ax, .339, "必要时，Agent 再修一次", height=.062, agent=True)
    node(ax, .247, "第二次 push / CI", height=.056)
    node(ax, .140, "交还人类评审\n不自动合并，不发布生产", height=.080)
    for start, end in [(.823, .793), (.711, .683), (.601, .573),
                       (.491, .461), (.405, .370), (.308, .275),
                       (.219, .180)]:
        arrow(ax, (.46, start), (.46, end))
    # A first-CI success bypasses all failure repair and second-CI nodes.
    ax.plot([.81, .93, .93], [.532, .532, .14], color=GREEN, lw=1.3)
    arrow(ax, (.93, .14), (.81, .14), color=GREEN)
    text(ax, .893, .375, "首轮 CI 通过", size=12.5, color=GREEN,
         ha="center", rotation=90)
    # Automatic fixes can go straight to the second push without an agent edit.
    ax.plot([.11, .065, .065], [.433, .433, .247], color=MUTED, lw=1.15)
    arrow(ax, (.065, .247), (.11, .247))
    text(ax, .034, .339, "无需 Agent 修改", size=10.5, color=MUTED,
         rotation=90, ha="center")
    text(ax, .49, .200, "通过或失败", size=11.5, color=MUTED)
    text(ax, .07, .066, "最多两轮 CI 是预算限制，并不保证成功。", size=12, color=INK)
    text(ax, .07, .030, "依据 Stripe 官方描述重绘 · 2026-02-09 / 02-19", size=11.5,
         color=MUTED)
    save(fig, "stripe-minions-flow", "Stripe Minions 交付流程示意",
         "Redrawn from Stripe's engineering posts, February 9 and 19, 2026. "
         "A maximum of two CI runs is a budget, not a success guarantee. "
         "Human review is required; no automatic merge or production deployment. "
         "https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2")


def vercel_d0_benchmark():
    with (DATA / "vercel-d0-benchmark.csv").open() as source:
        rows = list(csv.DictReader(source))
    durations = [float(row["mean_duration_seconds"]) for row in rows]
    successes = [int(row["successful_queries"]) for row in rows]
    assert durations == [274.8, 77.4] and all(value >= 0 for value in durations)
    assert successes == [4, 5] and all(int(row["total_queries"]) == 5 for row in rows)
    fig, ax = canvas(780)
    text(ax, .07, .948, "Vercel d0：调整工具设计前后", size=20)
    text(ax, .07, .886, "Vercel 内部小样本 · n = 5 个代表性查询", size=14,
         color=GREEN)
    text(ax, .07, .797, "平均查询耗时（秒）", size=16)
    for row, duration, y, color in zip(rows, durations, [.704, .609], [MUTED, GREEN]):
        text(ax, .07, y, row["variant"])
        ax.add_patch(Rectangle((.24, y - .017), .56 * duration / 300, .034,
                               color=color, linewidth=0))
        text(ax, .255 + .56 * duration / 300, y, f"{duration:.1f}", size=15,
             color=color)
    ax.plot([.24, .80], [.550, .550], color=LINE, lw=1)
    for value in [0, 100, 200, 300]:
        x = .24 + .56 * value / 300
        ax.plot([x, x], [.550, .542], color=LINE, lw=1)
        text(ax, x, .517, str(value), size=11.5, color=MUTED, ha="center")
    ax.plot([.07, .93], [.471, .471], color=LINE, lw=.8)
    text(ax, .07, .420, "成功查询数（共 5 个查询）", size=16)
    for row, count, y in zip(rows, successes, [.335, .245]):
        text(ax, .07, y, row["variant"])
        for index in range(5):
            ax.add_patch(Circle((.34 + .09 * index, y), .0135,
                                facecolor=GREEN if index < count else BG,
                                edgecolor=GREEN, lw=1.25))
        text(ax, .845, y, f"{count}/5", size=16, color=GREEN)
    text(ax, .07, .174, "实心表示成功，空心表示未成功；不表示具体查询顺序。", size=11.5,
         color=MUTED)
    text(ax, .07, .103, "来源：Vercel / Andrew Qu · 2025-12-22 · 厂商自测", size=11.5,
         color=MUTED)
    text(ax, .07, .049, "小样本工程记录，非独立复现；不能外推长期可靠性。", size=11.5,
         color=INK)
    save(fig, "vercel-d0-benchmark", "Vercel d0 工具设计调整前后",
         "Vercel self-reported small internal sample of five representative queries: "
         "mean duration 274.8 vs 77.4 seconds; successful queries 4/5 vs 5/5. "
         "Dots are aggregate counts, not a query-level sequence. " + rows[0]["source_url"])


def refund_timeout_sequence():
    fig, ax = canvas(980)
    text(ax, .07, .958, "超时以后，如何避免再退一次款？", size=20)
    text(ax, .07, .907, "假想示意，非真实事故", size=14, color=GREEN)
    for x in [.18, .82]:
        ax.plot([x, x], [.812, .143], color=LINE, lw=1.2, linestyle=(0, (4, 4)))
    node(ax, .842, "业务服务", x=.18, width=.24, height=.055)
    node(ax, .842, "退款服务", x=.82, width=.24, height=.055)
    arrow(ax, (.18, .746), (.82, .746))
    text(ax, .5, .777, "发起退款 100 元 · 业务键 R42", size=14, ha="center")
    node(ax, .654, "退款已完成\n持久保存 R42 与结果", x=.71, width=.46, height=.085)
    arrow(ax, (.82, .544), (.365, .544), dashed=True)
    ax.plot(.35, .544, marker="x", markersize=10, color=MUTED, mew=1.5)
    text(ax, .5, .580, "成功响应丢失 / 调用超时", size=14, ha="center")
    node(ax, .449, "业务服务恢复后继续处理", x=.285, width=.45, height=.060)
    arrow(ax, (.18, .357), (.82, .357), color=GREEN)
    text(ax, .5, .392, "以同一业务键 R42 重试", size=14, ha="center", color=GREEN)
    node(ax, .270, "命中已有结果\n未重复退款", x=.71, width=.46, height=.085,
         agent=False)
    arrow(ax, (.82, .161), (.18, .161), color=GREEN)
    text(ax, .5, .197, "返回首次退款结果", size=14, ha="center", color=GREEN)
    text(ax, .07, .083, "前提：退款服务持久保存并强制执行幂等规则。", size=12,
         color=INK)
    text(ax, .07, .042, "只在客户端重复传 R42，并不能防止重复退款。", size=12,
         color=MUTED)
    save(fig, "refund-timeout-sequence", "退款超时与幂等重试：假想示意",
         "Hypothetical illustration, not a real incident. A refund service durably "
         "stores and enforces idempotency for business key R42. A completed 100-yuan "
         "refund is not repeated after a lost response and a retry with the same key. "
         "Repeating a client string alone does not provide idempotency.")


if __name__ == "__main__":
    harness_benchmark()
    stripe_minions_flow()
    vercel_d0_benchmark()
    refund_timeout_sequence()
    print(f"SVG: {OUTPUT}\nPNG: {PREVIEW}")
