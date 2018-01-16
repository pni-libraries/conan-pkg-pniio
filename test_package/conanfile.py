from conans import ConanFile, CMake
import os


channel = os.getenv("CONAN_CHANNEL", "devel")
username = os.getenv("CONAN_USERNAME", "wintersb")


class PnicoreTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "pniio/master@%s/%s" % (username, channel)
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        # Current dir is "test_package/build/<build_id>" and CMakeLists.txt is in "test_package"
        cmake.configure(source_dir=self.source_folder, build_dir=self.build_folder)
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy("*.so*", dst="lib", src="lib")

    def test(self):
        os.chdir("bin")
        self.run(".%sexample" % os.sep)
