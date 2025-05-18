#用于生成项目文件层级并配置相应文件开头用途注释
import json
from pathlib import Path

def get_file_comment(file_path, manual_file_comments, root_dir):
    """优化后：自动注释+main函数手动注释双模式"""
    comment_map = {
        '.do': ('#',),          # DO文件单行注释
        '.json': ('#',),        # JSON文件单行注释
        '.txt': ('#',),          # 文本文件单行注释
        '.md': ('<!--', '-->'),  # Markdown使用HTML块注释
        '.py': ('#',),           # Python多行注释
        '.js': ('//',),          # JavaScript单行注释
        '.html': ('<!--', '-->'),# HTML块注释
        '.sh': ('#',),           # Shell单行注释
        '.c': ('//', '/*', '*/'),# C语言混合注释
    }
    
    ext = Path(file_path).suffix.lower()
    symbols = comment_map.get(ext, ())
    
    # 优先尝试自动读取注释
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2048)  # 读取前2048字节
            lines = content.split('\n')[:20]  # 检查前20行
            
            # 处理Python多行#注释（连续行）
            if ext == '.py' and symbols[0] == '#':
                comment_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith('#'):
                        comment = stripped[1:].strip()  # 移除#号
                        comment_lines.append(comment)
                    else:
                        break  # 非注释行停止读取
                auto_comment = '\n'.join(comment_lines) if comment_lines else None
            
            # 处理Markdown/HTML块注释（<!-- -->）
            elif len(symbols) == 2:
                start, end = symbols
                in_comment = False
                comment_lines = []
                for line in lines:
                    stripped = line.strip()
                    if start in stripped and not in_comment:
                        in_comment = True
                        comment_part = stripped.split(start, 1)[1]
                        if end in comment_part:  # 单行块注释
                            auto_comment = comment_part.split(end, 1)[0].strip()
                            break
                        comment_lines.append(comment_part.strip())
                    elif in_comment:
                        if end in stripped:  # 找到结束标记
                            comment_part = stripped.split(end, 1)[0].strip()
                            comment_lines.append(comment_part)
                            auto_comment = '\n'.join(comment_lines).strip()
                            break
                        comment_lines.append(stripped)
                auto_comment = '\n'.join(comment_lines).strip() if comment_lines else None
            
            # 处理其他单行注释（如JavaScript的//）
            elif len(symbols) == 1:
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith(symbols[0]):
                        auto_comment = stripped[len(symbols[0]):].strip()
                        break
                else:
                    auto_comment = None
            
            else:
                auto_comment = None  # 不支持的文件类型
            
            # 自动注释存在则返回，否则查手动注释
            if auto_comment:
                return auto_comment
            else:
                # 统一路径分隔符为斜杠（兼容不同系统）
                rel_path = str(file_path.relative_to(root_dir)).replace('\\', '/')
                return manual_file_comments.get(rel_path)  # 返回main函数中的手动注释
    
    except Exception as e:
        print(f"警告：读取文件 {file_path} 失败，原因：{str(e)}")
        return None

def load_dir_comments(root_dir):
    """加载目录注释配置"""
    config_path = Path(root_dir) / "dir_comments.json"
    if not config_path.exists():
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"警告：目录注释配置文件读取失败，原因：{str(e)}")
        return {}

def generate_structure(root_dir, manual_file_comments):
    root_dir = Path(root_dir).resolve()
    if not root_dir.exists():
        raise FileNotFoundError(f"目录不存在：{root_dir}")
    
    dir_comments = load_dir_comments(root_dir)
    structure = [f"{root_dir.name}/"]
    
    # 定义需要排除的路径（相对于项目根目录）
    excluded_paths = {
        '.git'
    }

    def walk_dir(current_dir, prefix='', is_last=False):
        items = list(current_dir.iterdir())
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))  # 目录优先+按名称排序
        
        for i, item in enumerate(items):
            # 计算当前项相对于根目录的路径（用于排除判断）
            rel_path = str(item.relative_to(root_dir)).replace('\\', '/')  # 统一为斜杠
            if rel_path in excluded_paths:
                continue  # 跳过指定路径
            
            is_last_item = (i == len(items) - 1)
            line_prefix = '└── ' if is_last_item else '├── '
            line = f"{prefix}{line_prefix}{item.name}"
            
            # 处理目录
            if item.is_dir():
                # 目录路径补全斜杠（与manual_file_comments键格式一致）
                rel_dir_path = f"{rel_path}/"
                # 优先使用manual_file_comments的注释，其次是dir_comments
                manual_comment = manual_file_comments.get(rel_dir_path, '')
                dir_comment = dir_comments.get(rel_dir_path, '')
                comment = manual_comment or dir_comment  # 手动注释优先级更高
                comment = f' # {comment}' if comment else ''
                # 计算对齐空格（示例中目录名后有固定空格）
                line += ' ' * (20 - len(item.name)) + comment
                structure.append(line)
                
                # 递归子目录（更新前缀）
                new_prefix = prefix + ('    ' if is_last_item else '│   ')
                walk_dir(item, new_prefix, is_last_item)
            
            # 处理文件
            else:
                # 获取文件注释（自动+手动）
                comment = get_file_comment(item, manual_file_comments, root_dir) or ''
                # 注释换行处理（保持层级结构整洁）
                comment = comment.replace('\n', ' ') if '\n' in comment else comment
                comment = f' # {comment}' if comment else ''
                # 计算对齐空格（示例中文件名后有固定空格）
                line += ' ' * (20 - len(item.name)) + comment
                structure.append(line)
    
    walk_dir(root_dir)
    return '\n'.join(structure)

def save_to_md(content, output_path):
    """将层级结构保存到.md文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 项目文件层级结构\n\n")  # 添加Markdown标题
            f.write(content)
        print(f"成功保存到：{output_path}")
    except Exception as e:
        print(f"保存失败：{str(e)}")

if __name__ == "__main__":
    # 配置参数（可根据需求修改）
    PROJECT_MAIN_DIR = "./"  # 项目根目录路径
    OUTPUT_MD_PATH = "./docs/PROJECT_STRUCTURE.md"               # 输出.md文件路径（自动创建目录）

    # 直接在main函数中定义手动注释字典（键为文件/目录相对路径，统一用斜杠）
    manual_file_comments = {
        # 文件注释示例（斜杠分隔）
        "docs/test.pdf": "测试所用的pdf文件",
        "src/main.py": "项目主入口文件",
        # 目录注释示例（以/结尾）
        "Shared_Resources/Paper/": "参考文献存放处",
        "Local_Files/": "本地文件存放于此，该文件夹下的文件不会被同步到云端仓库，所以大文件直接放在这里",
        "Local_Files/.gitkeep": '用于在空文件夹中占位来让git追踪该文件夹',
    }

    # 确保输出目录存在
    Path(OUTPUT_MD_PATH).parent.mkdir(parents=True, exist_ok=True)

    try:
        # 生成层级结构（传递手动注释字典）
        structure_content = generate_structure(PROJECT_MAIN_DIR, manual_file_comments)
        # 保存到.md文件
        save_to_md(structure_content, OUTPUT_MD_PATH)
    except Exception as e:
        print(f"执行失败：{str(e)}")