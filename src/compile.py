from pathlib import Path
from PyQt5 import uic
import sys
import os

def compile_qrc_file(qrc_name = 'qrc'):
    import subprocess
    """编译qrc文件为Python模块"""
    qrc_file = Path(__file__).parent /'..'/'qrc'/f'{qrc_name}.qrc'  # qrc文件路径
    py_file = Path(__file__).parent /'..'/'src'/f'{qrc_name}_rc.py'  # 输出的Python文件
    
    if qrc_file.exists():
        try:
            # 使用pyrcc5编译qrc文件
            result = subprocess.run([
                'pyrcc5', '-o', str(py_file), str(qrc_file)
            ], check=True, capture_output=True, text=True)
            print(f"QRC文件编译成功: {py_file}")
        except subprocess.CalledProcessError as e:
            print(f"编译QRC文件失败: {e}")
        except FileNotFoundError:
            print("pyrcc5未找到，请确保PyQt5正确安装")
    else:
        print(f"QRC文件不存在: {qrc_file}")

def compile_qrc_file_pyqt5(qrc_name = 'qrc'):
    from PyQt5.pyrcc_main import main as pyrcc_main
    """编译qrc文件为Python模块"""
    qrc_file = Path(__file__).parent /'..'/'qrc'/f'{qrc_name}.qrc'  # qrc文件路径
    py_file = Path(__file__).parent /'..'/'src'/f'{qrc_name}_rc.py'  # 输出的Python文件
    if qrc_file.exists():
        original_argv = sys.argv
        sys.argv = ['pyrcc5', '-o', str(py_file), str(qrc_file)]
        try:
            pyrcc_main()
            print("QRC编译成功")
        except Exception as e:
            print(f"编译失败: {e}")
        finally:
            sys.argv = original_argv

def compile_ui_file(ui_name = 'mainwindow'):
    """编译ui文件为Python模块"""
    # 确保导入路径正确
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

    # 使用pathlib加载UI文件
    ui_file = Path(__file__).parent / '..' / 'ui' /f'{ui_name}.ui'  # 修正了文件名
    # 解析为绝对路径（自动处理..等相对路径符号）
    ui_file = ui_file.resolve()

    if ui_file.exists():
        with open(f'./src/ui_py/ui_{ui_name}.py', 'w', encoding='utf-8') as f:
            uic.compileUi(str(ui_file), f)
    else:
        print(f"UI文件不存在: {ui_file}")
        # 如果UI文件不存在，直接使用已有的UI类