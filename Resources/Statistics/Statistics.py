import os
import re
import json
import argparse
import logging
from collections import defaultdict, deque
from datetime import date, timedelta
import git
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# 配置日志将在main函数中根据命令行参数完成
logger = logging.getLogger(__name__)


class DocStatistics:
    def __init__(self, path: str):
        self.path = path
        self.line_count = 0
        self.char_count = 0
        self.update_statistics()

    def update_statistics(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                content = file.read()
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
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self._doc_types = [".md"]
        self._doc_statistics = []
        self.update_statistics()

    def update_statistics(self):
        self._doc_statistics = []
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if any(file.endswith(ext) for ext in self._doc_types):
                    file_path = os.path.join(root, file)
                    doc_statistics = DocStatistics(file_path)
                    self._doc_statistics.append(doc_statistics)

    @property
    def word_count(self) -> int:
        return sum(stat.char_count for stat in self._doc_statistics)

    @property
    def line_count(self) -> int:
        return sum(stat.line_count for stat in self._doc_statistics)


def plot_repo_stats(daily_line_count, daily_word_count, daily_commit_count, 
                    output_path, figsize=(15, 6), linewidth=2):
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

    # 创建图表
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # 行数和字数曲线
    line1 = ax1.plot(date_range, line_counts, 'b-', label='lines', linewidth=linewidth)
    line2 = ax1.plot(date_range, word_counts, 'g-', label='words', linewidth=linewidth)
    
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Lines / Words', color='g')
    ax1.tick_params(axis='y', labelcolor='g')
    ax1.set_xlim(start_date, end_date + (end_date - start_date) * 0.05)
    ax1.set_ylim(0, max(list(daily_word_count.values())) * 1.1)
    
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
    plt.xticks(rotation=45)
    
    # 添加图例和网格
    # 获取所有图例元素
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    # 添加填充区域的图例（使用Patch）
    from matplotlib.patches import Patch
    patch = Patch(facecolor='red', alpha=0.4, label='commits per day')
    handles = lines + [patch]
    labels.append('commits per day')
    
    ax1.legend(handles, labels, loc='upper left')
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    plt.title('Repository Statistics Over Time')
    plt.tight_layout()
    
    # 保存图表
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path)
    logger.info(f"Statistics chart saved to {output_path}")
    
    # 显示图表
    plt.show()


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
    repo_path = "./Notebooks"
    repo = git.Repo(repo_path)
    repo.git.checkout("-f", "master")
    repo.git.pull()
    
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
        if hexsha in statistics_cache:
            continue
            
        try:
            repo.git.checkout("-f", hexsha)
            repo.submodule_update()
            repo_stats = RepoStatistics(repo_path)
            statistics_cache[hexsha] = {
                'date': commit.committed_datetime.isoformat(),
                'line_count': repo_stats.line_count,
                'word_count': repo_stats.word_count
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
    if args.output:
        plot_repo_stats(daily_line_count, daily_word_count, daily_commit_count, args.output)
    else:
        logger.warning("No output path specified, skipping chart generation")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {e}")
