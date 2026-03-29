#!/bin/bash
# OpenClaw 配置迁移脚本 (macOS/Linux)
# 用法: ./install.sh [-b|--backup]

set -e

BACKUP=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -b|--backup) BACKUP=true ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
    shift
done

# 检测目标路径
if [[ "$OSTYPE" == "darwin"* ]]; then
    TARGET_BASE="$HOME/.openclaw/workspace"
else
    TARGET_BASE="$HOME/.openclaw/workspace"
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FILES_DIR="$SCRIPT_DIR/files"

echo -e "\033[36m目标路径: $TARGET_BASE\033[0m"

# 创建目录
mkdir -p "$TARGET_BASE"
mkdir -p "$TARGET_BASE/rules"
mkdir -p "$TARGET_BASE/memory"

# 备份现有文件
if [ "$BACKUP" = true ]; then
    BACKUP_DIR="$SCRIPT_DIR/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    find "$FILES_DIR" -type f | while read -r file; do
        relative_path="${file#$FILES_DIR/}"
        target_file="$TARGET_BASE/$relative_path"
        
        if [ -f "$target_file" ]; then
            backup_file="$BACKUP_DIR/$relative_path"
            mkdir -p "$(dirname "$backup_file")"
            cp "$target_file" "$backup_file"
            echo -e "\033[33m备份: $relative_path\033[0m"
        fi
    done
    
    echo -e "\033[33m备份目录: $BACKUP_DIR\033[0m"
fi

# 复制文件
copied=0
find "$FILES_DIR" -type f | while read -r file; do
    relative_path="${file#$FILES_DIR/}"
    target_file="$TARGET_BASE/$relative_path"
    
    cp "$file" "$target_file"
    echo -e "\033[32m安装: $relative_path\033[0m"
    ((copied++)) || true
done

echo -e "\033[36m完成! 重启 OpenClaw 后生效\033[0m"
