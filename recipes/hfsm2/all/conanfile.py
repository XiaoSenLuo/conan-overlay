from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.0"


class Hfsm2Conan(ConanFile):
    # conancenter 仅有 hfsm2/2.5.2, 项目使用 2.12.x API
    # (hfsm2::MachineT / Config::ContextT / methodName / transitionName)
    name = "hfsm2"
    description = "Header-only hierarchical FSM framework in C++11, with fully statically-defined structure, no dynamic allocations"
    license = "MIT"
    homepage = "https://github.com/andrew-gresyk/HFSM2"
    topics = ("fsm", "state-machine", "header-only")
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

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
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "*", src=os.path.join(self.source_folder, "include"),
             dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "hfsm2")
        self.cpp_info.set_property("cmake_target_name", "hfsm2::hfsm2")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
