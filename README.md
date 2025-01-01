# 📚 AI 阅读书籍：逐页PDF知识提取与总结器

`read_books.py` 脚本对PDF书籍进行智能逐页分析，系统地提取知识点并在指定间隔生成逐步总结。它逐页处理内容，允许对详细内容进行理解，同时保持书籍的上下文连贯性。以下是脚本的工作原理详细说明：

### 功能

- 📚 自动化PDF书籍分析和知识提取
- 🤖 基于AI的内容理解和总结
- 📊 间隔式进度总结
- 💾 持久化知识库存储
- 📝 Markdown格式的总结
- 🎨 彩色终端输出以提高可见性
- 🔄 使用现有知识库恢复功能
- ⚙️ 可配置的分析间隔和测试模式
- 🚫 智能内容过滤（跳过目录、索引页等）
- 📂 组织良好的输出目录结构

## ❤️ 支持与获取400+AI项目

这是我的400+个有趣项目之一！[在Patreon支持我](https://www.patreon.com/c/echohive42/membership)以获取：

- 🎯 访问400+个AI项目（每天增加！）
  - 包括高级项目如[双代理实时语音模板带轮流发言](https://www.patreon.com/posts/2-agent-real-you-118330397)
- 📥 完整源代码及详细说明
- 📚 1000倍光标课程
- 🎓 实时编码会话及AMA
- 💬 一对一咨询（高级会员）
- 🎁 独家折扣AI工具及平台（最高价值$180）

## 如何使用

1. **设置**

   ```bash
   # 克隆仓库
   git clone [仓库地址]
   cd [仓库名称]

   # 安装依赖
   pip install -r requirements.txt
   ```
2. **配置**

   - 将PDF文件放置在项目根目录中
   - 打开 `read_books.py` 并更新 `PDF_NAME` 常量以使用您的PDF文件名
   - （可选）调整其他常量如 `ANALYSIS_INTERVAL` 或 `TEST_PAGES`
3. **运行**

   ```bash
   python read_books.py
   ```
4. **输出**
   脚本将生成：

   - `book_analysis/knowledge_bases/`: 包含提取知识的JSON文件
   - `book_analysis/summaries/`: 包含间隔和最终总结的Markdown文件
   - `book_analysis/pdfs/`: 您的PDF文件副本
5. **自定义选项**

   - 设置 `ANALYSIS_INTERVAL = None` 以跳过间隔总结
   - 设置 `TEST_PAGES = None` 以处理整本书
   - 调整 `MODEL` 和 `ANALYSIS_MODEL` 以使用不同的AI模型

### 配置常量

- `PDF_NAME`: 要分析的PDF文件名。
- `BASE_DIR`: 分析的基础目录。
- `PDF_DIR`: 存储PDF文件的目录。
- `KNOWLEDGE_DIR`: 存储知识库的目录。
- `SUMMARIES_DIR`: 存储总结的目录。
- `PDF_PATH`: PDF文件的完整路径。
- `OUTPUT_PATH`: 知识库JSON文件的路径。
- `ANALYSIS_INTERVAL`: 生成间隔分析的页数。设置为 `None` 以跳过间隔分析。
- `MODEL`: 用于处理页面的模型。
- `ANALYSIS_MODEL`: 用于生成分析的模型。
- `TEST_PAGES`: 用于测试的页数。设置为 `None` 以处理整本书。

### 类和函数

#### `PageContent` 类

一个Pydantic模型，表示从OpenAI API获取的页面内容分析响应结构。它有两个字段：

- `has_content`: 布尔值，指示页面是否有相关内容。
- `knowledge`: 从页面提取的知识点列表。

#### `load_or_create_knowledge_base() -> Dict[str, Any]`

如果存在，则从JSON文件加载现有知识库。如果不存在，则返回一个空字典。

#### `save_knowledge_base(knowledge_base: list[str])`

将知识库保存到JSON文件。它打印一条消息，指示保存的项目数量。

#### `process_page(client: OpenAI, page_text: str, current_knowledge: list[str], page_num: int) -> list[str]`

处理PDF的单页。它将页面文本发送到OpenAI API进行分析，并使用提取的知识点更新知识库。它还将更新的知识库保存到JSON文件。

#### `load_existing_knowledge() -> list[str]`

如果存在，则从JSON文件加载现有知识库。如果不存在，则返回一个空列表。

#### `analyze_knowledge_base(client: OpenAI, knowledge_base: list[str]) -> str`

使用OpenAI API生成整个知识库的综合总结。它以Markdown格式返回总结。

#### `setup_directories()`

设置分析所需的目录。它清除任何先前生成的文件，并确保PDF文件位于正确位置。

#### `save_summary(summary: str, is_final: bool = False)`

将生成的总结保存到Markdown文件。它根据是否为最终总结创建一个适当的文件名。

#### `print_instructions()`

打印使用脚本的说明。它解释配置选项和如何运行脚本。

#### `main()`

主函数，协调整个过程。它设置目录，加载知识库，处理PDF的每一页，生成间隔和最终总结，并保存它们。

### 工作原理

1. **设置**: 脚本设置必要的目录，并确保PDF文件位于正确位置。
2. **加载知识库**: 它加载现有知识库（如果存在）。
3. **处理页面**: 它处理PDF的每一页，提取知识点并更新知识库。
4. **生成总结**: 它根据 `ANALYSIS_INTERVAL` 生成间隔总结，并在处理完所有页面后生成最终总结。
5. **保存结果**: 它将知识库和总结保存到各自的文件中。

### 运行脚本

1. 将您的PDF文件放置在与脚本相同的目录中。
2. 使用您的PDF文件名更新 `PDF_NAME` 常量。
3. 运行脚本。它将处理书籍，提取知识点并生成总结。

### 使用示例
