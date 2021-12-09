# -*- coding: utf-8 -*- 
import os 
import argparse
import re 
import time 

from modules import folderMoniter, patternRecognizer, metaExtracter
from modules import urlDownload, note_modified


def set_args():
    parser = argparse.ArgumentParser(description="AutoLiterature")
    parser.add_argument('-p', '--root_path', type=str, default=None,
                        help="The path to the folder.")
    parser.add_argument('-t', '--interval_time', type=int, default=1, 
                        help='The interval time for monitoring folder.')
    args = parser.parse_args()
    
    return args 


def main():
    args = set_args()
    root_path = args.root_path 
    interval_time = args.interval_time

    # init 
    folder_moniter = folderMoniter(root_path)
    pattern_recog = patternRecognizer(r'- \[.*\]')  # 检测 - [DOI], 或者- [arxivId]
    meta_extracter = metaExtracter()
    url_download = urlDownload()

    while True:
        modified_items = folder_moniter.file_md5_update()
        for md_file, md_md5 in modified_items.items():
            with open(md_file, 'r',encoding = "utf-8") as f:
                content = f.read()
            
            m = pattern_recog.findall(content)
            if m:
                replace_dict = dict()

                for literature in m:
                    literature_id = literature.split('[')[-1].split(']')[0]
                    
                    # Fetch data
                    try:
                        bib_dict = meta_extracter.id2bib(literature_id)
                        print(bib_dict)
                        if "pdf_link" in bib_dict.keys():
                            pdf_dict = url_download.fetch(bib_dict["pdf_link"])
                            if not pdf_dict:
                                pdf_dict = url_download.fetch(literature_id)
                        else:
                            pdf_dict = url_download.fetch(literature_id)

                        # Upload attachment and generate shared link
                        if "\n" in bib_dict["title"]:
                            bib_dict["title"] = re.sub(r' *\n *', ' ', bib_dict["title"])
                            
                        pdf_name = bib_dict['year'] + '_' + bib_dict['title'] + '.pdf'
                        pdf_name=pdf_name.replace(" ","_").replace(":","").replace("/","").replace("\"","").replace("<","").replace(">","").replace("|","").replace("*","").replace("?","")
                        pdf_loc = os.path.join(os.path.dirname(root_path),"pdf",pdf_name)
                        pdf_loc=pdf_loc.replace("\\","/")
                        if pdf_dict:
                            with open(pdf_loc, 'wb') as pdf:
                                pdf.write(pdf_dict['pdf'])

                        pdf_shared_link = "../pdf/"+pdf_name

                        if 'cited_count' in bib_dict.keys():
                            replaced_literature = "|**{}**| {} et.al| {}| {}| ([pdf]({}))([link]({}))|{}||||".format(
                                bib_dict['title'], bib_dict["author"].split(" and ")[0], bib_dict['journal'], 
                                bib_dict['year'], pdf_shared_link, bib_dict['url'], bib_dict["cited_count"]
                                )
                        else:
                            replaced_literature = "|**{}**| {} et.al| {}| {}| ([pdf]({}))([link]({}))| ||||".format(
                                bib_dict['title'], bib_dict["author"].split(" and ")[0], bib_dict['journal'], 
                                bib_dict['year'], pdf_shared_link, bib_dict['url']
                                )

                        replace_dict[literature] = replaced_literature
                    except:
                        print("ex")
                        # replace_dict[literature] = literature

                # Modified note
                if replace_dict:
                    note_modified(pattern_recog, md_file, **replace_dict)

        time.sleep((interval_time))

if __name__ == "__main__":
    main()
