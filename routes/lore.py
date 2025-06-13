"""
Lore系统API路由
处理世界观、剧情介绍等内容的加载和展示
"""

from flask import Blueprint, jsonify, current_app
from pathlib import Path

bp = Blueprint("lore", __name__)

@bp.get("/api/lore")
def get_lore():
    """获取世界观介绍内容"""
    try:
        lore_path = Path(current_app.root_path) / "lore" / "intro.md"
        
        if not lore_path.exists():
            return jsonify({
                'success': False,
                'error': '世界观文件未找到'
            }), 404
            
        with open(lore_path, encoding="utf-8") as f:
            content = f.read()
            
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.get("/api/lore/<string:filename>")
def get_lore_file(filename):
    """获取指定的剧情文件"""
    try:
        # 安全检查，防止路径遍历
        if '..' in filename or '/' in filename:
            return jsonify({
                'success': False,
                'error': '无效的文件名'
            }), 400
            
        # 确保文件扩展名是.md
        if not filename.endswith('.md'):
            filename += '.md'
            
        lore_path = Path(current_app.root_path) / "lore" / filename
        
        if not lore_path.exists():
            return jsonify({
                'success': False,
                'error': f'剧情文件 {filename} 未找到'
            }), 404
            
        with open(lore_path, encoding="utf-8") as f:
            content = f.read()
            
        return jsonify({
            'success': True,
            'content': content,
            'filename': filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.get("/api/lore/list")
def list_lore_files():
    """列出所有可用的剧情文件"""
    try:
        lore_dir = Path(current_app.root_path) / "lore"
        
        if not lore_dir.exists():
            return jsonify({
                'success': True,
                'files': []
            })
            
        files = []
        for file_path in lore_dir.glob("*.md"):
            files.append({
                'filename': file_path.name,
                'title': file_path.stem.replace('_', ' ').title()
            })
            
        # 按文件名排序，确保intro.md在最前面
        files.sort(key=lambda x: (x['filename'] != 'intro.md', x['filename']))
        
        return jsonify({
            'success': True,
            'files': files
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500