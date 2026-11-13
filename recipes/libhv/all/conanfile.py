from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rm
import os

required_conan_version = ">=2.0.0"


class LibhvConan(ConanFile):
    # conancenter 缺失 libhv; 目标名对齐 vcpkg 端口 (hv_static)
    name = "libhv"
    description = "Libhv is a C/C++ network library similar to libevent/libuv"
    license = "BSD-3-Clause"
    homepage = "https://github.com/ithewei/libhv"
    topics = ("network", "event-loop", "http")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_http": [True, False],
        "with_evpp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_http": True,
        "with_evpp": True,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_EXAMPLES"] = False
        tc.variables["BUILD_UNITTEST"] = False
        tc.variables["WITH_PROTOCOL"] = False
        tc.variables["WITH_MQTT"] = False
        tc.variables["WITH_KCP"] = False
        tc.variables["WITH_OPENSSL"] = False
        tc.variables["WITH_CURL"] = False
        tc.variables["WITH_NGHTTP2"] = False
        tc.variables["WITH_EVPP"] = self.options.with_evpp
        tc.variables["WITH_HTTP"] = self.options.with_http
        tc.variables["BUILD_SHARED"] = self.options.shared
        tc.variables["BUILD_STATIC"] = not self.options.shared
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "libhv")
        self.cpp_info.components["hv_static"].set_property("cmake_target_name", "hv_static")
        self.cpp_info.components["hv_static"].libs = ["hv_static"]
        self.cpp_info.components["hv_static"].system_libs = ["pthread"]
        if self.settings.os == "Linux":
            self.cpp_info.components["hv_static"].system_libs.append("dl")
