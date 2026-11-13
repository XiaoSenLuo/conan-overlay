from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.0.0"


class PalsigslotConan(ConanFile):
    # conancenter 缺失 palsigslot (palacaze/sigslot), 目标名对齐 vcpkg 端口 (Pal::Sigslot)
    name = "palsigslot"
    description = "A header-only, thread safe implementation of signal-slots for C++"
    license = "MIT"
    homepage = "https://github.com/palacaze/sigslot"
    topics = ("signal", "slot", "header-only")
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
        self.cpp_info.set_property("cmake_file_name", "PalSigslot")
        self.cpp_info.set_property("cmake_target_name", "Pal::Sigslot")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
