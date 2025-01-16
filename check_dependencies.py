import importlib

# 需要检查的库
required_libraries = [
    ('kivy', '2.1.0'),
    ('librosa', '0.10.0'),
    ('pyaudio', '0.2.12'),
    ('numpy', '1.24.2')
]

def check_library(lib_name, required_version):
    try:
        module = importlib.import_module(lib_name)
        installed_version = getattr(module, '__version__', 'unknown')
        
        if installed_version == required_version:
            print(f"✅ {lib_name} {installed_version} (符合要求)")
        else:
            print(f"⚠️ {lib_name} {installed_version} (需要 {required_version})")
            
    except ImportError:
        print(f"❌ {lib_name} 未安装")

def main():
    print("正在检查依赖库...\n")
    for lib, version in required_libraries:
        check_library(lib, version)
    print("\n检查完成！")

if __name__ == '__main__':
    main()