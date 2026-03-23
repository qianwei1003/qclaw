/**
 * Task Dispatcher - 多智能体任务分发器
 * 
 * 根据任务类型自动派发给合适的智能体，或支持手动指定
 */

// 关键词到智能体ID的映射
const AGENT_KEYWORDS = {
  "crawler": ["爬", "抓取", "采集", "获取网页", "搜索", "爬虫"],
  "coder": ["代码", "编程", "写程序", "开发", "调试", "bug", "写个"],
  "analyst": ["分析", "统计", "数据", "对比", "趋势", "研究"],
  "writer": ["写", "文档", "整理", "报告", "润色", "改写", "整理成"],
  "researcher": ["研究", "调研", "调查", "了解", "分析"],
};

/**
 * 根据任务内容匹配最合适的智能体
 * @param {string} task - 任务描述
 * @returns {string|null} - 匹配的智能体ID，没有匹配返回null
 */
function matchAgent(task) {
  const scores = {};
  
  for (const [agentId, keywords] of Object.entries(AGENT_KEYWORDS)) {
    scores[agentId] = 0;
    for (const keyword of keywords) {
      if (task.includes(keyword)) {
        scores[agentId] += keyword.length; // 匹配越长的关键词得分越高
      }
    }
  }
  
  // 找出得分最高的智能体
  let bestAgent = null;
  let bestScore = 0;
  
  for (const [agentId, score] of Object.entries(scores)) {
    if (score > bestScore) {
      bestScore = score;
      bestAgent = agentId;
    }
  }
  
  return bestAgent;
}

/**
 * 解析手动 @ 指定的智能体
 * @param {string} task - 任务描述
 * @returns {{agent: string, task: string}|null} - 解析结果
 */
function parseAtMention(task) {
  const atMatch = task.match(/@(\w+)/);
  if (atMatch) {
    return {
      agent: atMatch[1],
      task: task.replace(/@\w+/, "").trim()
    };
  }
  return null;
}

/**
 * 判断是否需要多智能体协作
 * @param {string} task - 任务描述
 * @returns {boolean}
 */
function needsCollaboration(task) {
  const collabKeywords = ["协作", "合作", "并且", "同时", "对比", "比较"];
  return collabKeywords.some(kw => task.includes(kw));
}

/**
 * 分解协作任务为子任务
 * @param {string} task - 任务描述
 * @returns {string[]} - 子任务数组
 */
function decomposeTask(task) {
  // 按逗号分解
  if (task.includes(",")) {
    return task.split(",").map(s => s.trim()).filter(s => s);
  }
  
  // 按"和"、"与"分解
  if (task.includes("和") || task.includes("与")) {
    return task.split(/和|与/).map(s => s.trim()).filter(s => s);
  }
  
  // 按"并"分解
  if (task.includes("并")) {
    const parts = task.split("并");
    return [parts[0], "并" + parts.slice(1).join("并")].map(s => s.trim()).filter(s => s);
  }
  
  return [task];
}

/**
 * 派发任务 - 主入口
 * @param {string} task - 任务描述
 * @param {Object} options - 选项
 * @param {string} options.manualAgent - 手动指定的智能体ID
 * @param {boolean} options.multiAgent - 是否多智能体协作
 * @param {string} options.mode - 协作模式：pipeline | parallel | discussion
 * @returns {Promise<Object>} - 任务执行结果
 */
async function dispatch(task, options = {}) {
  const { manualAgent, multiAgent = false, mode = "pipeline" } = options;
  
  // 1. 手动 @ 指定
  const atResult = parseAtMention(task);
  if (atResult) {
    console.log(`[TaskDispatcher] 手动指定智能体: ${atResult.agent}`);
    return await spawnAgent(atResult.agent, atResult.task);
  }
  
  // 2. 手动指定智能体
  if (manualAgent) {
    console.log(`[TaskDispatcher] 使用指定智能体: ${manualAgent}`);
    return await spawnAgent(manualAgent, task);
  }
  
  // 3. 判断是否需要多智能体协作
  if (multiAgent || needsCollaboration(task)) {
    console.log(`[TaskDispatcher] 多智能体协作模式: ${mode}`);
    return await multiAgentCollaboration(task, mode);
  }
  
  // 4. 关键词自动匹配
  const matchedAgent = matchAgent(task);
  if (matchedAgent) {
    console.log(`[TaskDispatcher] 关键词匹配智能体: ${matchedAgent}`);
    return await spawnAgent(matchedAgent, task);
  }
  
  // 5. 默认主智能体处理
  console.log(`[TaskDispatcher] 使用主智能体处理`);
  return { agent: "main", task, status: "handled_by_main" };
}

/**
 * 派发任务给指定智能体
 * @param {string} agentId - 智能体ID
 * @param {string} task - 任务描述
 * @returns {Promise<Object>}
 */
async function spawnAgent(agentId, task) {
  // 使用 sessions_spawn 派发给子代理
  const sessionKey = await sessions_spawn({
    task: task,
    label: `dispatch-${agentId}-${Date.now()}`,
    runtime: "subagent",
  });
  
  return { 
    agent: agentId, 
    task, 
    sessionKey,
    status: "spawned" 
  };
}

/**
 * 多智能体协作
 * @param {string} task - 任务描述
 * @param {string} mode - 协作模式
 * @returns {Promise<Object>}
 */
async function multiAgentCollaboration(task, mode = "pipeline") {
  switch (mode) {
    case "parallel":
      return await parallelCollaboration(task);
    case "discussion":
      return await discussionCollaboration(task);
    case "pipeline":
    default:
      return await pipelineCollaboration(task);
  }
}

/**
 * 流水线协作：串行执行，后一个依赖前一个的结果
 * 例如：爬虫 → 分析师 → 写作
 */
async function pipelineCollaboration(task) {
  const steps = [];
  
  // 判断任务需要的步骤
  const hasSearch = task.includes("爬") || task.includes("研究") || task.includes("调查");
  const hasAnalysis = task.includes("分析") || task.includes("对比") || task.includes("统计");
  const hasWriting = task.includes("写") || task.includes("整理") || task.includes("报告");
  
  // 步骤1：爬虫/研究
  let currentTask = task;
  if (hasSearch) {
    console.log(`[Pipeline] 步骤1: 爬虫/研究`);
    const crawlerResult = await spawnAgent("crawler", currentTask);
    steps.push(crawlerResult);
    currentTask = `基于以下资料：\n${crawlerResult.output || "请分析任务结果"}\n\n请进行分析。`;
  }
  
  // 步骤2：分析
  if (hasAnalysis) {
    console.log(`[Pipeline] 步骤2: 分析`);
    const analystResult = await spawnAgent("analyst", currentTask);
    steps.push(analystResult);
    currentTask = `基于以下分析结果：\n${analystResult.output || "请根据分析结果"}\n\n请整理成报告。`;
  }
  
  // 步骤3：写作
  if (hasWriting) {
    console.log(`[Pipeline] 步骤3: 写作`);
    const writerResult = await spawnAgent("writer", currentTask);
    steps.push(writerResult);
  }
  
  return {
    mode: "pipeline",
    steps,
    finalOutput: steps[steps.length - 1]?.output
  };
}

/**
 * 并行协作：同时执行多个独立子任务
 * 例如：同时爬取 React, Vue, Angular
 */
async function parallelCollaboration(task) {
  // 分解任务
  const subtasks = decomposeTask(task);
  console.log(`[Parallel] 分解为 ${subtasks.length} 个子任务`);
  
  // 并行执行所有子任务
  const results = await Promise.all(
    subtasks.map((subtask, index) => 
      spawnAgent("crawler", { task: subtask, index })
    )
  );
  
  return {
    mode: "parallel",
    subtasks,
    results,
    mergedOutput: results.map(r => r.output).join("\n\n---\n\n")
  };
}

/**
 * 讨论协作：多角度分析
 * 例如：代码助手 + 分析师 + 写手一起分析一个问题
 */
async function discussionCollaboration(task) {
  const perspectives = [
    { agent: "coder", angle: "代码质量角度" },
    { agent: "analyst", angle: "性能角度" },
    { agent: "writer", angle: "可维护性角度" }
  ];
  
  console.log(`[Discussion] 多角度分析：${perspectives.length} 个视角`);
  
  // 同时派发给多个智能体
  const results = await Promise.all(
    perspectives.map(p => 
      spawnAgent(p.agent, `${task}（请从${p.angle}分析）`)
    )
  );
  
  return {
    mode: "discussion",
    perspectives,
    results,
    summary: results.map(r => r.output).join("\n\n")
  };
}

/**
 * 创建多个子智能体并行处理
 * 用于复杂任务分解
 */
async function createSubagents(parentAgent, task, subagentCount = 3) {
  const subtasks = [];
  
  // 简单分解任务
  const taskLength = task.length;
  const chunkSize = Math.ceil(taskLength / subagentCount);
  
  for (let i = 0; i < subagentCount; i++) {
    const start = i * chunkSize;
    const end = start + chunkSize;
    subtasks.push(task.slice(start, end));
  }
  
  console.log(`[Subagents] 创建 ${subagentCount} 个子智能体`);
  
  // 并行创建子智能体
  const subagents = await Promise.all(
    subtasks.map((subtask, index) =>
      sessions_spawn({
        task: subtask,
        label: `${parentAgent}-sub-${index}-${Date.now()}`,
        runtime: "subagent",
      })
    )
  );
  
  // 等待所有子智能体完成
  const results = await Promise.all(
    subagents.map(s => s.waitForComplete?.() || Promise.resolve({}))
  );
  
  return {
    parentAgent,
    subagentCount,
    results,
    mergedOutput: results.map(r => r.output || "").join("\n\n")
  };
}

// 导出函数供外部调用
module.exports = {
  dispatch,
  matchAgent,
  parseAtMention,
  needsCollaboration,
  decomposeTask,
  spawnAgent,
  multiAgentCollaboration,
  pipelineCollaboration,
  parallelCollaboration,
  discussionCollaboration,
  createSubagents,
  AGENT_KEYWORDS
};
