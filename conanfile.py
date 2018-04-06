from conans import ConanFile, tools
import platform

class GammaConan(ConanFile):
    name = 'gamma'

    source_version = '0.9.8'
    package_version = '1'
    version = '%s-%s' % (source_version, package_version)

    build_requires = 'llvm/3.3-5@vuo/stable', \
               'vuoutils/1.0@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://mat.ucsb.edu/gamma/'
    license = 'http://mat.ucsb.edu/gamma/#license'
    description = 'A cross-platform library for doing generic synthesis and filtering of signals'
    source_dir = 'Gamma-%s' % source_version
    install_dir = '_install'
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
            tools.replace_in_file('Makefile.common', 'DYNAMIC		= 0', 'DYNAMIC = 1')

            self.run('mv COPYRIGHT %s.txt' % self.name)

    def build(self):
        import VuoUtils

        if platform.system() == 'Darwin':
            flags = '-Oz -mmacosx-version-min=10.10'
        elif platform.system() == 'Linux':
            flags = '-Oz'

        with tools.chdir(self.source_dir):
            env_vars = {
                'CC'     : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX'    : self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
                'CFLAGS' : flags,
                'CXXFLAGS' : flags + ' -stdlib=libc++ -I' + ' -I'.join(self.deps_cpp_info['llvm'].include_paths),
                'LDFLAGS': flags,
            }
            with tools.environment_append(env_vars):
                self.run('make install DESTDIR=../%s NO_AUDIO_IO=1' % self.install_dir)
        with tools.chdir(self.install_dir + '/lib'):
            if platform.system() == 'Darwin':
                self.run('mv libGamma.1.0.dylib libGamma.dylib')
            elif platform.system() == 'Linux':
                self.run('mv libGamma.1.0.so libGamma.so')
                self.run('chmod +x libGamma.so')

            VuoUtils.fixLibs(self.libs, self.deps_cpp_info)

    def package(self):
        if platform.system() == 'Darwin':
            libext = 'dylib'
        elif platform.system() == 'Linux':
            libext = 'so'

        self.copy('*.h',            src='%s/include' % self.install_dir, dst='include')
        self.copy('libGamma.%s' % libext, src='%s/lib'     % self.install_dir, dst='lib')

        self.copy('%s.txt' % self.name, src=self.source_dir, dst='license')

    def package_info(self):
        self.cpp_info.libs = ['Gamma']
