from PIL import Image, ImageDraw, ImageFilter, ImageFont
import numpy as np, matplotlib

COR="assets/fonts/Cormorant.ttf"
SANSB=matplotlib.get_data_path()+"/fonts/ttf/DejaVuSans-Bold.ttf"
def F(p,s): return ImageFont.truetype(p,s)

CREAM=(244,232,208); GREEN=(95,138,74); GREEND=(74,110,58); PLUM=(45,31,58); PLUM2=(74,54,94)
W,H=1200,900

# ---- bg ----
yy,xx=np.mgrid[0:H,0:W]
d=np.sqrt((xx-W/2)**2+(yy-H*0.36)**2); d/=d.max()
c0=np.array([248,238,218]); c1=np.array([232,219,196])
bg=(c0*(1-d[...,None])+c1*d[...,None]).astype(np.uint8)
img=Image.fromarray(np.dstack([bg,np.full((H,W),255,np.uint8)]),"RGBA")

# ---- scattered leaf stamps (behind everything) ----
leafsrc=Image.open("assets/leaf.png").convert("RGBA")
def tint(im,rgb):
    a=np.array(im); a[:,:,0]=rgb[0]; a[:,:,1]=rgb[1]; a[:,:,2]=rgb[2]; return Image.fromarray(a)
def fade(im,f):
    a=np.array(im); a[:,:,3]=(a[:,:,3]*f).astype("uint8"); return Image.fromarray(a)
def stamp(cx,cy,h,ang,op,col=None):
    im=tint(leafsrc,col) if col else leafsrc
    im=fade(im,op).rotate(ang,expand=True,resample=Image.BICUBIC)
    w=int(h*im.size[0]/im.size[1]); im=im.resize((w,int(h)))
    img.alpha_composite(im,(int(cx-w/2),int(cy-h/2)))
rng=np.random.default_rng(7)
# cream-strip placement only — nothing over the laptop or behind the mushroom mark
spots=[(60,90),(50,290),(66,500),(88,700),(120,835),
       (1140,90),(1150,290),(1134,500),(1112,700),(1080,838)]
for i,(x,y) in enumerate(spots):
    ang=float(rng.integers(0,360)); sz=float(rng.integers(95,150)); op=float(rng.uniform(0.08,0.12))
    col=PLUM2 if i%3==0 else None     # every 3rd leaf is a purple accent
    stamp(x,y,sz,ang,op,col)

dr=ImageDraw.Draw(img)
def ctext(y,text,font,fill,ls=0,cx=W/2):
    if ls==0:
        w=dr.textlength(text,font=font); dr.text((cx-w/2,y),text,font=font,fill=fill)
    else:
        tot=sum(dr.textlength(c,font=font)+ls for c in text)-ls; x=cx-tot/2
        for c in text: dr.text((x,y),c,font=font,fill=fill); x+=dr.textlength(c,font=font)+ls
def fit(path,text,maxw,start):
    s=start
    while s>10:
        f=F(path,s)
        if dr.textlength(text,font=f)<=maxw: return f
        s-=2
    return F(path,10)

# ---- brand mark + text (all green; pill outline plum=purple accent) ----
mush=Image.open("assets/mushroom.png").convert("RGBA")
mw=66; mh=int(mw*mush.size[1]/mush.size[0])
img.alpha_composite(mush.resize((mw,mh)),(int(W/2-mw/2),22))
ctext(98,"INTERACTIVE  ANIMATED  STORYBOOK",F(SANSB,19),GREEND,ls=4)
tf=fit(COR,"Whispering Woods Books",1040,140)
ctext(120,"Whispering Woods Books",tf,GREEND)   # moved up, now green
pill="PIP  AND  THE  MAGIC  MUSHROOM  RINGS"; pf=F(SANSB,20)
pw=sum(dr.textlength(c,font=pf)+3 for c in pill)-3
px0=W/2-pw/2-26; py0=262
dr.rounded_rectangle([px0,py0,W/2+pw/2+26,py0+50],radius=25,outline=PLUM,width=2)  # purple accent
ctext(py0+13,pill,pf,GREEND,ls=3)

# ---- laptop (no badges baked in) ----
SW,SH=760,475; SX=(W-SW)//2; SY=352
lx0,ly0=SX-20,SY-24; lx1,ly1=SX+SW+20,SY+SH+26; RL=20
sh=Image.new("RGBA",(W,H),(0,0,0,0))
ImageDraw.Draw(sh).ellipse([SX-40,ly1+70,SX+SW+40,ly1+150],fill=(60,50,40,150))
sh=sh.filter(ImageFilter.GaussianBlur(34)); img.alpha_composite(sh); dr=ImageDraw.Draw(img)
def vgrad(y0,y1,ct,cb):
    g=np.zeros((H,W,4),np.uint8)
    for yr in range(max(0,y0),min(H,y1)):
        t=(yr-y0)/(y1-y0); g[yr,:,:3]=(np.array(ct)*(1-t)+np.array(cb)*t).astype(np.uint8)
    g[...,3]=255; return Image.fromarray(g,"RGBA")
lg=vgrad(ly0,ly1+1,[78,82,86],[40,43,46])
lm=Image.new("L",(W,H),0); ImageDraw.Draw(lm).rounded_rectangle([lx0,ly0,lx1,ly1],radius=RL,fill=255)
img.paste(lg,(0,0),lm); dr=ImageDraw.Draw(img)
dr.rounded_rectangle([lx0,ly0,lx1,ly1],radius=RL,outline=(170,176,180,200),width=2)
dr.rounded_rectangle([lx0+2,ly0+2,lx1-2,ly1-2],radius=RL-2,outline=(255,255,255,45),width=1)
dr.rounded_rectangle([SX-7,SY-7,SX+SW+7,SY+SH+7],radius=10,fill=(8,9,10,255))
dr.ellipse([W/2-3,ly0+10,W/2+3,ly0+16],fill=(70,78,72,255))
dr.rounded_rectangle([lx0+24,ly1+1,lx1-24,ly1+9],radius=4,fill=(150,156,160,255))
base=[(lx0-26,ly1+9),(lx1+26,ly1+9),(lx1+8,ly1+44),(lx0-8,ly1+44)]
bg2=vgrad(ly1+9,ly1+45,[190,195,198],[120,126,130])
bm=Image.new("L",(W,H),0); ImageDraw.Draw(bm).polygon(base,fill=255)
img.paste(bg2,(0,0),bm); dr=ImageDraw.Draw(img)
dr.line(base+[base[0]],fill=(110,116,120,255),width=2)
dr.rounded_rectangle([W/2-50,ly1+9,W/2+50,ly1+20],radius=6,fill=(120,126,130,255))

img=img.convert("RGBA")
hole=Image.new("L",(W,H),0); ImageDraw.Draw(hole).rounded_rectangle([SX,SY,SX+SW,SY+SH],radius=8,fill=255)
arr=np.array(img); arr[:,:,3]=np.where(np.array(hole)>0,0,arr[:,:,3]); img=Image.fromarray(arr)
sheen=Image.new("RGBA",(W,H),(0,0,0,0))
ImageDraw.Draw(sheen).polygon([(SX,SY),(SX+SW*0.4,SY),(SX,SY+SH*0.7)],fill=(255,255,255,15))
sheen=sheen.filter(ImageFilter.GaussianBlur(7)); sa=np.array(sheen)
sa[:,:,3]=np.where(np.array(hole)>0,sa[:,:,3],0)
img=Image.alpha_composite(img,Image.fromarray(sa))
img.save("assets/gallery-frame.png")
print("FRAME 1200x900  scale=760:475 overlay=%d:%d"%(SX,SY))

# ---- 3 standalone transparent badges ----
def make_badge(fname,base,l1,l2):
    SS=4; S=380*SS; cx=cy=S//2; r=int(168*SS)
    c=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(c)
    circ=Image.new("L",(S,S),0); ImageDraw.Draw(circ).ellipse([cx-r,cy-r,cx+r,cy+r],fill=255)
    cmask=np.array(circ)/255.0
    # solid smooth disc (no glare)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=base+(255,))
    # clean rim + cream inner ring
    d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=(244,232,208,140),width=SS*2)
    d.ellipse([cx-r+SS*11,cy-r+SS*11,cx+r-SS*11,cy+r-SS*11],outline=(244,232,208,205),width=SS*2)
    # text + stars
    f=F(SANSB,40*SS)
    for i,ln in enumerate([l1,l2]):
        w=d.textlength(ln,font=f); d.text((cx-w/2,cy-46*SS+i*48*SS),ln,font=f,fill=(244,232,208,255))
    fs=F(SANSB,26*SS)
    for ln,yy2 in [("\u2605 \u2605",cy-r+34*SS),("\u2605 \u2605",cy+r-64*SS)]:
        w=d.textlength(ln,font=fs); d.text((cx-w/2,yy2),ln,font=fs,fill=(244,232,208,225))
    c.resize((380,380),Image.LANCZOS).save(fname)
make_badge("assets/badge-animated.png",GREEN,"ANIMATED","PAGES")
make_badge("assets/badge-browser.png",PLUM2,"ANY","BROWSER")     # purple badge
make_badge("assets/badge-noapp.png",GREEND,"NO APP","NEEDED")
make_badge("assets/badge-swipe.png",PLUM2,"SWIPE TO","TURN")     # purple touch badge
print("badges saved")
