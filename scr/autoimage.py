# -*- coding: utf-8 -*- 
import os 
import hashlib
import argparse
import re 
import time 

import dropbox  


def set_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--root_path', type=str, default=None,
                        help="The path to the folder.")
    parser.add_argument('--dropbox_access_token', type=str, default=None,
                        help='https://www.dropbox.com/developers/documentation/python#tutorial')
    parser.add_argument('--interval_time', type=int, default=1, 
                        help='The interval time for monitoring folder.')
    args = parser.parse_args()
    
    return args 


def folder_moniter(**file_md5):
    modified_files = []
    for file_path, md5_before in file_md5.items():
        md5_now = hashlib.md5(open(file_path).read().encode('utf-8')).hexdigest()
        if md5_now != md5_before:
            file_md5[file_path] = md5_now
            modified_files.append(file_path)
    
    return modified_files, file_md5 
    
    
def obtain_dropbox_pdf_url(dbx, file_path):
    dbx_pdf_path = dbx.sharing_create_shared_link(file_path).url
    
    return dbx_pdf_path 
    
def multiple_replace(pattern, line, **dt):
    def replace_(matched):
        return dt[matched.group(0)]
    
    tt = pattern.sub(replace_, line)
    
    return tt


if __name__ == "__main__":
    args = set_args()
    root_path = args.root_path 
    interval_time = args.interval_time
    dropbox_access_token = args.dropbox_access_token
    
    # 获得dropbox数据库权限 init 
    dbx = dropbox.Dropbox(dropbox_access_token)
    # init
    file_md5 = {os.path.join(root_path, tmp): ' ' for tmp in os.listdir(root_path)}
    
    # moniter 
    while True:
        modified_files, file_md5 = folder_moniter(**file_md5)

        pattern = re.compile(r"\(.*?.png\)")
        for file in modified_files: 
            with open(file, 'r') as f:
                content = f.read()
                m = pattern.findall(content)
                if m:
                    data_dict = dict()
                    for img in m:
                        img_path = img.split(')')[0].split('(')[-1]
                            
                        # 上传本地pdf到dropbox database /img文件夹
                        with open(img_path, 'rb') as f:
                            dbx.files_upload(f.read(), '/img/'+os.path.split(img_path)[-1], mode=dropbox.files.WriteMode.overwrite)
                        
                        # 获得Dropbox里面img链接
                        pdf_url_in_dropbox = obtain_dropbox_pdf_url(dbx, '/img/'+os.path.split(img_path)[-1]).replace('www', 'dl')
                    
                        # 要修改的item文件
                        data_dict[img] = "(" + pdf_url_in_dropbox + ')'
            
                    new_content = multiple_replace(pattern, content, **data_dict)
                    # 修改md文件
                    with open(file, "w") as f:
                        f.write(''.join(new_content))
                
        time.sleep((interval_time))