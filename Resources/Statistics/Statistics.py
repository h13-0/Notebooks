import os
import re
from collections import deque
import git
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, timedelta


class DocStatistics:
    def __init__(self, path: str):
        self.path = path
        self.line_count = 0
        self.char_count = 0
        self.update_statistics()

    def update_statistics(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                line_count = len(lines)
                char_count = sum(self._count_words(line) for line in lines)
            self.line_count = line_count
            self.char_count = char_count
        except Exception as e:
            print(f"Error reading file {self.path}: {e}")
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
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(tuple(self._doc_types)):
                    file_path = os.path.join(root, file)
                    doc_statistics = DocStatistics(file_path)
                    self._doc_statistics.append(doc_statistics)

    def word_count(self) -> int:
        return sum(statistics.char_count for statistics in self._doc_statistics)

    def line_count(self) -> int:
        return sum(statistics.line_count for statistics in self._doc_statistics)

def plot_repo_stats(daily_line_count, daily_word_count, daily_commit_count, 
                    figsize=(15, 6), linewidth=2):
    """
    绘制代码库统计数据的曲线图
    
    参数:
    daily_line_count (dict): {日期: 总行数}
    daily_word_count (dict): {日期: 总字数}
    daily_commit_count (dict): {日期: 提交次数}
    figsize (tuple): 图表尺寸 (宽, 高)
    linewidth (int): 曲线宽度
    """
    # 1. 准备数据
    # 获取所有日期(包括开始到结束的所有日期)
    all_dates = sorted(set(daily_line_count.keys()) | 
                    set(daily_word_count.keys()) | 
                    set(daily_commit_count.keys()))
    
    if not all_dates:
        return
    
    # 创建连续的日期范围
    start_date = min(all_dates)
    end_date = max(all_dates)
    date_range = [start_date + timedelta(days=i) 
                for i in range((end_date - start_date).days + 1)]
    
    # 2. 填充数据(处理缺失日期)
    line_counts = []
    word_counts = []
    commit_counts = []
    
    current_line = 0
    current_word = 0
    
    for day in date_range:
        # 处理行数(保留最后有效值)
        if day in daily_line_count:
            current_line = daily_line_count[day]
        line_counts.append(current_line)
        
        # 处理字数(保留最后有效值)
        if day in daily_word_count:
            current_word = daily_word_count[day]
        word_counts.append(current_word)
        
        # 处理提交次数(不存在则为0)
        commit_counts.append(daily_commit_count.get(day, 0))

    # 创建主Y轴(用于行数和字数)
    fig, ax1 = plt.subplots(figsize=figsize)
    
    # 绘制行数曲线(左轴)
    line1 = ax1.plot(date_range, line_counts, 'b-', label='lines', linewidth=linewidth, zorder=3, alpha=1)
    # 绘制字数曲线(左轴)
    line2 = ax1.plot(date_range, word_counts, 'g-', label='words', linewidth=linewidth, zorder=2, alpha=1)
    
    # 设置左轴标签
    ax1.set_xlabel('date')
    ax1.set_ylabel('lines / words', color='g')
    ax1.tick_params(axis='y', labelcolor='g')
    ax1.set_ylim(0, max(list(daily_word_count.values())) * 1.1)
    ax1.set_xlim(start_date, end_date + (end_date - start_date) * 0.05)
    
    # 创建右轴(用于提交次数)
    ax2 = ax1.twinx()
    # 绘制提交次数曲线(右轴)
    line3 = ax2.plot(date_range, commit_counts, 'r-', label='commits per day', linewidth=linewidth, zorder=1, alpha=0.5)
    
    # 设置右轴标签
    ax2.set_ylabel('commits per day', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.set_ylim(0, 100)

    
    # 4. 格式化日期轴
    interval = 60
    date_fmt = '%Y-%m'

    # 设置x轴格式
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=interval))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter(date_fmt))
    plt.xticks(rotation=45)
    
    # 5. 添加图例
    # 合并所有图例项
    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left')
    
    # 6. 添加网格和标题
    ax1.grid(True, linestyle='--', alpha=0.7)
    plt.title('Notebooks Statistics')
    plt.tight_layout()
    plt.savefig("./Statistics.svg")
    
    # 显示图表
    plt.show()


def main():
    repo = git.Repo(r"./Notebooks")
    repo.git.pull()
    repo_status = []

    d = deque(repo.iter_commits())
    while d:
        commit = d.pop()
        print(f"Commit: {commit.hexsha}")
        print(f"Author: {commit.author.name}")
        print(f"Date: {commit.committed_datetime}")
        print(f"Message: {commit.message}")

        # 获取仓库状态
        try:
            repo.git.checkout(commit.hexsha)
            repo_statistics = RepoStatistics(r"./Notebooks")
            line_count = repo_statistics.line_count()
            word_count = repo_statistics.word_count()
            repo_status.append((commit.committed_datetime, line_count, word_count))
            print(f"Line count: {line_count}")
            print(f"Word count: {word_count}")
            print("-" * 40)
        except Exception as e:
            repo.git.checkout("master")
            print(f"Error checking out commit {commit.hexsha}: {e}")


    # 按日计算总行数、总字数和当日提交数
    daily_line_count = {}
    daily_word_count = {}
    daily_commit_count = {}
    for date, line_count, word_count in repo_status:
        daily_line_count[date.date()] = line_count
        daily_word_count[date.date()] = word_count
        if date.date() in daily_commit_count:
            daily_commit_count[date.date()] += 1
        else:
            daily_commit_count[date.date()] = 1

    plot_repo_stats(daily_line_count, daily_word_count, daily_commit_count)


if __name__ == "__main__":
    main()
