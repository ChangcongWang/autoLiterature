# -*- coding: utf-8 -*- 
import os 
import argparse 

from concurrent.futures import ThreadPoolExecutor as Executor 

FILE_PATH = os.path.abspath(os.path.dirname(__file__))

def set_args():
    parser = argparse.ArgumentParser(description='autoLiterature')
    parser.add_argument('-p', '--root_path', type=str, default='D:\Paper\papernote',
                        help="The path to the folder.")
    parser.add_argument('-t', '--interval_time', type=int, default=1, 
                        help='The interval time for monitoring folder.')
    args = parser.parse_args()
    
    return args 

def autoliter(root_path, interval_time):
    os.system("python {}/scr/autoliterature.py -p {} -t {}".format(FILE_PATH,
                                                                         root_path,
                                                                         interval_time))


def main():
    args = set_args()
    root_path = args.root_path
    interval_time = args.interval_time
    
    with Executor(max_workers=1) as executor: 
        task1 = executor.submit(autoliter, root_path, interval_time)

if __name__ == "__main__":
    main()