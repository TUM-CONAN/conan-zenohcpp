#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout, CMakeDeps
from conan.tools.scm import Git
from conan.tools.files import load, update_conandata, copy, replace_in_file, get, collect_libs
import os


class ZenohCppConan(ConanFile):

    name = "zenoh-cpp"
    _version = "0.10.0-rc"
    revision = ""
    version = _version+revision

    license = "Apache-2.0"
    homepage = "https://github.com/eclipse-zenoh/zenoh-cpp"
    url = "https://github.com/TUM-CONAN/conan-zenoh-cpp"
    description = "Zenoh networking library - cpp-wrapper"
    topics = ("Pattern", "Architecture", "Networking")

    settings = "os", "compiler", "build_type", "arch"
    options = {
         "shared": [True, False],
         "fPIC": [True, False]
    }
    default_options = {
        "shared": False,
        "fPIC": True
    }

    def export(self):
        update_conandata(self, {"sources": {
            "commit": "{}".format(self._version),
            "url": "https://github.com/eclipse-zenoh/zenoh-cpp.git"
            }}
            )

    def source(self):
        git = Git(self)
        sources = self.conan_data["sources"]
        git.clone(url=sources["url"], target=self.source_folder)
        git.checkout(commit=sources["commit"])

    def requirements(self):
        self.requires("zenoh-c/{}@camposs/stable".format(self._version), transitive_libs=True, transitive_headers=True)

    def generate(self):
        tc = CMakeToolchain(self)

        def add_cmake_option(option, value):
            var_name = "{}".format(option).upper()
            value_str = "{}".format(value)
            var_value = "ON" if value_str == 'True' else "OFF" if value_str == 'False' else value_str
            tc.variables[var_name] = var_value

        for option, value in self.options.items():
            add_cmake_option(option, value)

        tc.cache_variables["CPP_STANDARD"] = str(self.settings.compiler.cppstd)

        tc.generate()

        deps = CMakeDeps(self)
        deps.generate()

    def layout(self):
        cmake_layout(self, src_folder="source_folder")

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder=os.path.join(self.source_folder, "install"))
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = collect_libs(self)
