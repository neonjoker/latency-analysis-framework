#!/bin/bash
set -e

echo "🔧 设置 Python 环境..."

# 检查 pyenv
if ! command -v pyenv &> /dev/null; then
    echo "❌ pyenv 未安装，请先安装 pyenv"
    exit 1
fi

# 设置 Python 版本
echo "📦 设置 Python 3.11.8..."
pyenv install 3.11.8 --skip-existing
pyenv local 3.11.8

# 创建虚拟环境
echo "🌱 创建虚拟环境..."
python -m venv .venv

# 激活虚拟环境
echo "⚡ 激活虚拟环境..."
source .venv/bin/activate

# 升级 pip
echo "📈 升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt

# 验证安装
echo "✅ 验证安装..."
python --version
pytest --version
fastapi --version

echo "🎉 环境设置完成！"
echo ""
echo "使用方法:"
echo "  source .venv/bin/activate  # 激活虚拟环境"
echo "  claude                     # 启动 Claude Code"
