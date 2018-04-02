from conans import ConanFile, tools
import platform

class GammaConan(ConanFile):
    name = 'gamma'

    source_version = '0.9.5'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-2@vuo/stable', \
               'vuoutils/1.0@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://mat.ucsb.edu/gamma/'
    license = 'http://mat.ucsb.edu/gamma/#license'
    description = 'A cross-platform library for doing generic synthesis and filtering of signals'
    source_dir = 'gamma-%s' % source_version
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
        tools.mkdir(self.source_dir)
        with tools.chdir(self.source_dir):
            tools.get('http://mat.ucsb.edu/gamma/dl/gamma-%s.tar.gz' % self.source_version,
                      sha256='9cc24f30c4c418dd9697f12743db2887b35d29a738fe6acb21d82c8eeda6cc5a')

            tools.replace_in_file('Makefile.common', 'DYNAMIC		= 0', 'DYNAMIC = 1')

        self.run('mv %s/COPYRIGHT %s/%s.txt' % (self.source_dir, self.source_dir, self.name))

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
                'LDFLAGS': flags,
            }
            with tools.environment_append(env_vars):
                self.run('make install DESTDIR=../%s' % self.install_dir)
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
