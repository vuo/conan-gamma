from conans import ConanFile, tools

class GammaConan(ConanFile):
    name = 'gamma'

    source_version = '0.9.5'
    package_version = '2'
    version = '%s-%s' % (source_version, package_version)

    requires = 'llvm/3.3-1@vuo/stable'
    settings = 'os', 'compiler', 'build_type', 'arch'
    url = 'http://mat.ucsb.edu/gamma/'
    license = 'http://mat.ucsb.edu/gamma/#license'
    description = 'A cross-platform library for doing generic synthesis and filtering of signals'
    source_dir = 'gamma-%s' % source_version
    install_dir = '_install'

    def source(self):
        tools.mkdir(self.source_dir)
        with tools.chdir(self.source_dir):
            tools.get('http://mat.ucsb.edu/gamma/dl/gamma-%s.tar.gz' % self.source_version,
                      sha256='9cc24f30c4c418dd9697f12743db2887b35d29a738fe6acb21d82c8eeda6cc5a')

            tools.replace_in_file('Makefile.common', 'DYNAMIC		= 0', 'DYNAMIC = 1')

    def build(self):
        with tools.chdir(self.source_dir):
            env_vars = {
                'CC'     : self.deps_cpp_info['llvm'].rootpath + '/bin/clang',
                'CXX'    : self.deps_cpp_info['llvm'].rootpath + '/bin/clang++',
                'CFLAGS' : '-Oz -mmacosx-version-min=10.10',
                'LDFLAGS': '-Oz -mmacosx-version-min=10.10',
            }
            with tools.environment_append(env_vars):
                self.run('make install DESTDIR=../%s' % self.install_dir)
        with tools.chdir(self.install_dir):
            self.run('mv lib/libGamma.1.0.dylib lib/libGamma.dylib')
            self.run('install_name_tool -id @rpath/libGamma.dylib lib/libGamma.dylib')

    def package(self):
        self.copy('*.h',            src='%s/include' % self.install_dir, dst='include')
        self.copy('libGamma.dylib', src='%s/lib'     % self.install_dir, dst='lib')

    def package_info(self):
        self.cpp_info.libs = ['Gamma']
