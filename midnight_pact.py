# MidnightPact - Python GUI版 (tkinter, 无需安装)
import tkinter as tk
from tkinter import messagebox
import json, random, os, time, threading
from pathlib import Path

os.chdir(Path(__file__).parent)

# ======================== 存档 ========================
def save():
    try: json.dump(GS, open("midnight_save.json","w",encoding="utf-8"))
    except: pass

def load():
    try: return json.load(open("midnight_save.json","r",encoding="utf-8"))
    except: return None

def stats_load():
    try: return json.load(open("midnight_stats.json","r",encoding="utf-8"))
    except: return {"ends":[],"items":[]}

def stats_save(s):
    try: json.dump(s, open("midnight_stats.json","w",encoding="utf-8"))
    except: pass

GS = {"room":"bedroom","phase":0,"inv":[],"fl":{},"md":False,"kd":False}

def reset_game():
    global GS
    GS = {"room":"bedroom","phase":0,"inv":[],"fl":{},"md":False,"kd":False}
    save()

def add_item(name):
    for i in GS["inv"]:
        if i["name"] == name: return
    GS["inv"].append({"name":name})
    s = stats_load()
    if name not in s["items"]:
        s["items"].append(name); stats_save(s)
    refresh_ui()

# ======================== 房间数据 ========================
ROOMS = {
    "bedroom": {"name":"卧 室","items":{"电脑":"monitor","床铺":"bed","衣柜":"closet","窗户":"window",
        "书架":"shelf","床头柜":"nightstand"},"moves":{"浴室":("bathroom","mirrorTask"),"走廊":("hallway",None),"客厅":("living",None)}},
    "bathroom":{"name":"浴 室","items":{"镜子":"mirror","洗手台":"sink","淋浴间":"shower","储物柜":"cabinet"},"moves":{"卧室":("bedroom",None)}},
    "hallway":{"name":"走 廊","items":{"大门":"frontdoor","303室":"nbrdoor","门垫":"doormat"},"moves":{"卧室":("bedroom",None),"地下室":("basement",None)}},
    "living":{"name":"客 厅","items":{"电视":"tv","沙发":"sofa","电话":"phone","照片":"lphoto"},"moves":{"厨房":("kitchen",None),"卧室":("bedroom",None)}},
    "kitchen":{"name":"厨 房","items":{"冰箱":"fridge","刀架":"knife","抽屉":"drawer"},"moves":{"客厅":("living",None)}},
    "basement":{"name":"地下室","items":{"旧纸箱":"boxes","旧箱子":"trunk","热水器":"heater"},"moves":{"走廊":("hallway",None)}}
}

TEXTS = {
    "monitor_1":"一封新邮件。发件人空缺。\n\n「你已经被邀请了。凌晨三点见。」\n发送时间：2003年3月3日。",
    "monitor_2":"管理员帖: 第一场游戏——镜中人。\n规则：凌晨三点，面对镜子，念三遍自己的名字。\n\n提示：去浴室，站在镜子前。",
    "monitor_clues":"论坛刷新。管理员新帖：「第二场游戏——开门。」\n四号成员：「不要开。它在我门口。」\n\n提示：去走廊——站在大门前。",
    "monitor_seven":"最后的私信\n\n七号：「林霄——我在公寓外面。出来见我。」\n\n提示：去走廊——打开大门见七号。或留在家里。",
    "bed":"被子湿透了。另一个枕头有凹痕。\n枕下摸到一撮湿漉漉的黑发——不是你的。",
    "closet":"纸条被钉在木板上——钉子是一枚人指甲。\n\n「不要玩第二场游戏。不要开门。它一旦进来就不会走了。」",
    "closet2":"柜门虚掩着。里面有什么在轻轻刮木头...",
    "window":"外面是实心的黑。玻璃外面的雾...形状像一张脸。",
    "shelf":"2003年剪报。13名大学生死亡。\n照片里有一张脸——很像你。眼角有颗痣。",
    "shelf2":"剪报还夹在书里。书翻到了第13页...",
    "nightstand":"床头柜上放着一杯水。药瓶压着纸条：\n「第十一天。已经记不清上次睡是什么时候了。」",
    "mirror_needed":"镜子里你的倒影——黑眼圈很重。\n倒影比你提前眨了眼睛。",
    "mirror_done":"瞥了一眼镜子。倒影还在看你...\n在默念你的名字。",
    "mirror_game":"关灯。面对镜子。念名字。一遍。两遍。三遍。\n嘴唇停下来了——镜子里的那张嘴还在动。\n它在尖叫。无声地。指甲抠在玻璃内侧...",
    "sink":"拧开水龙头——深红色液体。温热的。粘稠的。",
    "shower":"浴帘后面...下水口堵着一大团黑发。扯不动。",
    "cabinet":"一瓶安眠药——空的。三十片。纸条：\n「别睡。你一睡它就会进来。已经挺了七天。」",
    "frontdoor_lock":"大门。门锁完好。门下缝隙慢慢渗进一小滩深色液体...",
    "frontdoor_wait":"站到门前——门把手自己在轻轻转动...",
    "frontdoor_open":"凌晨三点三十三分。手放到门把手上——把手是温的，湿的。\n打开门。走廊一片漆黑。湿漉漉的拍打声。在你门口停住。咚。",
    "frontdoor_result":"天花板上——一对湿脚印。倒悬着往房间方向延伸...\n\n提示：回卧室看电脑。",
    "frontdoor_seven":"七号就在门外。打开门面对她。",
    "nbrdoor":"303室。敲了敲——没人应答。\n转身要走——门里传出脚步声。和你同步的。",
    "doormat":"门垫下面压着几封信。给303室住户。全都没拆封。",
    "tv":"老电视。按了开关——屏幕亮了。\n雪花噪点里有一张脸：\n「第三轮了...你已经死过两次了...」",
    "sofa":"沙发垫子下面——一本日记。封面上是你的名字。\n「第三天。七号联系了我。」\n「她不是受害者。她是招募者。」",
    "sofa2":"沙发上有个凹陷——人的形状。但没有人。",
    "phone":"老式座机。拿起听筒——拨号音。夹杂着呼吸声。\n「你是第十三号。七号会来接你的。」",
    "phone2":"电话线被拔了。但拿起听筒——还是有拨号音。",
    "lphoto":"墙上照片——你和一群论坛成员。\n中间瘦削女人站你旁边。背面标注：「七号——招募者」。",
    "fridge":"打开冰箱——一个玻璃罐。泡着几颗人的臼齿。\n标签：「第三轮收集。还差三颗。」",
    "fridge2":"冰箱嗡鸣。罐子在。好像比上次多了一颗。",
    "knife":"刀架上有五把刀。四把在——最外面那把不见了。\n在旁边灶台上找到了。刀刃上沾着干涸痕迹。",
    "knife2":"刀架上少了一把刀。不在灶台上。在哪里？",
    "drawer":"一叠旧信封。收件人都是你。里面一张照片——是你，穿着不认识的衣服。",
    "boxes":"几个积满灰尘的旧纸箱。箱底压着纸条：\n「第三轮。你每次都会忘。每次都会重新来。」",
    "boxes2":"箱子被翻过了。灰尘上有手印。",
    "trunk":"锁着的旧箱子。打开——失踪人口档案。\n最后一份封面——贴着你的照片。",
    "trunk2":"箱子开着的。档案还在。",
    "heater":"老式热水器。管道嗡嗡作响。夏天没人开热水器。\n管道里传出敲击声：三下，停，三下。",
    "computer_empty":"电脑屏幕亮着。你不敢看暗下去的屏幕反光。"
}

# ======================== GUI ========================
root = tk.Tk()
root.title("三更之约 MidnightPact")
root.geometry("900x650")
root.configure(bg="#0a0a0a")
root.resizable(True, True)

# 标题画面
title_frame = tk.Frame(root, bg="#0a0000")
title_label = tk.Label(title_frame, text="三 更 之 约", font=("SimSun","宋体",48,"bold"),
    fg="#8b0000", bg="#0a0000")
sub_label = tk.Label(title_frame, text="MidnightPact", font=("SimSun",16),
    fg="#555", bg="#0a0000")
tag_label = tk.Label(title_frame, text="你没有受邀。\n你被选中了。", font=("SimSun",14),
    fg="#b33", bg="#0a0000")

# 游戏画面
game_frame = tk.Frame(root, bg="#121212")
top_bar = tk.Frame(game_frame, bg="#151515", height=50)
room_label = tk.Label(top_bar, text="卧 室", font=("SimSun",18,"bold"),
    fg="#c22", bg="#151515")
hint_label = tk.Label(top_bar, text="看看电脑——书桌上有台旧台式机",
    font=("SimSun",11), fg="#e8c070", bg="#151515")
inv_frame = tk.Frame(game_frame, bg="#0f0f0f", height=36)
inv_label = tk.Label(inv_frame, text="物 品：", font=("SimSun",10),
    fg="#666", bg="#0f0f0f")
inv_text = tk.Label(inv_frame, text="（暂无）", font=("SimSun",10),
    fg="#b99", bg="#0f0f0f")
text_area = tk.Text(game_frame, bg="#0d0d0d", fg="#bbb", font=("SimSun",12),
    wrap=tk.WORD, state=tk.DISABLED, height=12, relief=tk.FLAT, padx=15, pady=10)
item_frame = tk.Frame(game_frame, bg="#121212")

saved = load()
if saved:
    GS = saved

# ======================== 弹窗 ========================
def show_modal(title, text, btns=None):
    """显示模态弹窗，btns为[(文字,回调),...]"""
    popup = tk.Toplevel(root)
    popup.title("")
    popup.geometry("500x400+200+100")
    popup.configure(bg="#0a0a0a")
    popup.transient(root)
    popup.grab_set()
    
    tl = tk.Label(popup, text=title, font=("SimSun",16,"bold"),
        fg="#c22", bg="#0a0a0a")
    tl.pack(pady=(20,10))
    
    ta = tk.Text(popup, bg="#0d0d0d", fg="#bbb", font=("SimSun",12),
        wrap=tk.WORD, relief=tk.FLAT, padx=15, pady=15, height=12)
    ta.insert("1.0", text)
    ta.configure(state=tk.DISABLED)
    ta.pack(fill=tk.BOTH, expand=True, padx=30)
    
    bf = tk.Frame(popup, bg="#0a0a0a")
    bf.pack(pady=15)
    
    if not btns:
        btns = [("继续", lambda: popup.destroy())]
    
    for i, (label, cmd) in enumerate(btns):
        def make_cmd(c, p):
            return lambda: (c(), p.destroy())
        btn = tk.Button(bf, text=label, font=("SimSun",12),
            fg="#aaa", bg="#151515", activebackground="#2a0a0a",
            activeforeground="#f44", relief=tk.FLAT,
            padx=25, pady=8, cursor="hand2",
            command=make_cmd(cmd, popup))
        btn.pack(side=tk.LEFT, padx=8)
        btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#f44",bg="#200"))
        btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#aaa",bg="#151515"))
    
    return popup

def end_screen(title, desc):
    s = stats_load()
    if title not in s["ends"]:
        s["ends"].append(title)
        for i in GS["inv"]:
            if i["name"] not in s["items"]:
                s["items"].append(i["name"])
        stats_save(s)
    
    popup = tk.Toplevel(root)
    popup.title("")
    popup.geometry("600x450+150+100")
    popup.configure(bg="#000")
    popup.transient(root)
    popup.grab_set()
    
    tk.Label(popup, text=title, font=("SimSun",28,"bold"),
        fg="#8b0000", bg="#000").pack(pady=(40,15))
    tk.Label(popup, text=desc, font=("SimSun",12),
        fg="#888", bg="#000", wraplength=450).pack(pady=15)
    
    bf = tk.Frame(popup, bg="#000")
    bf.pack(pady=25)
    
    def restart():
        popup.destroy()
        show_title()
    def exit_game():
        popup.destroy()
        root.destroy()
    
    for label, cmd in [("重新开始", restart), ("退出", exit_game)]:
        btn = tk.Button(bf, text=label, font=("SimSun",12),
            fg="#aaa", bg="#151515", activebackground="#2a0a0a",
            activeforeground="#f44", relief=tk.FLAT,
            padx=30, pady=8, cursor="hand2", command=cmd)
        btn.pack(side=tk.LEFT, padx=8)
        btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#f44",bg="#200"))
        btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#aaa",bg="#151515"))

# ======================== 相互作用 ========================
def interact(item_id):
    global GS
    
    if item_id == "monitor":
        if GS["phase"] == 0:
            GS["phase"] = 1
            GS["fl"]["mirrorTask"] = True
            add_item("指缝碎屑")
            save()
            show_modal("新邮件", TEXTS["monitor_1"], [
                ("点击链接", lambda: show_modal("论坛", TEXTS["monitor_2"]))
            ])
            refresh_ui()
        elif GS["md"] and not GS["kd"]:
            clues = sum(1 for k in ["cf","sf","sof","ph","ff","trunkF","boxesF"] if GS["fl"].get(k))
            if clues < 2:
                show_modal("电脑", "论坛上还没有新帖子。在屋子里多找找线索。\n（已找到线索："+str(clues)+"/2）")
            else:
                GS["fl"]["doorTask"] = True; save()
                show_modal("论坛", TEXTS["monitor_clues"]); refresh_ui()
        elif GS["kd"] and not GS["fl"].get("ended"):
            GS["fl"]["sevenTask"] = True; save()
            if GS["fl"].get("sof") and GS["fl"].get("ph"):
                show_modal("最后的私信", TEXTS["monitor_seven"]+"\n\n等一下——日记和电话。七号不是受害者——她是招募者。")
            else:
                show_modal("最后的私信", TEXTS["monitor_seven"])
            refresh_ui()
        else:
            show_modal("电脑", TEXTS["computer_empty"])
        return
    
    item_actions = {
        "bed": lambda: show_modal("床铺", TEXTS["bed"]),
        "closet": lambda: (
            GS["fl"]["cf"] and show_modal("衣柜", TEXTS["closet2"])
            or (GS["fl"].update({"cf":True}), add_item("钉着的纸条"), save(), show_modal("衣柜", TEXTS["closet"]))
        ),
        "window": lambda: show_modal("窗户", TEXTS["window"]),
        "shelf": lambda: (
            GS["fl"]["sf"] and show_modal("书架", TEXTS["shelf2"])
            or (GS["fl"].update({"sf":True}), add_item("2003年剪报"), save(), show_modal("书架", TEXTS["shelf"]))
        ),
        "nightstand": lambda: show_modal("床头柜", TEXTS["nightstand"]),
        "mirror": lambda: _mirror(),
        "sink": lambda: show_modal("洗手台", TEXTS["sink"]),
        "shower": lambda: show_modal("淋浴间", TEXTS["shower"]),
        "cabinet": lambda: (add_item("药瓶和纸条"), save(), show_modal("储物柜", TEXTS["cabinet"])),
        "frontdoor": lambda: _frontdoor(),
        "nbrdoor": lambda: show_modal("303室", TEXTS["nbrdoor"]),
        "doormat": lambda: show_modal("门垫", TEXTS["doormat"]),
        "tv": lambda: (
            GS["fl"]["tvOn"] and show_modal("电视", TEXTS["tv"])
            or (GS["fl"].update({"tvOn":True}), save(), show_modal("电视", TEXTS["tv"]))
        ),
        "sofa": lambda: (
            GS["fl"]["sof"] and show_modal("沙发", TEXTS["sofa2"])
            or (GS["fl"].update({"sof":True}), add_item("旧日记"), save(), show_modal("沙发", TEXTS["sofa"]))
        ),
        "phone": lambda: (
            GS["fl"]["ph"] and show_modal("电话", TEXTS["phone2"])
            or (GS["fl"].update({"ph":True}), save(), show_modal("电话", TEXTS["phone"]))
        ),
        "lphoto": lambda: (add_item("客厅照片"), save(), show_modal("照片", TEXTS["lphoto"])),
        "fridge": lambda: (
            GS["fl"]["ff"] and show_modal("冰箱", TEXTS["fridge2"])
            or (GS["fl"].update({"ff":True}), add_item("装满牙齿的罐子"), save(), show_modal("冰箱", TEXTS["fridge"]))
        ),
        "knife": lambda: (
            GS["fl"]["kf"] and show_modal("刀架", TEXTS["knife2"])
            or (GS["fl"].update({"kf":True}), add_item("带血的刀"), save(), show_modal("刀架", TEXTS["knife"]))
        ),
        "drawer": lambda: (add_item("抽屉里的照片"), save(), show_modal("抽屉", TEXTS["drawer"])),
        "boxes": lambda: (
            GS["fl"]["boxesF"] and show_modal("旧纸箱", TEXTS["boxes2"])
            or (GS["fl"].update({"boxesF":True}), add_item("箱子里的纸条"), save(), show_modal("旧纸箱", TEXTS["boxes"]))
        ),
        "trunk": lambda: (
            GS["fl"]["trunkF"] and show_modal("旧箱子", TEXTS["trunk2"])
            or (GS["fl"].update({"trunkF":True}), add_item("失踪档案"), save(), show_modal("旧箱子", TEXTS["trunk"]))
        ),
        "heater": lambda: (add_item("热水器"), save(), show_modal("热水器", TEXTS["heater"])),
    }
    
    fn = item_actions.get(item_id)
    if fn: fn()

def _mirror():
    if GS["md"]:
        show_modal("镜子", TEXTS["mirror_done"])
    elif not GS["fl"].get("mirrorTask"):
        show_modal("镜子", TEXTS["mirror_needed"])
    else:
        GS["md"] = True; add_item("镜中笔记"); save()
        show_modal("镜中人", TEXTS["mirror_game"], [
            ("尖叫后退", lambda: show_modal("浴室地板","摔倒在浴室地板上。瓷砖是湿的——不是水。\n\n提示：回卧室看电脑。")),
            ("伸手摸镜子", lambda: show_modal("镜子","指尖碰到玻璃——不是冷的。37度。\n镜子里的唇语：「你已经在里面了。」\n\n提示：回卧室看电脑。"))
        ])
        refresh_ui()

def _frontdoor():
    if GS["kd"] and GS["fl"].get("sevenTask"):
        show_modal("公寓外", "七号就在这扇门的外面。她在等你。「林霄——你来了。」", [
            ("打开门去见七号", lambda: _chase()),
            ("转身回家", lambda: end_screen("幸运的你","你转身离开。第二天太阳照常升起。论坛消失了。"))
        ])
    elif GS["kd"]:
        show_modal("大门", TEXTS["frontdoor_seven"])
    elif not GS["fl"].get("doorTask"):
        show_modal("大门", TEXTS["frontdoor_lock"])
    elif GS["fl"].get("doorTried"):
        show_modal("大门", TEXTS["frontdoor_wait"])
    else:
        GS["fl"]["doorTried"] = True
        def door_result():
            GS["kd"] = True
            add_item("湿足迹" if random.random()>0.5 else "塞进门的纸条")
            save(); refresh_ui()
            show_modal("门开了", TEXTS["frontdoor_result"])
        show_modal("开门", TEXTS["frontdoor_open"], [
            ("抬头看", door_result),
            ("关门", door_result)
        ])

# ======================== 追逐战 ========================
def _chase():
    from tkinter import simpledialog
    has_knife = any(i["name"]=="带血的刀" for i in GS["inv"])
    
    result = ["escaped"]
    window = tk.Toplevel(root)
    window.title("追逐战")
    window.geometry("600x500+150+80")
    window.configure(bg="#0a0000")
    window.transient(root)
    window.grab_set()
    
    timer_label = tk.Label(window, text="30", font=("SimSun",48,"bold"),
        fg="#f44", bg="#0a0000")
    timer_label.pack(pady=10)
    
    status_label = tk.Label(window, text="躲避七号的分身！使用按钮移动", font=("SimSun",14),
        fg="#e8c070", bg="#0a0000")
    status_label.pack(pady=5)
    
    bridge_label = tk.Label(window, text="天桥可用: 3", font=("SimSun",11),
        fg="#68a", bg="#0a0000")
    bridge_label.pack(pady=2)
    
    charge_label = tk.Label(window, text="", font=("SimSun",11),
        fg="#ff0", bg="#0a0000")
    charge_label.pack(pady=2)
    
    game_over = [False]
    timer_val = [30]
    bridges_left = [3]
    charge = [0]
    rage = [False]
    rage_timer = [0]
    
    def update_timer():
        if game_over[0] or window.winfo_exists()==0:
            return
        timer_val[0] -= 1
        
        # 狂暴
        if timer_val[0] % 5 < 3:
            rage_timer[0] -= 1
            if rage_timer[0] <= 0:
                rage[0] = not rage[0]
                rage_timer[0] = 3 if rage[0] else 2
            if rage[0]:
                timer_label.configure(fg="#f80")
                status_label.configure(text="⚠ 七号暴走了！快躲！")
        
        timer_label.configure(text=str(max(0, timer_val[0])))
        if timer_val[0] <= 0:
            game_over[0] = True
            window.destroy()
            items_count = len(GS["inv"])
            if items_count >= 5:
                end_screen("逃离", "三十秒像三十年。七号的分身们停住了。天边泛白，你活下来了。\n你感觉自己掌握了很多线索...")
            else:
                end_screen("逃离", "三十秒像三十年。七号的分身们停住了。天边泛白，你活下来了。")
            return
        if not game_over[0]:
            root.after(1000, update_timer)
    
    def move(dir):
        if game_over[0]: return
        danger = random.random()
        if not rage[0] and danger < 0.15:
            game_over[0] = True
            window.destroy()
            if timer_val[0] > 25:
                end_screen("瞬间被擒", "你甚至来不及反应——七号的手已经掐住了你的喉咙。")
            else:
                end_screen("被困者", "七号的分身抓住了你。二十三年间她抓过无数人。")
            return
        elif rage[0] and danger < 0.35:
            game_over[0] = True
            window.destroy()
            end_screen("被困者", "七号暴走时抓住了你。太快了。")
            return
        
        if danger < 0.3:
            status_label.configure(text="七号的脚步声越来越近！")
        else:
            status_label.configure(text="WASD移动中... 方向: "+dir)
    
    def use_bridge():
        if game_over[0]: return
        if bridges_left[0] > 0:
            bridges_left[0] -= 1
            bridge_label.configure(text="天桥可用: "+str(bridges_left[0]))
            status_label.configure(text="跳上天桥！七号在下面徘徊（安全3秒）")
            status_label.configure(fg="#6af")
            root.after(3000, lambda: status_label.configure(fg="#e8c070"))
        else:
            status_label.configure(text="天桥已用尽！")
    
    def attack():
        if game_over[0]: return
        if not has_knife:
            status_label.configure(text="没有武器！去厨房找刀")
            return
        danger = random.random()
        if danger < 0.3:
            charge[0] += 20
            charge_label.configure(text="蓄力: "+str(charge[0])+"%")
            if charge[0] >= 100:
                game_over[0] = True
                window.destroy()
                end_screen("真正的胜利", "蓄力条满的瞬间——你冲向七号。刀刃刺穿她的身体，所有分身碎裂。\n她低头看伤口，笑了：终于有人做到了。循环结束。你赢了。")
                return
        elif danger < 0.6:
            status_label.configure(text="太远了！靠近七号再按空格！")
        else:
            status_label.configure(text="攻击偏了！")
    
    mv_frame = tk.Frame(window, bg="#0a0000")
    mv_frame.pack(pady=20)
    
    # WASD layout
    dirs = [("W ↑", "上", 0,1), ("A ←", "左", 2,0), ("D →", "右", 2,2)]
    for i, (label, dir, row, col) in enumerate(dirs):
        btn = tk.Button(mv_frame, text=label, font=("SimSun",14),
            width=8, height=2, fg="#aaa", bg="#200",
            activebackground="#400", activeforeground="#f44",
            relief=tk.FLAT, cursor="hand2",
            command=lambda d=dir: move(d))
        btn.grid(row=row, column=col, padx=5, pady=5)
        btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#f44"))
        btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#aaa"))
    
    # S
    btn = tk.Button(mv_frame, text="S ↓", font=("SimSun",14),
        width=8, height=2, fg="#aaa", bg="#200",
        activebackground="#400", activeforeground="#f44",
        relief=tk.FLAT, cursor="hand2",
        command=lambda: move("下"))
    btn.grid(row=1, column=1, padx=5, pady=5)
    btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#f44"))
    btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#aaa"))
    
    act_frame = tk.Frame(window, bg="#0a0000")
    act_frame.pack(pady=10)
    
    for label, cmd in [("天桥 F", use_bridge), ("攻击 [空格]", attack)]:
        btn = tk.Button(act_frame, text=label, font=("SimSun",12),
            width=10, height=2, fg="#e8c070", bg="#200",
            activebackground="#400", activeforeground="#ff0",
            relief=tk.FLAT, cursor="hand2", command=cmd)
        btn.pack(side=tk.LEFT, padx=10)
        btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#ff0"))
        btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#e8c070"))
    
    root.after(1000, update_timer)

# ======================== UI刷新 ========================
def refresh_ui():
    room = ROOMS[GS["room"]]
    room_label.configure(text=room["name"])
    
    # 提示
    hint = ""
    if GS["room"] == "bedroom":
        if GS["phase"] == 0:
            hint = "看看电脑——书桌上有台旧台式机"
        elif GS["fl"].get("mirrorTask") and not GS["md"]:
            hint = "去浴室——站在镜子前完成游戏"
        elif GS["md"] and not GS["kd"]:
            hint = "在屋子里多找找线索，至少找2个"
        elif GS["kd"] and not GS["fl"].get("sevenTask"):
            hint = "看电脑——有新信息"
        elif GS["fl"].get("sevenTask"):
            hint = "去走廊——打开大门"
    elif GS["room"] == "hallway" and GS["fl"].get("doorTask") and not GS["kd"]:
        hint = "站在大门前——别从猫眼看"
    elif GS["room"] == "bathroom" and GS["fl"].get("mirrorTask") and not GS["md"]:
        hint = "站到镜子前——念三遍你的名字"
    
    hint_label.configure(text=hint)
    
    # 物品
    inv_text.configure(text="  |  ".join(i["name"] for i in GS["inv"]) if GS["inv"] else "（暂无）")
    
    # 清除物品按钮
    for w in item_frame.winfo_children():
        w.destroy()
    
    # 添加物品按钮
    for name, item_id in room["items"].items():
        btn = tk.Button(item_frame, text=name, font=("SimSun",10),
            fg="#888", bg="#151515", activebackground="#2a0a0a",
            activeforeground="#f44", relief=tk.FLAT,
            padx=12, pady=4, cursor="hand2",
            command=lambda i=item_id: interact(i))
        btn.pack(side=tk.LEFT, padx=4, pady=4)
        btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#f44",bg="#200"))
        btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#888",bg="#151515"))
    
    # 移动到按钮
    tk.Label(item_frame, text="  |  ", font=("SimSun",10),
        fg="#444", bg="#121212").pack(side=tk.LEFT)
    
    for name, (target, need) in room["moves"].items():
        if need and not GS["fl"].get(need):
            continue
        label = "去"+name
        btn = tk.Button(item_frame, text=label, font=("SimSun",10),
            fg="#888", bg="#1a1a1a", activebackground="#2a2a0a",
            activeforeground="#ee4", relief=tk.FLAT,
            padx=12, pady=4, cursor="hand2",
            command=lambda t=target: move_room(t))
        btn.pack(side=tk.LEFT, padx=4, pady=4)
        btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#ee4",bg="#220"))
        btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#888",bg="#1a1a1a"))
    
    # 电脑按钮
    if GS["room"] == "bedroom" and (GS["phase"]<=1 or (GS["md"] and not GS["kd"]) or (GS["kd"] and not GS["fl"].get("ended"))):
        btn = tk.Button(item_frame, text="查看电脑消息", font=("SimSun",10,"bold"),
            fg="#e8c070", bg="#200", activebackground="#400",
            activeforeground="#ff0", relief=tk.FLAT,
            padx=12, pady=4, cursor="hand2",
            command=lambda: interact("monitor"))
        btn.pack(side=tk.LEFT, padx=4, pady=4)
        btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#ff0",bg="#300"))
        btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#e8c070",bg="#200"))

def move_room(target):
    GS["room"] = target
    save()
    refresh_ui()

# ======================== 标题画面 ========================
def show_title():
    game_frame.pack_forget()
    title_frame.pack(fill=tk.BOTH, expand=True)
    
    # 动态按钮
    for w in title_frame.winfo_children():
        if isinstance(w, tk.Button):
            w.destroy()
    
    title_label.pack(pady=(60,5))
    sub_label.pack(pady=5)
    tag_label.pack(pady=(10,30))
    
    saved = load()
    
    btns = [("开 始 游 戏", lambda: start_game())]
    if saved:
        btns.append(("继 续 游 戏", lambda: continue_game()))
    btns.append(("达成结局", lambda: show_stats("ends")))
    btns.append(("收集物品", lambda: show_stats("items")))
    btns.append(("退 出", lambda: root.destroy()))
    
    for text, cmd in btns:
        btn = tk.Button(title_frame, text=text, font=("SimSun",14),
            fg="#aaa", bg="#151515", activebackground="#2a0a0a",
            activeforeground="#f44", relief=tk.FLAT,
            padx=40, pady=10, cursor="hand2", command=cmd)
        btn.pack(pady=4)
        btn.bind("<Enter>", lambda e,b=btn: b.configure(fg="#f44",bg="#200"))
        btn.bind("<Leave>", lambda e,b=btn: b.configure(fg="#aaa",bg="#151515"))

def start_game():
    reset_game()
    continue_game()

def continue_game():
    global GS
    saved = load()
    if saved:
        GS = saved
    title_frame.pack_forget()
    game_frame.pack(fill=tk.BOTH, expand=True)
    top_bar.pack(fill=tk.X)
    room_label.pack(side=tk.LEFT, padx=20)
    hint_label.pack(side=tk.LEFT, padx=10)
    inv_frame.pack(fill=tk.X)
    inv_label.pack(side=tk.LEFT, padx=15)
    inv_text.pack(side=tk.LEFT)
    text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,5))
    item_frame.pack(fill=tk.X, padx=10, pady=5)
    refresh_ui()

def show_stats(typ):
    s = stats_load()
    if typ == "ends":
        title = "已达成结局"
        all_ends = ["幸运的你","反抗者","新管理员","瞬间被擒","被困者","逃离","真正的胜利"]
        lines = [("✓ " if e in s["ends"] else "○ ")+e for e in all_ends]
        lines.append(f"\n共 {len(s['ends'])}/7")
        show_modal(title, "\n".join(lines))
    else:
        title = "已收集物品"
        text = "\n".join("• "+e for e in s["items"]) if s["items"] else "尚未收集任何物品"
        show_modal(title, text+f"\n\n共 {len(s['items'])} 件")

# ======================== 启动 ========================
show_title()
root.mainloop()