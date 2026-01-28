// 0/1背包和完全背包的模板
int solve(vector<int>& weights, int capacity) {
    int illegal = -1;
    // 一维数组形式：dp[j] 表示容量为 j 的情况下，上一轮物品 i 的 dp 表
    vector<int> dp(capacity + 1, illegal);
	
    // 设置初始化条件：当容量为0时，组合为0
    dp[0] = 0;
	
    // i 为物品
    for(int i = 1; i <= weights.size(); i++) {
        // 定义 weight 和 value
		int weight = weights[i - 1];
		int value = 1;
        // j 为容量，需要倒序遍历
        for(int j = capacity; j > 0; j--) {
            // 无论i、j为何值，其一定可以不拿，则：dp[j] = dp[j]
            // dp[j] = dp[j]; // 不拿
			
            // 判定是否可拿条件：
            // 1. 背包可容下当前物品i，即：j >= weight
            // 2. 背包容量为 j - i 时有解，即：[j - weight] != illegal
            if(j >= weight && dp[j - weight] != illegal) {
                // dp = max(不拿, 拿)
                dp[j] = max(
                    dp[j],                // 不拿
                    dp[j - weight] + value  // 拿
                );
            }
        }
    }
	
    // dp[j] 表示背包容量等于 j 时的最大价值
    // 则最大价值为 dp[capacity]
    int max_value = dp[capacity];
    
    return ...; // 按需返回值
}




