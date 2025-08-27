#!/bin/bash

echo "========================================"
echo "Outlook OAuth Demo 安装和测试脚本"
echo "========================================"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.7+"
    exit 1
fi

echo "1. 创建虚拟环境..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "错误: 创建虚拟环境失败"
    exit 1
fi

echo "2. 激活虚拟环境..."
source venv/bin/activate

echo "3. 升级pip..."
python -m pip install --upgrade pip

echo "4. 安装依赖包..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 安装依赖包失败"
    exit 1
fi

echo "5. 检查配置文件..."
if [ ! -f "outlook_token.txt" ]; then
    echo "错误: 未找到outlook_token.txt文件"
    echo "请确保该文件存在并包含正确的OAuth配置"
    exit 1
fi

echo "========================================"
echo "安装完成！现在开始测试..."
echo "========================================"

echo "6. 运行Token验证测试..."
python main.py --test-token
echo

echo "7. 运行Graph API测试..."
python main.py --test-graph
echo

echo "8. 运行完整测试..."
python main.py --test-all

echo "========================================"
echo "测试完成！"
echo "========================================"
echo
echo "如需交互式测试，请运行: python main.py"
echo "如需退出虚拟环境，请运行: deactivate"
echo
