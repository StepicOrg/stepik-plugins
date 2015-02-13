--haskell
main = readFile "{{ SECRET_FILE }}" >>= putStr
