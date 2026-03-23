#!/usr/bin/env python3
"""
Cline 配置自动部署脚本
支持跨平台快速恢复配置
"""

import json
import os
import sys
import shutil
import platform
from pathlib import Path
from datetime import datetime

class ClineConfigManager:
    def __init__(self, config_dir="./cline-config"):
        self.config_dir = Path(config_dir)
        self.system = platform.system()
        self.home = Path.home()
        
        # 根据系统设置 Cline 配置目录
        if self.system == "Darwin":  # macOS
            self.cline_home = self.home / "Library/Application Support/Cline"
        elif self.system == "Windows":
            self.cline_home = self.home / "AppData/Local/Cline"
        else:  # Linux
            self.cline_home = self.home / ".cline"
    
    def backup_current_config(self):
        """备份当前配置"""
        if self.cline_home.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.cline_home / f"backup_{timestamp}"
            shutil.copytree(self.cline_home, backup_dir)
            print(f"✅ 配置已备份到: {backup_dir}")
            return backup_dir
        return None
    
    def deploy_config(self):
        """部署配置文件"""
        if not self.config_dir.exists():
            print(f"❌ 配置目录不存在: {self.config_dir}")
            return False
        
        # 创建 Cline 主目录
        self.cline_home.mkdir(parents=True, exist_ok=True)
        
        # 复制配置文件
        files_to_copy = [
            "settings.json",
            "mcp-servers.json",
            "custom-prompts.md",
            "keybindings.json"
        ]
        
        for file in files_to_copy:
            src = self.config_dir / file
            dst = self.cline_home / file
            
            if src.exists():
                shutil.copy2(src, dst)
                print(f"✅ 已复制: {file}")
            else:
                print(f"⚠️  文件不存在: {file}")
        
        return True
    
    def verify_config(self):
        """验证配置"""
        print("\n🔍 验证配置...")
        
        settings_file = self.cline_home / "settings.json"
        if not settings_file.exists():
            print("❌ settings.json 不存在")
            return False
        
        try:
            with open(settings_file) as f:
                config = json.load(f)
            
            # 检查必要字段
            required_fields = ["apiProvider", "model"]
            for field in required_fields:
                if field not in config:
                    print(f"❌ 缺少必要字段: {field}")
                    return False
            
            print("✅ 配置验证通过")
            print(f"   - API Provider: {config.get('apiProvider')}")
            print(f"   - Model: {config.get('model')}")
            return True
        
        except json.JSONDecodeError:
            print("❌ settings.json 格式错误")
            return False
    
    def export_config(self, output_file=None):
        """导出当前配置"""
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"cline-config-export-{timestamp}.json"
        
        config_data = {}
        
        # 收集所有配置文件
        for file in self.cline_home.glob("*.json"):
            try:
                with open(file) as f:
                    config_data[file.name] = json.load(f)
            except Exception as e:
                print(f"⚠️  无法读取 {file.name}: {e}")
        
        # 保存导出文件
        with open(output_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✅ 配置已导出到: {output_file}")
        return output_file
    
    def import_config(self, import_file):
        """导入配置"""
        try:
            with open(import_file) as f:
                config_data = json.load(f)
            
            self.cline_home.mkdir(parents=True, exist_ok=True)
            
            for filename, content in config_data.items():
                dst = self.cline_home / filename
                with open(dst, 'w') as f:
                    json.dump(content, f, indent=2)
                print(f"✅ 已导入: {filename}")
            
            return True
        except Exception as e:
            print(f"❌ 导入失败: {e}")
            return False
    
    def show_status(self):
        """显示配置状态"""
        print("\n📊 Cline 配置状态")
        print(f"系统: {self.system}")
        print(f"配置目录: {self.cline_home}")
        
        if self.cline_home.exists():
            files = list(self.cline_home.glob("*.json"))
            print(f"配置文件数: {len(files)}")
            for f in files:
                print(f"  - {f.name}")
        else:
            print("❌ 配置目录不存在")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Cline 配置管理工具")
    parser.add_argument("--config-dir", default="./cline-config", help="配置目录")
    parser.add_argument("--deploy", action="store_true", help="部署配置")
    parser.add_argument("--verify", action="store_true", help="验证配置")
    parser.add_argument("--backup", action="store_true", help="备份当前配置")
    parser.add_argument("--export", nargs="?", const="auto", help="导出配置")
    parser.add_argument("--import", dest="import_file", help="导入配置")
    parser.add_argument("--status", action="store_true", help="显示状态")
    
    args = parser.parse_args()
    
    manager = ClineConfigManager(args.config_dir)
    
    if args.backup:
        manager.backup_current_config()
    
    if args.deploy:
        manager.backup_current_config()
        manager.deploy_config()
        manager.verify_config()
    
    if args.verify:
        manager.verify_config()
    
    if args.export:
        output = None if args.export == "auto" else args.export
        manager.export_config(output)
    
    if args.import_file:
        manager.import_config(args.import_file)
    
    if args.status or not any([args.backup, args.deploy, args.verify, args.export, args.import_file]):
        manager.show_status()

if __name__ == "__main__":
    main()
