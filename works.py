import requests
import re
import time
from datetime import datetime, tzinfo, timezone, timedelta

import wiki_lib as wb


def uma_music_update(Session: requests.Session):
    '更新赛马娘音乐列表'

    title = "赛马娘 Pretty Derby/译名对照表"
    table_section = "歌曲"

    count_total = 0
    count_finfish = 0
    count_translate = 0
    count_create = 0

    page_in_table = set()
    page_in_cat = set()
    page_in_template = set()
    not_in_table = set()
    not_in_cat = set()
    not_created = set()
    not_in_table_tem = set()

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

        page_in_table.add(link)
        count_total += 1

        if status == "{{支持|已收录}}":
            print("[%d] %s 为已收录，跳过检查。" % (count_total, link))
            count_finfish += 1
            continue
        elif status == "":
            if wb.check_page_exist(Session, link) == -1:
                print("[%d] %s 未被创建" % (count_total, link))
                count_create += 1
                page_in_table.remove(link)
                not_created.add(link)
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
            print("[%d]已检查 %s 翻译已完成。" % (count_total, link))
            count_finfish += 1
            content = str.replace(content, rep, '| ' +
                                  rep_link + ' || {{支持|已收录}} ||', 1)
        else:
            count_translate += 1
            print("[%d]已检查 %s 翻译未完成" % (count_total, link))
            content = str.replace(content, rep, '| ' +
                                  rep_link + ' || {{疑问|无翻译}} ||', 1)
        time.sleep(1)

    content = re.sub(r'\{\{countdown\|2.*?\}\}',
                     '{{countdown|{{subst:#time:c}}}}', content, 1)

    wb.edit_section(Session, title, section_id, content, 'Bot: 歌词翻译检查完成，现有%d首已翻译，%d首未翻译或无歌词，%d首未创建。' % (
        count_finfish, count_translate, count_create), bot=True)
    time.sleep(1)

    page_in_cat = wb.in_category(Session, "赛马娘 Pretty Derby音乐")[0]

    not_in_cat = page_in_table.copy()
    not_in_table = page_in_cat.copy()
    for val in page_in_table:
        caped = val[0].upper() + val[1:]
        if caped in page_in_cat:
            not_in_cat.remove(val)
            not_in_table.remove(caped)

    template = wb.get_wikitext(Session, "模板:赛马娘 Pretty Derby")
    template = re.search(r"相关音乐([\s\S]*)作品相关", template).group(1)
    result = re.finditer(r"\[\[(.*?)(?:\|.*?)?\]\]", template)

    for val in result:
        link = val.group(1)
        if not link in page_in_table and not link in not_created:
            not_in_table_tem.add(link)

    content = '''== 维护信息 ==
{{mbox|type=notice|image=[[File:Crystal Clear action run.svg|50px]]||text=\'\'\'此段落被[[萌娘百科:机器人|机器人]]使用。\'\'\'<br><span style="font-size: smaller;">如果您打算修改本段落，则有可能影响到机器人，请先通知机器人操作者。<br>相关的机器人：SinonJZH-bot</span>}}'''
    need_update = False

    if len(not_in_table_tem) > 0:
        need_update = True
        content += "\n<br/>以下页面在大家族模板中但不在对照表中：<br/>"
        for val in not_in_table_tem:
            content += "[[" + val + "]]，"
        content = content.strip("，")
    if len(not_in_cat) > 0:
        need_update = True
        content += "\n<br/>以下页面在对照表中但不在音乐分类中：<br/>"
        for val in not_in_cat:
            content += "[[" + val + "]]，"
        content = content.strip("，")
    if len(not_in_table) > 0:
        need_update = True
        content += "\n<br/>以下页面在音乐分类中但不在对照表中：<br/>"
        for val in not_in_table:
            content += "[[" + val + "]]，"
        content = content.strip("，")
    if len(not_created) > 0:
        need_update = True
        content += "\n<br/>以下页面尚未被创建：<br/>"
        for val in not_created:
            content += "[[" + val + "]]，"
        content = content.strip("，")
    if need_update:
        wb.edit_section(Session, title, wb.get_section_id(Session, "赛马娘 Pretty Derby/译名对照表",
                        "维护信息"), content, "有需要维护的页面，请查看[[赛马娘 Pretty Derby/译名对照表#维护信息|维护信息]]。", bot=True)


def event_count(Session: requests.Session):
    "讨论版参与人数统计"
    tz_utc_8 = timezone(timedelta(hours=8))
    fromstamp = datetime(2021, 10, 29, 20, 51, tzinfo=tz_utc_8)
    tostamp = datetime(2021, 10, 31, 0, 0, tzinfo=tz_utc_8)

    uset = wb.count_rev(Session, "萌娘百科 talk:讨论版/方针政策", fromstamp, tostamp)
    uset = wb.count_rev(Session, "萌娘百科 talk:讨论版/权限变更",
                        fromstamp, tostamp, uset)
