# qr-cli

快速生成二维码的 Python 工具，支持剪贴板快捷键和大文本分片处理。

## 功能特性

- **超短命令**: `qr` 一键生成二维码
- **智能分片**: 大文本自动按容量切分成多个二维码
- **按行生成**: 每行一个二维码（适合 URL 列表）
- **默认剪贴板**: 不带参数直接从剪贴板生成
- **快捷键支持**: 按 `F8 + O` 快速获取剪贴板文本生成二维码

## 安装

```bash
pip install qr-cli
```

## 使用方法

### 最常用方式

```bash
# 1. 直接从剪贴板生成
qr

# 2. 从文本生成
qr -t "Hello, World!"

# 3. 指定输出文件
qr -t "https://example.com" -o site.png
```

### 文件处理

**大文本自动分片**（默认）:
```bash
# 将大文本自动切分成多个 QR 码
qr -f large_text.txt -d ./output
# 输出: part_001_of_N.png, part_002_of_N.png, ...
```

**按行生成**（URL 列��等）:
```bash
# 每行生成一个 QR 码
qr -f urls.txt -l -d ./qrcodes
```

### 完整选项

| 选项 | 简写 | 说明 |
|------|------|------|
| --text | -t | 指定文本内容 |
| --clipboard | -c | 从剪贴板读取（默认） |
| --file | -f | 从文件读取 |
| --lines | -l | 按行生成模式 |
| --chunk-size | - | 自定义分片大小（字节） |
| --output | -o | 输出文件路径 |
| --output-dir | -d | 输出目录 |
| --terminal | -T | 在终端显示二维码 |
| --hotkey | -h | 启动快捷键监听 |
| --hotkey-code | - | 自定义快捷键 |

### 常用示例

```bash
# 剪贴板 -> 终端显示
qr -c -T

# 大代码文件 -> 自动分片
qr -f app.py -d ./qr_backup

# URL 列表 -> 每行一个 QR
qr -f urls.txt -l -d ./qrcodes

# 快捷键模式（F8+O）
qr -h
```

### 分片模式说明

当文件内容过大时，默认会自动分片：

- **自动计算**: 根据二维码容量自动计算分片大小
- **元数据**: 每个 QR 包含序列号（如 `1/3:data`）
- **可恢复**: 扫描所有 QR 码可恢复原始数据

### 快捷键模式

启动快捷键监听后，按 `F8 + O` 即可将剪贴板内容转为二维码：

```bash
qr -h
```

- 默认保存位置: `~/qr_output/`
- 文件名格式: `clipboard_{timestamp}_{content}.png`

## Python API

```python
from qr_cli import generate_qr, generate_large_text

# 单个二维码
generate_qr("Hello, World!", output="hello.png")

# 大文本分片生成
generate_large_text(
    large_text,
    output_dir="./qr_chunks",
    chunk_size=500,  # 可选，默认自动计算
)
```

## 注意事项

- Windows 快捷键模式需要管理员权限
- 分片模式按二维码最大容量自动切分
- 按行模式适合 URL 列表等结构化数据

## 许可证

MIT License
