import requests
import re
import time

import wiki_lib as wb


def uma_music_update(Session: requests.Session):
    '更新赛马娘音乐列表'

    title = "User:SinonJZH/Sandbox"  # 赛马娘 Pretty Derby/译名对照表
    table_section = "歌曲"

    count_finfish = 0
    count_translate = 0
    count_create = 0

    wb.login(Session)

    section_id = wb.get_section_id(Session, title, table_section)
    content = wb.get_wikitext(Session, title, section_id)

    pattern = re.compile(
        r'\|\s*(\[\[(.*?)(?:\|.*)?\]\])\s*\|\|\s*(.*?)\s*\|\|')
    result = pattern.finditer(content)

    pattern = re.compile(
        r'\{\{LyricsKai[\s\S]*\|translated=\s*([\s\S]*?)\s*\}\}')
    for val in result:
        rep = val.group(0)
        rep_link = val.group(1)
        link = val.group(2)
        status = val.group(3)

        if status == "{{支持|已收录}}":
            print(link + " 为已收录，跳过检查。")
            count_finfish += 1
            continue
        elif status == "":
            if wb.check_page_exist(Session, link) == -1:
                print(link + " 未被创建")
                count_create += 1
                time.sleep(1)
                continue

        lyc_id = wb.get_section_id(Session, link, "歌词")

        if lyc_id == -1:
            lyc = ""
        else:
            lyc = wb.get_wikitext(Session, link, lyc_id)

            lyc = pattern.search(lyc)
            if lyc:
                lyc = lyc.group(1)
            else:
                lyc = ""

        if len(lyc) >= 20:
            print("已检查 " + link + " 翻译已完成。")
            count_finfish += 1
            content = str.replace(content, rep, '| ' +
                                  rep_link + ' || {{支持|已收录}} ||', 1)
        else:
            count_translate += 1
            print("已检查 " + link + " 翻译未完成")
            content = str.replace(content, rep, '| ' +
                                  rep_link + ' || {{疑问|无翻译}} ||', 1)
        time.sleep(1)

    content = re.sub(r'\{\{countdown\|2.*?\}\}',
                     '{{countdown|{{subst:#time:c}}}}', content, 1)

    wb.edit_section(Session, title, section_id, content, 'Bot: 歌词翻译检查完成，现有%d首已翻译，%d首未翻译或无歌词，%d首未创建。' % (
        count_finfish, count_translate, count_create))
