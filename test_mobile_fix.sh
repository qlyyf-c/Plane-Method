#!/bin/bash
# 手机端API访问测试脚本

echo "=========================================="
echo "手机端API访问修复验证"
echo "=========================================="
echo ""

# 1. 检查前端服务是否在运行
echo "1. 检查前端服务状态..."
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✅ 前端服务运行中 (http://localhost:5173)"
else
    echo "❌ 前端服务未启动"
    echo "   请先运行: cd frontend && npm run dev"
    exit 1
fi

# 2. 检查后端服务是否在运行
echo ""
echo "2. 检查后端服务状态..."
if curl -s http://localhost:8001/docs > /dev/null 2>&1; then
    echo "✅ 后端服务运行中 (http://localhost:8001)"
else
    echo "❌ 后端服务未启动"
    echo "   请先启动后端服务"
    exit 1
fi

# 3. 测试代理是否工作
echo ""
echo "3. 测试API代理..."
response=$(curl -s http://localhost:5173/api/v1/anchor/options)
if echo "$response" | grep -q "concrete_grades"; then
    echo "✅ API代理工作正常"
    echo "   测试数据: $(echo $response | jq -r '.concrete_grades | length') 个混凝土选项"
else
    echo "❌ API代理失败"
    echo "   响应: $response"
    exit 1
fi

# 4. 获取本机局域网IP
echo ""
echo "4. 获取局域网IP地址..."
if command -v hostname > /dev/null; then
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    echo "✅ 本机局域网IP: $LOCAL_IP"
else
    LOCAL_IP="<你的电脑IP>"
    echo "⚠️  请手动查看本机IP (ipconfig/ifconfig)"
fi

echo ""
echo "=========================================="
echo "验证步骤："
echo "=========================================="
echo ""
echo "1. 确保手机和电脑连接同一WiFi"
echo ""
echo "2. 在手机浏览器访问:"
echo "   http://$LOCAL_IP:5173"
echo ""
echo "3. 测试以下页面:"
echo "   - 锚固计算: 应该能加载选项数据"
echo "   - 解析页面: 应该能正常解析文本"
echo "   - 图集速查: 应该能加载分类列表"
echo ""
echo "4. 如果仍有问题，请检查:"
echo "   - 浏览器控制台错误信息"
echo "   - 网络请求状态 (F12 -> Network)"
echo ""
echo "=========================================="