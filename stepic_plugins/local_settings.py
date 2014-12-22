import os


COMPILERS = {
    'c++': {
        'bin': 'g++',
        'ext': 'cpp',
        'args': ['-pipe', '-O2', '-static', '-o', 'main']
    },
    'asm32': {
        'bin': 'gcc',
        'ext': 'S',
        'args': ['-pipe', '-m32', '-o', 'main']
    },
    'asm64': {
        'bin': 'gcc',
        'ext': 'S',
        'args': ['-pipe', '-m64', '-o', 'main']
    },
    'haskell': {
        'bin': 'ghc',
        'ext': 'hs',
        'args': ['-O', '-static', '-optl-static', '-optl-pthread', '-o', 'main']
    },
    'java': {
        'bin': os.path.join('{{ SANDBOX_JDK_HOME }}', 'bin/javac'),
        'ext': 'java',
        'args': []
    }
}
