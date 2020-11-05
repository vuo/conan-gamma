from conans import ConanFile, tools
import platform
import shutil

class GammaConan(ConanFile):
    name = 'gamma'

    source_version = '0.9.8'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    build_requires = (
        'llvm/5.0.2-1@vuo/stable',
        'macos-sdk/11.0-0@vuo/stable',
        'vuoutils/1.2@vuo/stable',
    )
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://mat.ucsb.edu/gamma/'
    license = 'http://mat.ucsb.edu/gamma/#license'
    description = 'A cross-platform library for doing generic synthesis and filtering of signals'
    source_dir = 'Gamma-%s' % source_version

    build_x86_dir = '_build_x86'
    build_arm_dir = '_build_arm'
    install_x86_dir = '_install_x86'
    install_arm_dir = '_install_arm'
    install_universal_dir = '_install_universal_dir'

    exports_sources = '*.patch'

    libs = {
        'Gamma': 1,
    }

    def requirements(self):
        if platform.system() == 'Linux':
            self.requires('patchelf/0.10pre-1@vuo/stable')
        elif platform.system() != 'Darwin':
            raise Exception('Unknown platform "%s"' % platform.system())

    def source(self):
        tools.get('https://github.com/LancePutnam/Gamma/archive/%s.tar.gz' % self.source_version,
                  sha256='2ecc7ef250659e58ad80859bb18b8939a8657e4cfaedd12cc1dc20183556950b')

        with tools.chdir(self.source_dir):
            tools.patch(patch_file='../sndfile.patch')
            tools.replace_in_file('Makefile.common', 'OSX_SDK := $(lastword $(shell ls $(OSX_SDK_PATH)))', '')
            self.run('mv COPYRIGHT %s.txt' % self.name)

    def build(self):
        import VuoUtils

        c_flags = '-Oz -I.'
        if platform.system() == 'Darwin':
            c_flags += ' -isysroot %s' % self.deps_cpp_info['macos-sdk'].rootpath
            c_flags += ' -mmacosx-version-min=10.11'

        cxx_flags = c_flags + ' -stdlib=libc++ -I' + ' -I'.join(self.deps_cpp_info['llvm'].include_paths)
        ld_flags = c_flags

        env_vars = {
            'CC'      : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
            'CXX'     : self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
        }
        make_args = 'install -j9 DYNAMIC=1 NO_AUDIO_IO=1 NO_SOUNDFILE=1'

        self.output.info("=== Build for x86_64 ===")
        self.run('cp -a %s %s' % (self.source_dir, self.build_x86_dir))
        with tools.chdir(self.build_x86_dir):
            with tools.environment_append(env_vars):
                self.run('make %s DESTDIR=../%s CFLAGS="%s" CXXFLAGS="%s" LDFLAGS="%s"' % (make_args, self.install_x86_dir, c_flags, cxx_flags, ld_flags))
        with tools.chdir('%s/lib' % self.install_x86_dir):
            shutil.move('libGamma.1.0.dylib', 'libGamma.dylib')
            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

        self.output.info("=== Build for arm64 ===")
        self.run('cp -a %s %s' % (self.source_dir, self.build_arm_dir))
        with tools.chdir(self.build_arm_dir):
            arm_flags = ' -target arm64-apple-macos10.11.0'
            with tools.environment_append(env_vars):
                self.run('make %s DESTDIR=../%s CFLAGS="%s %s" CXXFLAGS="%s %s" LDFLAGS="%s %s"' % (make_args, self.install_arm_dir, c_flags, arm_flags, cxx_flags, arm_flags, ld_flags, arm_flags))
        with tools.chdir('%s/lib' % self.install_arm_dir):
            shutil.move('libGamma.1.0.dylib', 'libGamma.dylib')
            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        tools.mkdir(self.install_universal_dir)
        with tools.chdir(self.install_universal_dir):
            self.run('lipo -create ../%s/lib/libGamma.%s ../%s/lib/libGamma.%s -output libGamma.dylib' % (self.install_x86_dir, libext, self.install_arm_dir, libext))

        self.copy('*.h', src='%s/include' % self.install_x86_dir, dst='include')
        self.copy('libGamma.%s' % libext, src=self.install_universal_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['Gamma']
