#!/bin/bash
# 执行所有修复的Shell脚本

echo "🚀 开始执行全面修复..."
echo "================================="

# 1. 首先运行Python修复脚本
echo "📝 运行主修复脚本..."
python fix_all_bugs.py

# 2. 运行原有的修复脚本
echo -e "\n📝 运行辅助修复脚本..."
python final_fixes.py

# 3. 修复文件权限
echo -e "\n🔧 修复文件权限..."
chmod +x start_xwe.sh
chmod +x test_fixes.sh
chmod +x quick_start_monitoring.sh
chmod +x setup_permissions.sh

# 4. 创建必要的目录
echo -e "\n📁 创建必要的目录..."
mkdir -p logs saves data/cache tests/benchmarks

# 5. 初始化游戏实例属性（修复app.py）
echo -e "\n🔧 修复app.py..."
cat >> app.py << 'EOF'

# 初始化游戏实例存储
app = create_app()
app.game_instances = {}
EOF

echo -e "\n✅ 所有修复完成！"
echo "================================="
echo ""
echo "下一步操作："
echo "1. 运行测试: pytest -v"
echo "2. 启动应用: python app.py"
echo "3. 检查健康状态: curl http://localhost:5001/health"
