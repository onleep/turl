import logging

formatter = f'%(asctime)s | %(levelname)s: %(message)s'
datefmt = f'%Y-%m-%d %H:%M:%S'
logging.basicConfig(format=formatter,
                    datefmt=datefmt,
                    level=logging.INFO,
                    filename='logging.log',
                    filemode='a')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(logging.Formatter(formatter, datefmt))
logging.getLogger().addHandler(console_handler)
