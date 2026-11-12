# Generate a photo-free textured background tinted by desk colour.
import sys, numpy as np
from PIL import Image, ImageFilter
desk=sys.argv[1]; out=sys.argv[2]
tint={'D1':(150,40,40),'D2':(150,115,30),'D3':(35,70,140),'D4':(95,45,130),'D5':(30,110,75),'D6':(70,80,95)}.get(desk[:2],(60,60,70))
h,w=1350,1080; rng=np.random.default_rng(abs(hash(out))%2**32)
yy,xx=np.mgrid[0:h,0:w]/np.array([h,w])[:,None,None]
glow=np.exp(-(((xx-0.75)**2)/0.08+((yy-0.25)**2)/0.06))
base=np.zeros((h,w,3)); 
for i in range(3): base[...,i]=14+tint[i]*0.55*glow+tint[i]*0.12*(1-yy)
lines=((xx*w+yy*h*0.6)%46<1.2)*10*glow          # faint diagonal hatch
noise=rng.normal(0,6,(h,w))
img=base+(lines+noise)[...,None]
Image.fromarray(img.clip(0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.6)).save(out,quality=92)
