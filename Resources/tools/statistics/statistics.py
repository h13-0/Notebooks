import os
import re
import json
import argparse
import logging
import shutil
import fnmatch
from collections import defaultdict, deque
from datetime import date, datetime, timedelta, timezone
import git
from git.exc import GitCommandError
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

plt.rcParams['font.family'] = ['Source Han Mono']
plt.rcParams['axes.unicode_minus'] = False


# 配置日志将在main函数中根据命令行参数完成
logger = logging.getLogger(__name__)


AI_REVIEW_BLOCK_RE = re.compile(
    r"(?ms)^<!-- ai-review:start unit=ru[0-9]{6} -->.*?^<!-- ai-review:end -->\s*"
)
AI_REVIEW_ANCHOR_RE = re.compile(r"(?m)(?:\s*\^ru[0-9]{6}\b)")

DEFAULT_FILTER_CONFIG = {
    "exclude_paths": [
        "AI-Review",
        "tools/ai-review",
        "skills/ai-review",
        ".codex/skills/ai-review",
        ".cursor/rules/ai-review.mdc",
        "AGENTS.ai-review.md",
        "AI-Review-SLASH_COMMANDS.md",
        "README.ai-review-skill.md",
    ],
    "exclude_globs": [
        ".codex/commands/ai-review*.md",
        "*.ai-review.md",
    ],
    "strip_ai_review_blocks": True,
    "strip_ai_review_anchors": True,
}


def normalize_rel_path(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def load_filter_config(config_path: str | None) -> dict:
    config = json.loads(json.dumps(DEFAULT_FILTER_CONFIG))
    if not config_path:
        return config
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            user_config = json.load(file)
    except FileNotFoundError:
        logger.warning(f"Statistics filter config not found: {config_path}; using defaults")
        return config
    except Exception as exc:
        raise RuntimeError(f"Error loading statistics filter config {config_path}: {exc}") from exc

    for key in ("exclude_paths", "exclude_globs"):
        if key in user_config:
            config[key] = user_config[key] or []
    for key in ("strip_ai_review_blocks", "strip_ai_review_anchors"):
        if key in user_config:
            config[key] = bool(user_config[key])
    return config


def filter_config_hash(config: dict) -> str:
    payload = json.dumps(config, ensure_ascii=False, sort_keys=True)
    import hashlib
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def is_excluded_path(rel_path: str, config: dict) -> bool:
    rel = normalize_rel_path(rel_path)
    parts = rel.split("/")
    for raw in config.get("exclude_paths", []):
        item = normalize_rel_path(str(raw))
        if not item:
            continue
        if rel == item or rel.startswith(item + "/"):
            return True
        if "/" not in item and item in parts:
            return True
    for raw in config.get("exclude_globs", []):
        pattern = normalize_rel_path(str(raw))
        if pattern and fnmatch.fnmatch(rel, pattern):
            return True
    return False


def sanitize_markdown_for_statistics(content: str, config: dict) -> str:
    if config.get("strip_ai_review_blocks", True):
        content = AI_REVIEW_BLOCK_RE.sub("", content)
    if config.get("strip_ai_review_anchors", True):
        content = AI_REVIEW_ANCHOR_RE.sub("", content)
    return content


class DocStatistics:
    def __init__(self, path: str, filter_config: dict):
        self.path = path
        self.filter_config = filter_config
        self.line_count = 0
        self.char_count = 0
        self.update_statistics()

    def update_statistics(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                content = sanitize_markdown_for_statistics(file.read(), self.filter_config)
                self.line_count = content.count('\n') + 1
                self.char_count = self._count_words(content)
        except Exception as e:
            logger.error(f"Error reading file {self.path}: {e}")
            self.line_count = 0
            self.char_count = 0

    def _count_words(self, text):
        chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf]')
        english_pattern = re.compile(r'[a-zA-Z]+')
        chinese_count = len(chinese_pattern.findall(text))
        english_count = len(english_pattern.findall(text))
        return chinese_count + english_count


class RepoStatistics:
    def __init__(self, repo_path: str, filter_config: dict | None = None):
        self.repo_path = repo_path
        self.filter_config = filter_config or DEFAULT_FILTER_CONFIG
        self._doc_types = [".md"]
        self._doc_statistics = []
        self._top_level_word_counts = defaultdict(int)
        self.update_statistics()

    def update_statistics(self):
        self._doc_statistics = []
        self._top_level_word_counts = defaultdict(int)
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if any(file.endswith(ext) for ext in self._doc_types):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.repo_path)
                    if is_excluded_path(rel_path, self.filter_config):
                        continue
                    doc_statistics = DocStatistics(file_path, self.filter_config)
                    self._doc_statistics.append(doc_statistics)
                    top_level = self._get_top_level_folder(file_path)
                    self._top_level_word_counts[top_level] += doc_statistics.char_count

    @property
    def word_count(self) -> int:
        return sum(stat.char_count for stat in self._doc_statistics)

    @property
    def line_count(self) -> int:
        return sum(stat.line_count for stat in self._doc_statistics)

    @property
    def top_level_word_counts(self):
        return dict(self._top_level_word_counts)

    def _get_top_level_folder(self, file_path: str) -> str:
        rel_path = os.path.relpath(file_path, self.repo_path)
        if rel_path in (".", ""):
            return "[root]"
        parts = rel_path.split(os.sep)
        top_level = parts[0] if parts else "[root]"
        if top_level in ("", "."):
            return "[root]"
        return top_level


def update_submodules(repo: git.Repo):
    """Force-update submodules to match the current commit."""
    args = ["update", "--init", "--recursive", "--force", "--checkout"]
    try:
        repo.git.submodule(*args)
    except GitCommandError as exc:
        # 有些 Git 版本会把信息写在 stdout
        output = ""
        if getattr(exc, "stderr", None):
            output += exc.stderr
        if getattr(exc, "stdout", None):
            output += exc.stdout
        if output:
            logger.error(f"Submodule update failed: {output.strip()}")
        raise


def deinit_submodules(repo: git.Repo):
    """Remove registered submodules to avoid stale directories."""
    try:
        repo.git.submodule("deinit", "--all", "--force")
    except GitCommandError as exc:
        logger.warning(f"Submodule deinit failed: {exc}")


def clean_worktree(repo: git.Repo, logger: logging.Logger):
    """Remove untracked files and directories to match the checked-out commit."""
    try:
        repo.git.clean("-xfd")
    except GitCommandError as exc:
        logger.warning(f"git clean failed: {exc}")


def remove_orphan_submodule_dirs(repo_path: str, repo: git.Repo, logger: logging.Logger):
    """Remove lingering submodule directories that are not tracked in the current commit."""
    try:
        tracked_paths = set(repo.git.ls_files().splitlines())
    except GitCommandError as exc:
        logger.warning(f"git ls-files failed: {exc}")
        tracked_paths = set()

    orphan_dirs = []
    for root, dirs, files in os.walk(repo_path):
        git_file = os.path.join(root, ".git")
        if not os.path.isfile(git_file):
            continue
        rel_path = os.path.relpath(root, repo_path).replace("\\", "/")
        if rel_path == ".":
            continue
        if rel_path not in tracked_paths:
            orphan_dirs.append(root)

    for path in orphan_dirs:
        logger.info(f"Removing orphan submodule directory: {path}")
        shutil.rmtree(path, ignore_errors=True)


def plot_repo_stats(daily_line_count, daily_word_count, daily_commit_count,
                    top_level_word_count, output_path, figsize=(15, 10), linewidth=2,
                    top_n_folders=8, data_updated_text: str | None = None,
                    note_updated_text: str | None = None):
    """绘制代码库统计数据的曲线图"""
    if not daily_line_count:
        logger.warning("No data available for plotting")
        return

    # 准备日期范围
    all_dates = sorted(set(daily_line_count.keys()) |
                       set(daily_word_count.keys()) |
                       set(daily_commit_count.keys()))

    start_date = min(all_dates)
    end_date = date.today()
    date_range = [start_date + timedelta(days=i)
                  for i in range((end_date - start_date).days + 1)]

    # 填充数据
    line_counts = []
    word_counts = []
    commit_counts = []

    current_line = 0
    current_word = 0

    for day in date_range:
        if day in daily_line_count:
            current_line = daily_line_count[day]
        line_counts.append(current_line)

        if day in daily_word_count:
            current_word = daily_word_count[day]
        word_counts.append(current_word)

        commit_counts.append(daily_commit_count.get(day, 0))

    # 创建图表并共享输出画布
    fig = plt.figure(figsize=figsize)
    gs = fig.add_gridspec(2, 5, height_ratios=[2, 1])
    ax1 = fig.add_subplot(gs[0, :])
    ax_bar = fig.add_subplot(gs[1, :3])
    ax_donut = fig.add_subplot(gs[1, 3])
    ax_legend = fig.add_subplot(gs[1, 4])

    # 行数和字数曲线
    line1 = ax1.plot(date_range, line_counts, 'b-', label='lines', linewidth=linewidth)
    line2 = ax1.plot(date_range, word_counts, 'g-', label='words', linewidth=linewidth)

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Lines / Words', color='g')
    ax1.tick_params(axis='y', labelcolor='g')
    ax1.set_xlim(start_date, end_date + (end_date - start_date) * 0.05)
    max_word = max(daily_word_count.values()) if daily_word_count else 0
    if max_word > 0:
        ax1.set_ylim(0, max_word * 1.1)

    # 提交次数曲线 - 改为填充区域
    ax2 = ax1.twinx()
    # 使用fill_between代替plot，创建与x轴之间的填充区域
    ax2.fill_between(date_range, commit_counts, 0, color='red', alpha=0.2, label='commits per day')

    ax2.set_ylabel('Commits per Day', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.set_ylim(0, 100)

    # 设置x轴格式
    total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    interval = max(1, total_months // 16)
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=interval))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    for label in ax1.get_xticklabels():
        label.set_rotation(45)

    # 添加图例和网格
    from matplotlib.patches import Patch
    lines = line1 + line2
    patch = Patch(facecolor='red', alpha=0.4, label='commits per day')
    handles = lines + [patch]
    labels = [l.get_label() for l in lines] + ['commits per day']

    ax1.legend(handles, labels, loc='upper left')
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 绘制一级目录字数统计
    total_words = sum(top_level_word_count.values()) if top_level_word_count else 0
    if total_words > 0:
        sorted_folders = sorted(
            top_level_word_count.items(), key=lambda item: item[1], reverse=True
        )
        top_folders = sorted_folders[:top_n_folders]
        folder_labels = [name for name, _ in top_folders]
        folder_counts = [count for _, count in top_folders]

        colors = plt.cm.tab20(np.linspace(0, 1, len(top_folders)))
        counts_k = [count / 1000 for count in folder_counts]
        percentages = [round((count / total_words) * 100) for count in folder_counts]

        indices = np.arange(len(folder_labels))
        bars = ax_bar.bar(indices, counts_k, color=colors)
        ax_bar.set_ylabel('Word Count (k)')
        ax_bar.set_title(f'Top Notebooks by Word Count')
        ax_bar.set_xticks(indices)

        def wrap_label(label: str, max_width: float = 5.0) -> str:
            lines = []
            current = ''
            width = 0.0
            for ch in label:
                if ch.isascii() and ch.strip():
                    char_width = 2 / 3
                elif ch.isascii():
                    char_width = 2 / 3
                else:
                    char_width = 1.0
                if current and width + char_width > max_width:
                    lines.append(current)
                    current = ch
                    width = char_width
                else:
                    current += ch
                    width += char_width
            if current:
                lines.append(current)
            return '\n'.join(lines) if lines else label

        formatted_labels = [wrap_label(label) for label in folder_labels]
        ax_bar.set_xticklabels(formatted_labels, ha='center')
        max_height = max(counts_k) if counts_k else 0
        if max_height > 0:
            ax_bar.set_ylim(0, max_height * 1.25)
        y_offset = max_height * 0.02 if max_height else 0.1

        for bar, count_k, pct in zip(bars, counts_k, percentages):
            ax_bar.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + y_offset,
                f'{count_k:.1f}k\n{pct}%',
                ha='center',
                va='bottom',
                fontsize=9
            )

        wedges, _ = ax_donut.pie(
            folder_counts,
            colors=colors,
            startangle=90,
            wedgeprops={'width': 0.4, 'edgecolor': 'white'}
        )
        for wedge, pct in zip(wedges, percentages):
            if pct == 0:
                continue
            angle = np.deg2rad((wedge.theta2 + wedge.theta1) / 2)
            radius = wedge.r + 0.15
            ax_donut.text(
                np.cos(angle) * radius,
                np.sin(angle) * radius,
                f'{pct}%',
                ha='center',
                va='center',
                fontsize=9
            )

        ax_legend.axis('off')
        ax_legend.legend(
            wedges,
            folder_labels,
            loc='center',
            frameon=False
        )
    else:
        for ax in (ax_bar, ax_donut, ax_legend):
            ax.text(
                0.5,
                0.5,
                'No folder word count data available',
                transform=ax.transAxes,
                ha='center',
                va='center'
            )
            ax.set_axis_off()

    ax1.set_title('Notebooks Statistics Overview', pad=8)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    if total_words > 0:
        donut_box = ax_donut.get_position(fig)
        legend_box = ax_legend.get_position(fig)
        center_x = (donut_box.x0 + legend_box.x1) / 2
        top_y = max(donut_box.y1, legend_box.y1) + 0.02
        fig.text(
            center_x,
            top_y,
            'Word Share by Notebook',
            ha='center',
            va='bottom',
            fontsize=12
        )

    # 保存图表
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    annotation_lines = []
    if data_updated_text:
        annotation_lines.append(data_updated_text)
    if note_updated_text:
        annotation_lines.append(note_updated_text)
    if annotation_lines:
        fig.text(
            0.99,
            0.02,
            "\n".join(annotation_lines),
            ha='right',
            va='bottom',
            fontsize=10,
        )

    fig.savefig(output_path)
    logger.info(f"Statistics chart saved to {output_path}")

    # 显示图表
    # plt.show()


def load_statistics(cache_file):
    """从JSON文件加载统计数据"""
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading statistics cache: {e}")
    return {}


def save_statistics(cache_file, statistics):
    """保存统计数据到JSON文件"""
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2)
        #logger.info(f"Statistics cache saved to {cache_file}")
    except Exception as e:
        logger.error(f"Error saving statistics cache: {e}")


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Generate repository statistics report')
    parser.add_argument('--output', type=str,
                        help='Path to save the statistics chart')
    parser.add_argument('--cache', type=str, default='./statistics.json',
                        help='Path to statistics cache file')
    parser.add_argument('--repo-path', type=str, default='./Notebooks',
                        help='Path to the target repository for statistics')
    parser.add_argument('--filter-config', type=str, default=None,
                        help='Path to statistics filter config JSON')
    # 添加日志路径参数
    parser.add_argument('--log', type=str, default=None,
                        help='Path to log file (appended mode)')
    args = parser.parse_args()

    # 配置日志
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if args.log:
        # 确保日志目录存在
        log_dir = os.path.dirname(args.log)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        # 配置文件日志（追加模式）
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(args.log, mode='a', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
    else:
        # 只配置控制台日志
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler()]
        )
    
    logger.info(f"Starting repository statistics analysis")
    logger.info(f"Command line arguments: {args}")

    # 初始化仓库
    repo_path = os.path.abspath(args.repo_path)
    logger.info(f"Using repository path: {repo_path}")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filter_config_path = args.filter_config
    if filter_config_path is None:
        filter_config_path = os.path.join(script_dir, "statistics_config.json")
    elif not os.path.isabs(filter_config_path):
        filter_config_path = os.path.abspath(filter_config_path)
    filter_config = load_filter_config(filter_config_path)
    current_filter_hash = filter_config_hash(filter_config)
    logger.info(f"Using statistics filter config: {filter_config_path}")
    repo = git.Repo(repo_path)
    repo.git.checkout("-f", "master")
    repo.git.pull()
    deinit_submodules(repo)
    clean_worktree(repo, logger)
    remove_orphan_submodule_dirs(repo_path, repo, logger)
    update_submodules(repo)
    
    # 加载历史统计
    cache_file = args.cache
    statistics_cache = load_statistics(cache_file)
    
    # 获取所有commit（从旧到新）
    commits = list(repo.iter_commits('master', reverse=True))
    logger.info(f"Found {len(commits)} commits in repository")
    
    # 处理新commit
    new_entries = 0
    for commit in commits:
        hexsha = commit.hexsha
        cached = statistics_cache.get(hexsha)
        if isinstance(cached, dict) and cached.get('filter_hash') == current_filter_hash:
            continue
            
        try:
            repo.git.checkout("-f", hexsha)
            deinit_submodules(repo)
            clean_worktree(repo, logger)
            remove_orphan_submodule_dirs(repo_path, repo, logger)
            update_submodules(repo)
            repo_stats = RepoStatistics(repo_path, filter_config)
            statistics_cache[hexsha] = {
                'date': commit.committed_datetime.isoformat(),
                'line_count': repo_stats.line_count,
                'word_count': repo_stats.word_count,
                'filter_hash': current_filter_hash,
            }
            new_entries += 1
            logger.info(
                f"Processed commit {hexsha[:7]}: date: {commit.committed_datetime.isoformat()}, {repo_stats.line_count} lines, {repo_stats.word_count} words"
            )
            
            # 实时保存缓存
            save_statistics(cache_file, statistics_cache)
        except Exception as e:
            logger.error(f"Error processing commit {hexsha[:7]}: {e}")
    
    # 恢复master分支
    repo.git.checkout("-f", "master")
    deinit_submodules(repo)
    clean_worktree(repo, logger)
    remove_orphan_submodule_dirs(repo_path, repo, logger)
    update_submodules(repo)
    repo_stats_current = RepoStatistics(repo_path, filter_config)
    top_level_word_count = repo_stats_current.top_level_word_counts
    
    if new_entries:
        logger.info(f"Added {new_entries} new commit statistics")
    else:
        logger.info("No new commits to process")
    
    # 准备绘图数据
    daily_line_count = defaultdict(int)
    daily_word_count = defaultdict(int)
    daily_commit_count = defaultdict(int)
    
    for data in statistics_cache.values():
        commit_date = date.fromisoformat(data['date'][:10])
        daily_line_count[commit_date] = data['line_count']
        daily_word_count[commit_date] = data['word_count']
        daily_commit_count[commit_date] += 1
    
    # 生成图表
    tz_utc8 = timezone(timedelta(hours=8))
    now_local = datetime.now(tz_utc8)
    latest_commit = repo.head.commit.committed_datetime
    if latest_commit.tzinfo is None:
        latest_commit = latest_commit.replace(tzinfo=timezone.utc)
    latest_commit_local = latest_commit.astimezone(tz_utc8)
    data_updated_text = f"数据更新日期：{now_local.strftime('%Y-%m-%d')}"
    note_updated_text = f"笔记更新日期：{latest_commit_local.strftime('%Y-%m-%d')}"

    if args.output:
        plot_repo_stats(
            daily_line_count,
            daily_word_count,
            daily_commit_count,
            top_level_word_count,
            args.output,
            data_updated_text=data_updated_text,
            note_updated_text=note_updated_text,
        )
    else:
        logger.warning("No output path specified, skipping chart generation")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
