"""
API 配置模块

跨平台数据文件夹配置
"""

import json
import platform
from pathlib import Path
from typing import List, Dict, Any, Optional


# 系统敏感目录黑名单（跨平台）
FORBIDDEN_DIRS = {
    "Windows": [
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\ProgramData",
        "C:\\$Recycle.Bin",
        "C:\\System Volume Information",
    ],
    "Darwin": [  # macOS
        "/System",
        "/Library",
        "/usr",
        "/bin",
        "/sbin",
        "/etc",
        "/var",
        "/boot",
        "/dev",
        "/proc",
    ],
    "Linux": [
        "/etc",
        "/usr",
        "/bin",
        "/sbin",
        "/var",
        "/boot",
        "/dev",
        "/proc",
        "/sys",
        "/root",
    ],
}


class Config:
    """配置管理"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，None 使用默认路径
        """
        self.config_path = config_path or Path(__file__).parent.parent.parent / "config.json"
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"警告：配置文件加载失败：{e}，使用默认配置")
                self.config = {}
        else:
            self.config = {}
    
    def get_allowed_roots(self) -> List[str]:
        """获取允许的根目录列表"""
        return self.config.get("data_folders", {}).get("allowed_roots", [])
    
    def get_forbidden_dirs(self) -> List[str]:
        """获取禁止的目录列表"""
        # 合并系统默认黑名单和配置黑名单
        system_forbidden = FORBIDDEN_DIRS.get(platform.system(), [])
        config_forbidden = self.config.get("data_folders", {}).get("forbidden_dirs", [])
        return system_forbidden + config_forbidden
    
    def get_default_path(self) -> str:
        """获取默认数据路径"""
        return self.config.get("data_folders", {}).get("default_path", "")


# 全局配置实例
config = Config()


def validate_folder_path(path: str) -> tuple[bool, str]:
    """
    验证文件夹路径（跨平台）
    
    Args:
        path: 要验证的路径
        
    Returns:
        (是否有效，错误消息)
    """
    try:
        # 转换为绝对路径
        full_path = Path(path).resolve()
        path_str = str(full_path)
        
        # 1. 必须是绝对路径
        if not full_path.is_absolute():
            return False, "路径必须是绝对路径"
        
        # 2. 检查路径遍历攻击
        if ".." in path:
            return False, "路径包含非法字符 '..'"
        
        # 3. 检查是否在禁止目录中
        forbidden = config.get_forbidden_dirs()
        for forbidden_dir in forbidden:
            # 跨平台路径比较（统一为正斜杠）
            if path_str.replace("\\", "/").startswith(forbidden_dir.replace("\\", "/")):
                return False, f"禁止访问系统目录：{forbidden_dir}"
        
        # 4. 检查路径是否存在
        if not full_path.exists():
            return False, "路径不存在"
        
        # 5. 检查是否是目录
        if not full_path.is_dir():
            return False, "路径不是目录"
        
        # 6. 检查是否有读取权限
        if not os.access(full_path, os.R_OK):
            return False, "没有读取权限"
        
        # 7. 检查是否包含 parquet 文件
        parquet_files = list(full_path.glob("*.parquet"))
        if len(parquet_files) == 0:
            return False, "目录中没有 parquet 文件"
        
        return True, f"验证通过，找到 {len(parquet_files)} 个 parquet 文件"
        
    except Exception as e:
        return False, f"验证失败：{str(e)}"


# 导入 os 模块
import os
