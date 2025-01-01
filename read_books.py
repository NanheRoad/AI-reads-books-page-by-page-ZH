from ,athlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel
import json
from openai import OpenAI
import fitz  # PyMuPDF
from termcolor import colored
from datetime import datetime
import shutil

# source for the infinite descent book: https://infinitedescent.xyz/dl/infdesc.pdf

""" 
使用前需设置环境变量
1.临时设置环境变量（仅对当前终端会话有效）：
export OPENAI_API_KEY=your_api_key_here
2.永久设置环境变量（对所有终端会话有效）：
在 ~/.bashrc 或 ~/.zshrc 文件中添加以下行：
export OPENAI_API_KEY=your_api_key_here
然后运行以下命令使更改生效：
source ~/.bashrc  # 或 source ~/.zshrc
3.在代码中传递 API 密钥（不推荐）
如果你选择在代码中传递 API 密钥，请确保将其存储在安全的位置，并且不要将其提交到版本控制系统中。
client = OpenAI(api_key="your_api_key_here") 
"""


# 配置常量
PDF_NAME = "meditations.pdf"
BASE_DIR = Path("book_analysis")
PDF_DIR = BASE_DIR / "pdfs"
KNOWLEDGE_DIR = BASE_DIR / "knowledge_bases"
SUMMARIES_DIR = BASE_DIR / "summaries"
PDF_PATH = PDF_DIR / PDF_NAME
OUTPUT_PATH = KNOWLEDGE_DIR / f"{PDF_NAME.replace('.pdf', '_knowledge.json')}"
ANALYSIS_INTERVAL = 20  # 设置为None以跳过间隔分析，或设置为数字（例如，10）以每N页生成分析
MODEL = "gpt-4o-mini"
ANALYSIS_MODEL = "o1-mini"
TEST_PAGES = 60  # 设置为None以处理整本书


class PageContent(BaseModel):
    has_content: bool
    knowledge: list[str]


def load_or_create_knowledge_base() -> Dict[str, Any]:
    if Path(OUTPUT_PATH).exists():
        with open(OUTPUT_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_knowledge_base(knowledge_base: list[str]):
    output_path = KNOWLEDGE_DIR / f"{PDF_NAME.replace('.pdf', '')}_knowledge.json"
    print(colored(f"💾 保存知识库（{len(knowledge_base)} 项）...", "blue"))
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"knowledge": knowledge_base}, f, indent=2)

def process_page(client: OpenAI, page_text: str, current_knowledge: list[str], page_num: int) -> list[str]:
    print(colored(f"\n📖 处理第 {page_num + 1} 页...", "yellow"))
    
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[
            {"role": "system", "content": """分析此页面，如同你在学习一本书。

            跳过包含以下内容的页面：
            - 目录
            - 章节列表
            - 索引页面
            - 空白页面
            - 版权信息
            - 出版详情
            - 参考文献或书目
            - 致谢
            
            提取知识如果页面包含以下内容：
            - 解释重要概念的前言内容
            - 实际教育内容
            - 关键定义和概念
            - 重要论点或理论
            - 示例和案例研究
            - 显著发现或结论
            - 方法论或框架
            - 批判性分析或解释
            
            对于有效内容：
            - 将 has_content 设置为 true
            - 提取详细的、可学习的知识点
            - 包括重要引用或关键陈述
            - 捕获示例及其上下文
            - 保留技术术语和定义
            
            对于要跳过的页面：
            - 将 has_content 设置为 false
            - 返回空知识列表"""},
            {"role": "user", "content": f"页面文本: {page_text}"}
        ],
        response_format=PageContent
    )
    
    result = completion.choices[0].message.parsed
    if result.has_content:
        print(colored(f"✅ 找到 {len(result.knowledge)} 个新知识点", "green"))
    else:
        print(colored("⏭️  跳过页面（无相关内容）", "yellow"))
    
    updated_knowledge = current_knowledge + (result.knowledge if result.has_content else [])
    
    # 更新单个知识库文件
    save_knowledge_base(updated_knowledge)
    
    return updated_knowledge

def load_existing_knowledge() -> list[str]:
    knowledge_file = KNOWLEDGE_DIR / f"{PDF_NAME.replace('.pdf', '')}_knowledge.json"
    if knowledge_file.exists():
        print(colored("📚 加载现有知识库...", "cyan"))
        with open(knowledge_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(colored(f"✅ 加载了 {len(data['knowledge'])} 个现有知识点", "green"))
            return data['knowledge']
    print(colored("🆕 从空白知识库开始", "cyan"))
    return []

def analyze_knowledge_base(client: OpenAI, knowledge_base: list[str]) -> str:
    if not knowledge_base:
        print(colored("\n⚠️  跳过分析：未收集到知识点", "yellow"))
        return ""
        
    print(colored("\n🤔 生成最终书籍分析...", "cyan"))
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": """创建所提供内容的综合摘要，格式简洁但详细，使用代码格式。
           
            使用代码格式：
            - ## 用于主标题
            - ### 用于子标题
            - 项目符号用于列表
            - `代码块` 用于任何代码或公式
            - **粗体** 用于强调
            - *斜体* 用于术语
            - > 块引用用于重要笔记
            
            仅返回代码摘要，不要在前后添加任何其他内容，如“以下是摘要”等"""},
            {"role": "user", "content": f"分析此内容：\n" + "\n".join(knowledge_base)}
        ]
    )
    
    print(colored("✨ 分析生成成功！", "green"))
    return completion.choices[0].message.content

def setup_directories():
    # 清除所有先前生成的文件
    for directory in [KNOWLEDGE_DIR, SUMMARIES_DIR]:
        if directory.exists():
            for file in directory.glob("*"):
                file.unlink()  # 删除这些目录中的所有文件
    
    # 创建所有必要的目录
    for directory in [PDF_DIR, KNOWLEDGE_DIR, SUMMARIES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # 确保PDF位于正确位置
    if not PDF_PATH.exists():
        source_pdf = Path(PDF_NAME)
        if source_pdf.exists():
            # 复制PDF而不是移动它
            shutil.copy2(source_pdf, PDF_PATH)
            print(colored(f"📄 将PDF复制到分析目录：{PDF_PATH}", "green"))
        else:
            raise FileNotFoundError(f"未找到PDF文件 {PDF_NAME}")

def save_summary(summary: str, is_final: bool = False):
    if not summary:
        print(colored("⏭️  跳过摘要保存：无内容可保存", "yellow"))
        return
        
    # 使用适当的命名创建代码文件
    if is_final:
        existing_summaries = list(SUMMARIES_DIR.glob(f"{PDF_NAME.replace('.pdf', '')}_final_*.md"))
        next_number = len(existing_summaries) + 1
        summary_path = SUMMARIES_DIR / f"{PDF_NAME.replace('.pdf', '')}_final_{next_number:03d}.md"
    else:
        existing_summaries = list(SUMMARIES_DIR.glob(f"{PDF_NAME.replace('.pdf', '')}_interval_*.md"))
        next_number = len(existing_summaries) + 1
        summary_path = SUMMARIES_DIR / f"{PDF_NAME.replace('.pdf', '')}_interval_{next_number:03d}.md"
    
    # 创建带有元数据的代码内容
    code_content = f"""# 书籍分析: {PDF_NAME}
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{summary}

---
*使用AI书籍分析工具生成的分析*
"""
    
    print(colored(f"\n📝 保存 {'最终' if is_final else '间隔'}分析到代码...", "cyan"))
    with open(summary_path, 'w', encoding='utf-8') as f:  # 添加了encoding='utf-8'
        f.write(code_content)
    print(colored(f"✅ 分析已保存到: {summary_path}", "green"))


def print_instructions():
    print(colored("""\
📚 PDF书籍分析工具 📚
---------------------------
1. 将您的PDF文件放置在与该脚本相同的目录中
2. 更新PDF_NAME常量以使用您的PDF文件名
3. 该脚本将：
   - 逐页处理书籍
   - 提取并保存知识点
   - 生成间隔摘要（如果启用）
   - 创建最终的综合分析

配置选项：
- ANALYSIS_INTERVAL: 设置为None以跳过间隔分析，或设置为数字以每N页进行分析
- TEST_PAGES: 设置为None以处理整本书，或设置为数字以进行部分处理

按Enter继续或按Ctrl+C退出...
""", "cyan"))


def main():
    try:
        print_instructions()
        input()
    except KeyboardInterrupt:
        print(colored("\n❌ 用户取消了进程", "red"))
        return

    setup_directories()
    client = OpenAI()
    
    # 加载或初始化知识库
    knowledge_base = load_existing_knowledge()
    
    pdf_document = fitz.open(PDF_PATH)
    pages_to_process = TEST_PAGES if TEST_PAGES is not None else pdf_document.page_count
    
    print(colored(f"\n📚 正在处理 {pages_to_process} 页...", "cyan"))
    for page_num in range(min(pages_to_process, pdf_document.page_count)):
        page = pdf_document[page_num]
        page_text = page.get_text()
        
        knowledge_base = process_page(client, page_text, knowledge_base, page_num)
        
        # 如果设置了ANALYSIS_INTERVAL，则生成间隔分析
        if ANALYSIS_INTERVAL:
            is_interval = (page_num + 1) % ANALYSIS_INTERVAL == 0
            is_final_page = page_num + 1 == pages_to_process
            
            if is_interval and not is_final_page:
                print(colored(f"\n📊 进度: {page_num + 1}/{pages_to_process} 页已处理", "cyan"))
                interval_summary = analyze_knowledge_base(client, knowledge_base)
                save_summary(interval_summary, is_final=False)
        
        # 始终在最后一页生成最终分析
        if page_num + 1 == pages_to_process:
            print(colored(f"\n📊 最后一页 ({page_num + 1}/{pages_to_process}) 已处理", "cyan"))
            final_summary = analyze_knowledge_base(client, knowledge_base)
            save_summary(final_summary, is_final=True)
    
    print(colored("\n✨ 处理完成！ ✨", "green", attrs=['bold']))


if __name__ == "__main__":
    main()