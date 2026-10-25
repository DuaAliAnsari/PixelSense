# Generates placeholder images + manifest.csv. Replace any image in images/ with a real one (same filename).
import csv, os
from PIL import Image, ImageDraw, ImageFont
os.makedirs("images", exist_ok=True)
try: F = ImageFont.load_default(size=20)
except Exception: F = ImageFont.load_default()
# file, type, description, visible_text, album, suggested_label
R = [
("beach_trip","photo","Friends on a beach at sunset during a summer trip","","Travel","Travel"),
("mountain_hike","photo","Family hiking in the northern mountains","","Travel","Travel"),
("sea_sunset","photo","Sunset over the sea","","Travel",""),
("family_dinner","photo","Family dinner at a restaurant with a birthday cake","","Family","Family"),
("wedding_cousins","photo","Cousins posing together at a wedding event","","Family","Family"),
("cat_sofa","photo","Cat sleeping on a sofa","","Camera",""),
("biryani_plate","photo","Plate of biryani on a table","","Camera","Food"),
("receipt_grocery","receipt","Supermarket receipt","Imtiaz Supermarket Total Rs 4,250 Date 12 Sep","Receipts","Travel"),
("receipt_restaurant","receipt","Restaurant receipt","Cafe Total Rs 3,100 Date 3 Oct","Receipts","Receipt"),
("bill_electricity","bill","Electricity bill","K-Electric Bill Amount due Rs 8,640 Due date 28 Oct","Bills","Receipt"),
("bill_internet","bill","Internet bill","Internet bill Rs 3,500 due 5 Nov","Bills","Receipt"),
("ticket_flight","ticket","Flight boarding pass","Flight KHI to ISB Gate 14 Seat 12A","Travel","Travel"),
("shot_deadline","screenshot","Screenshot of an assignment notice","HCI assignment deadline 23 Nov submit on LMS","Screenshots","Study material"),
("shot_lecture","screenshot","Lecture slide screenshot","Lecture 7 Cognitive load theory","Screenshots","Study material"),
("shot_chat","screenshot","Chat screenshot about meeting up","Meet at 5pm outside the library","Screenshots","Study material"),
("shot_laptop","screenshot","Online listing for a laptop","Laptop for sale Rs 185,000","Shopping","Shopping"),
("shot_shoes","screenshot","Sale post for running shoes","Running shoes sale Rs 7,999","Shopping","Shopping"),
("poster_techfest","document","University tech fest poster","Tech Fest 14 Nov main auditorium","Screenshots","Event"),
("private_bank_sms","screenshot","Synthetic bank message screenshot","Your account balance alert (sample)","Private","Receipt"),
("private_note","screenshot","Synthetic personal note screenshot","Personal note (sample)","Private",""),
]
cols = [(60,90,140),(70,120,90),(150,90,70),(110,80,140),(140,120,60),(60,120,130)]
with open("manifest.csv","w",newline="",encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id","file","type","description","visible_text","album","suggested_label"])
    for i,(fn,t,d,v,a,s) in enumerate(R,1):
        p=f"images/{fn}.png"
        if not os.path.exists(p):
            im=Image.new("RGB",(400,400),cols[i%6] if t=="photo" else (245,245,240)); dr=ImageDraw.Draw(im)
            ink=(255,255,255) if t=="photo" else (30,30,30)
            dr.text((20,20),f"[{t}] replace with real image" if t=="photo" else t.upper(),fill=ink,font=F)
            body=d if t=="photo" else v
            for n,line in enumerate([body[j:j+28] for j in range(0,len(body),28)]): dr.text((20,70+n*28),line,fill=ink,font=F)
            im.save(p)
        w.writerow([f"img{i:02d}",p,t,d,v,a,s])
print("done")
