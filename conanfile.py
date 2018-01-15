from conans import ConanFile, CMake, tools
import os
import git

class PniioConan(ConanFile):
        """
    Building the pnicore library from a the current repository. 
    """
    #
    # set this to the appropriate library version and deactivate 
    # auto_update for stables releases
    #
    version = "master"
    auto_update = True
    
    #
    # this could be left unchanged for virtually all stable and developer
    # releases.
    #
    name = "pniio"
    version = "master"
    license = "GPL V2"
    url = "<Package recipe repository url here, for issues about the package>"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False],
               "with_system_hdf5":[True,False],
               "with_system_boost":[True,False],
               "with_system_pnicore":[True,False],
               "commit":"ANY"}
    default_options = "shared=False","with_system_boost=True","with_system_hdf5=True","with_system_pnicore=True"

    generators = "cmake"

    description = """
    Package is building the development version of the pniio library from the
    master branch.
    """

    boost_package   = "Boost/1.62.0@lasote/stable"
    hdf5_package    = "hdf5/1.10.1@eugenwintersberger/testing"
    pnicore_package = "pnicore/master@eugenwintersberger/devel"
    h5cpp_package   = "h5cpp/master@eugenwintersberger/devel"
    zlib_package    = "zlib/1.2.8@conan/stable"
    bzip2_package   = "bzip2/1.0.6@conan/stable"
    
    pniio_git_url = "https://github.com/pni-libraries/libpniio.git"

    
    def _get_local_current_commit(self,repository_path):
        self.output.info("Trying to access repository in: "+repository_path)
        commit = None
        try:
            self.run("cd %s && git pull" %repository_path) 
            repo = git.Repo(repository_path)
            commit = repo.commit().hexsha
            self.output.info("Current commit is: "+commit)
            
        except:
            self.output.info("Could not retrieve current commit of sources")
            
        return commit
    
    def _get_remote_current_commit(self):
        self.output.info("Trying to get latest commit from remote repository")
        gcmd = git.cmd.Git()
        commit = None
        
        try:
            commit = gcmd.ls_remote(self.pnicore_git_url,"refs/heads/master").split("\t")[0]
            self.output.info("The current remote master is on: %s" %commit)
        except:
            self.output.info("Failure to determine the current commit from remote")
            
        return commit
    
    def _get_current_commit(self):
        #we pull here the repository and add the commit to the build options. 
        #if the commit has changed the hash of the build configuration will change
        #and thus force a rebuild of the package
        
        
        current_commit = None
        self.output.info("Checking the GIT commit")       
        source_path =  os.path.join(self.conanfile_directory,"..","source","libpniio")
        
        if os.path.exists(source_path):
            current_commit = self._get_local_current_commit(source_path)
        else:
            current_commit = self._get_remote_current_commit()
            
        return current_commit
    
    def _set_commit_option(self):
        current_commit = self._get_current_commit()
        if current_commit != None:
            #if we can obtain the actual commit of the repository we can do something with it
            self.options.commit = current_commit

    def configure(self):

        if not self.options.with_system_hdf5:
            self.requires(self.hdf5_package)

        if not self.options.with_system_boost:
            self.requires(self.boost_package)

        if not self.options.with_system_pnicore:
            self.requires(self.pnicore_package)

            if self.options.with_system_boost:
                self.options["pnicore"].with_system_boost=True
                
        if self.auto_update: self._set_commit_option()


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
        self.cpp_info.libs = ["pniio"]

    def imports(self):
        if self.settings.os=="Windows":
            self.copy("*.dll","bin","bin")
