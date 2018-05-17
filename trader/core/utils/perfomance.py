def execution_time(fn, *args):
    start = time.time()
    fn(args) if args else fn()
    end = time.time()
    t = end - start
    print('fn {} took {} s to run'.format(fn.__name__, t))
