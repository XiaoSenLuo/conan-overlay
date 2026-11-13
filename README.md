# conan-overlay

工作项目使用的 Conan 2 overlay 仓库，包含两部分内容：

1. **扩展 CCI (Conan Center Index) 的软件配方** —— 补充 conancenter 缺失的包、版本落后的包，以及与 vcpkg 端口布局/目标名对齐而需要差异化的包；
2. **常用构建 profile** —— 覆盖工作项目的原生构建 (Windows MSVC / MinGW、Linux GCC) 与交叉编译 (Yocto SDK → ZYNQ armv7) 场景。

所有配方均为 Conan 2 风格 (`required_conan_version >= 2.0.0`)，不依赖任何自定义 remote，源码直接取自上游发布 tarball (conandata.yml 中固定 sha256)。

## 目录结构

```
conan-overlay/
├── profiles/              # 常用构建 profile
│   ├── profile-Linux-armv7hf-gcc-13-23.txt
│   ├── profile-Linux-x86_64-gcc-11-gnu17.txt
│   ├── profile-Windows-x86_64-gcc-14-gnu17.txt
│   └── profile-Windows-x86_64-msvc-194-14.txt
└── recipes/               # CCI 扩展配方 (布局遵循 CCI: config.yml + <folder>/conanfile.py)
    ├── concurrentqueue/
    ├── hfsm2/
    ├── libhv/
    └── palsigslot/
```

## 配方 (recipes)

| 包名 | 版本 | 类型 | 与 CCI 的关系 |
|------|------|------|---------------|
| [concurrentqueue](https://github.com/cameron314/concurrentqueue) | 1.0.5 | header-only | 差异化: 同时安装 `moodycamel/...` 与 `concurrentqueue/moodycamel/...` 两种包含前缀 (兼容 vcpkg 端口布局) |
| [hfsm2](https://github.com/andrew-gresyk/HFSM2) | 2.12.1 | header-only | 版本扩充: conancenter 仅有 2.5.2，项目使用 2.12.x API (`hfsm2::MachineT` / `Config::ContextT` / `methodName` / `transitionName`) |
| [libhv](https://github.com/ithewei/libhv) | 1.3.4 | library (静态/动态) | 缺失补充: conancenter 无 libhv；CMake 目标名对齐 vcpkg 端口 (`hv_static`) |
| [palsigslot](https://github.com/palacaze/sigslot) | 1.2.3 | header-only | 缺失补充: conancenter 无 palsigslot；CMake 目标名对齐 vcpkg 端口 (`Pal::Sigslot`) |

各配方导出的 CMake 目标名：

| 包名 | CMake 文件名 | CMake 目标名 |
|------|--------------|--------------|
| concurrentqueue | `concurrentqueue` | `concurrentqueue::concurrentqueue` |
| hfsm2 | `hfsm2` | `hfsm2::hfsm2` |
| libhv | `libhv` | `hv_static` |
| palsigslot | `PalSigslot` | `Pal::Sigslot` |

libhv 提供选项: `shared` (默认 False)、`fPIC`、`with_http` (默认 True)、`with_evpp` (默认 True)；其余子功能 (openssl/curl/mqtt/kcp/nghttp2 等) 均已关闭。

## Profiles

### 命名规则

文件名编码了 profile 的 settings，profile 内部用 Jinja2 从文件名解析 (对应官方文档
"Getting settings from a filename" 的推荐用法)：

```
profile-<os>-<arch>-<compiler>-<compiler.version>-<cppstd>.txt
```

### 一览

| profile | 用途 | 传入方式 |
|---------|------|----------|
| `profile-Linux-armv7hf-gcc-13-23.txt` | **host**: Yocto SDK 交叉编译 armv7hf 目标机 (ZYNQ, cortex-a9, thumb, neon, hard-float)，C++23 | `-pr:h` |
| `profile-Linux-x86_64-gcc-11-gnu17.txt` | **build**: x86_64 Linux 构建机 (Ubuntu 22.04, 系统 GCC 11.4)，gnu++17 | `-pr:b` |
| `profile-Windows-x86_64-gcc-14-gnu17.txt` | Windows 原生构建，MinGW-w64 GCC 14 (winlibs UCRT)，gnu++17 | `-pr:h` + `-pr:b` (同一个) |
| `profile-Windows-x86_64-msvc-194-14.txt` | Windows 原生构建，MSVC 194 (VS2022)，C++14，动态 CRT | `-pr:h` + `-pr:b` (同一个) |

### 说明

- **交叉编译** (`profile-Linux-armv7hf-gcc-13-23.txt`):
  - 使用前必须先 source Yocto SDK 环境脚本 —— 它提供 PATH 中的交叉工具链
    (`arm-amd-linux-gnueabi-gcc` 等)，以及 profile 推导 sysroot 与 binutils 所需的
    `SDKTARGETSYSROOT` / `OECORE_NATIVE_SYSROOT` 环境变量；
  - profile 显式声明 `tools.build:sysroot`、体系结构/ABI 标志
    (`-mthumb -mfpu=neon -mfloat-abi=hard -mcpu=cortex-a9`)、链接加固选项
    (`-Wl,-z,relro -z now` 等)，并将 `CMAKE_AR`/`CMAKE_RANLIB` 等显式指向 SDK 原生
    工具链，避免 CMake 在目标 sysroot 中解析到 ARM 架构的 binutils 导致
    "Exec format error"；这些 conf 经 `conan_toolchain.cmake` 同样作用于所有依赖包自身的构建。
- **原生构建** (Windows 两个 profile): 同一 profile 需分别以 `-pr:h` 和 `-pr:b` 传入；
  仅传 `-pr` 时 build profile 会回退到默认 profile，工具链风格可能错配 (例如 MSVC host
  配到 GNU 风格的构建工具)。

## 使用方式

其他项目按以下三步接入：

**1. 克隆到项目根目录** (推荐作为 submodule，便于随项目固定版本):

```bash
git submodule add <本仓库地址> conan-overlay
# 或者直接: git clone <本仓库地址> conan-overlay
```

**2. 导出使用的配方** (导入本地 Conan 缓存，只需按需导出用到的包):

```bash
conan export conan-overlay/recipes/hfsm2/all
conan export conan-overlay/recipes/libhv/all
# ...其余同理
```

Windows PowerShell 下批量导出全部配方:

```powershell
Get-ChildItem conan-overlay/recipes -Directory | ForEach-Object { conan export "$($_.FullName)/all" }
```

bash 下:

```bash
for r in conan-overlay/recipes/*/all; do conan export "$r"; done
```

**3. 指定 profile 安装**:

原生构建 (Windows MSVC 为例，host/build 传同一 profile):

```bash
conan install . -pr:h conan-overlay/profiles/profile-Windows-x86_64-msvc-194-14.txt \
                -pr:b conan-overlay/profiles/profile-Windows-x86_64-msvc-194-14.txt \
                --build=missing
```

交叉编译 (先 source Yocto SDK 环境脚本，host 为 armv7 目标机，build 为 x86_64 构建机):

```bash
. /opt/sdk/environment-setup-arm-amd-linux-gnueabi   # 以实际 SDK 环境脚本路径为准
conan install . -pr:h conan-overlay/profiles/profile-Linux-armv7hf-gcc-13-23.txt \
                -pr:b conan-overlay/profiles/profile-Linux-x86_64-gcc-11-gnu17.txt \
                --build=missing
```

依赖解析时 conancenter 与本仓库导出的配方会合并 (本地缓存优先)，`CMakeDeps`/`CMakeToolchain`
生成的配置中可直接使用上文列出的 CMake 目标名。

## 新增内容约定

- **配方**: 目录布局遵循 CCI —— `<name>/config.yml` 声明版本 → folder 映射，源码地址与
  sha256 记录在 `<name>/<folder>/conandata.yml`；与 CCI 已有配方的差异点在 conanfile.py
  顶部注释说明。
- **profile**: 按 `profile-<os>-<arch>-<compiler>-<compiler.version>-<cppstd>.txt` 命名，
  settings 由文件名解析，新增工具链/标志时参考现有 profile 的注释组织 `[buildenv]`/`[runenv]`/`[conf]`。

## License

[MIT](LICENSE)
