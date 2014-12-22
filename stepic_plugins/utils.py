def get_limits_for_java(limits):
    java_limits = dict(limits)
    # for gc
    java_limits["CAN_FORK"] = True
    # setrlimit does not work because of MAP_NORESERVE, use -Xmx instead
    java_limits["MEMORY"] = None
    xmxk = limits["MEMORY"] // 1024
    return java_limits, ["-Xmx{}k".format(xmxk), "-Xss8m"]
