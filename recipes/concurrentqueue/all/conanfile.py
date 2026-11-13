from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.0"


class ConcurrentqueueConan(ConanFile):
    name = "concurrentqueue"
    description = "A fast multi-producer, multi-consumer lock-free concurrent queue for C++11"
    license = ["BSD-2-Clause", "BSL-1.0"]
    homepage = "https://github.com/cameron314/concurrentqueue"
    topics = ("queue", "lock-free", "concurrency", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    # 与 CCI 配方的差异: 项目同时使用 "concurrentqueue/moodycamel/..." (vcpkg 端口布局)
    # 与 "moodycamel/..." 两种包含前缀, 因此同时安装两份头文件
    _headers = ["concurrentqueue.h", "blockingconcurrentqueue.h", "lightweightsemaphore.h"]

    @property
    def _min_cppstd(self):
        return 11

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            check_min_cppstd(self, self._min_cppstd)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        pass

    def package(self):
        copy(self, "LICENSE.md", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        for header in self._headers:
            copy(self, header, src=self.source_folder,
                 dst=os.path.join(self.package_folder, "include", "moodycamel"))
            copy(self, header, src=self.source_folder,
                 dst=os.path.join(self.package_folder, "include", "concurrentqueue", "moodycamel"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "concurrentqueue")
        self.cpp_info.set_property("cmake_target_name", "concurrentqueue::concurrentqueue")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.system_libs = ["pthread"]
