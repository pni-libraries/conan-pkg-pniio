from conans import ConanFile, CMake, tools
import os


class PniioConan(ConanFile):
    name = "pniio"
    version = "1.X.X"
    license = "<Put the package license here>"
    url = "<Package recipe repository url here, for issues about the package>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_system_hdf5":[True,False],
               "with_system_boost":[True,False],
               "with_system_pnicore":[True,False]}
    default_options = "shared=False","with_system_boost=True","with_system_hdf5=True","with_system_pnicore=True"

    generators = "cmake"

    description = """
    Package is building the development version of the pniio library from the
    1.X.X branch.
    """

    boost_package = "Boost/1.62.0@lasote/stable"
    pnicore_package = "pnicore/1.1.0@wintersb/devel"
    hdf5_package = "hdf5/1.10.1@wintersb/stable"

    def configure(self):

        if not self.options.with_system_hdf5:
            self.requires(self.hdf5_package)

        if not self.options.with_system_boost:
            self.requires(self.boost_package)

        if not self.options.with_system_pnicore:
            self.requires(self.pnicore_package)

            if self.options.with_system_boost:
                self.options["pnicore"].with_system_boost=True


    def source(self):
        self.run("git clone https://github.com/pni-libraries/libpniio.git")
        self.run("cd libpniio && git submodule init && git submodule update --remote")
        # This small hack might be useful to guarantee proper /MT /MD linkage in MSVC
        # if the packaged project doesn't have variables to set it properly
        tools.replace_in_file("libpniio/CMakeLists.txt", "include(CTest)",
'''include(CTest)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')


    def build(self):
        cmake = CMake(self)

        cmake_defs = {}
        cmake_defs["CMAKE_INSTALL_PREFIX"]=self.package_folder
        cmake_defs["CMAKE_BUILD_TYPE"]=self.settings.build_type

        cmake.configure(source_dir="libpniio",
                        defs=cmake_defs)

        cmake.build()

        if self.settings.os == "Windows":
            cmake.build(target="RUN_TESTS")
        else:
            cmake.build(target="test")

        cmake.build(target="install")


    def package(self):
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["hello"]

    def imports(self):
        if self.settings.os=="Windows":
            self.copy("*.dll","bin","bin")
