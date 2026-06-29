#!/bin/bash
# PWA 功能验证脚本

echo "=== PWA 功能验证 ==="

# 检查 manifest.json 文件
if [ -f "frontend/public/manifest.json" ]; then
    echo "✓ manifest.json 存在"
    # 检查关键字段
    if grep -q '"name": "平法助手"' "frontend/public/manifest.json"; then
        echo "✓ manifest.name 正确"
    else
        echo "✗ manifest.name 错误"
    fi

    if grep -q '"display": "standalone"' "frontend/public/manifest.json"; then
        echo "✓ manifest.display 正确"
    else
        echo "✗ manifest.display 错误"
    fi
else
    echo "✗ manifest.json 不存在"
fi

# 检查图标文件
ICON_DIR="frontend/public/icons"
if [ -d "$ICON_DIR" ]; then
    ICON_COUNT=$(ls "$ICON_DIR" | wc -l)
    echo "✓ 图标文件夹存在，包含 $ICON_COUNT 个图标"

    # 检查关键图标
    if [ -f "$ICON_DIR/icon-192x192.png" ] && [ -f "$ICON_DIR/icon-512x512.png" ]; then
        echo "✓ 关键图标存在"
    else
        echo "⚠ 关键图标缺失"
    fi
else
    echo "✗ 图标文件夹不存在"
fi

# 检查 PWA 插件配置
if [ -f "frontend/vite.config.ts" ]; then
    if grep -q "vite-plugin-pwa" "frontend/vite.config.ts"; then
        echo "✓ PWA 插件已配置"
    else
        echo "✗ PWA 插件未配置"
    fi
else
    echo "✗ vite.config.ts 不存在"
fi

echo "=== PWA 验证完成 ==="