from PIL import Image
import numpy as np, vtracer, cairosvg
from scipy.ndimage import gaussian_filter
from sklearn.cluster import KMeans
src='/home/box/agent-data/agents/318d93b2-b422-4a32-9848-e92f3e7899f4/attachments/fd509d94ff28aa70e146a76e7e2e62b3c4c9095db50979a4ac4ee6e4db1ba867.png'
im=Image.open(src).convert('RGBA'); a=np.array(im).astype(float)
white=(a[...,3]<128)|(a[...,:3].min(-1)>232)
ys,xs=np.where(~white); P=12
box=(xs.min()-P,ys.min()-P,xs.max()+P,ys.max()+P); print('crop',box)
a=a[box[1]:box[3],box[0]:box[2]]; H,W=a.shape[:2]
px=a[...,:3].reshape(-1,3); light=(a[...,3].reshape(-1)<128)|(px.min(1)>215)|((px.mean(1)>205)&(px[:,2]>170))
km=KMeans(6,n_init=4,random_state=0).fit(px[~light][::3]); pal=km.cluster_centers_; print(pal.astype(int))
lab=km.predict(px); S=4; maps=[]
up=lambda m:np.array(Image.fromarray((m*255).astype(np.uint8)).resize((W*S,H*S),Image.BICUBIC)).astype(float)
for k in range(6): maps.append(gaussian_filter(up(((lab==k)&~light).reshape(H,W)),5))
maps.append(gaussian_filter(up(light.reshape(H,W)),5))
L=np.argmax(np.stack(maps),0); out=np.zeros((H*S,W*S,4),np.uint8)
for k in range(6): out[L==k,:3]=pal[k]; out[L==k,3]=255
Image.fromarray(out).save('/tmp/q11h.png')
vtracer.convert_image_to_svg_py('/tmp/q11h.png','11-agave-to-tequila.svg',colormode='color',hierarchical='stacked',mode='spline',filter_speckle=150,color_precision=8,layer_difference=1,corner_threshold=60,length_threshold=8,splice_threshold=45,path_precision=2)
cairosvg.svg2png(url='11-agave-to-tequila.svg',write_to='/tmp/r.png',output_width=4500)
p=Image.open('/tmp/r.png'); p.save('11-agave-to-tequila.png',dpi=(300,300)); print(p.size)
q=np.array(p); al=q[...,3]; print('light opaque',((q[...,:3].min(-1)>215)&(al>0)).sum(),'partial',((al>0)&(al<255)).sum())
bg=Image.new('RGBA',p.size,(30,30,30,255));bg.alpha_composite(p);bg.convert('RGB').resize((1500,int(1500*p.height/p.width))).save('/tmp/dark4.png')
# before/after: jug+bottle (right ~45%)
x0=int(W*0.55); s=Image.fromarray(a.astype(np.uint8)).crop((x0,0,W,H)); z=2
s=s.resize((s.width*z,s.height*z),Image.NEAREST); f=p.crop((int(x0*4500/W),0,4500,p.height)).resize(s.size,Image.LANCZOS)
c=Image.new('RGBA',(s.width*2+20,s.height),(235,228,215,255))
for i,x in ((s,0),(f,s.width+20)):
  t=Image.new('RGBA',i.size,(235,228,215,255));t.alpha_composite(i.convert('RGBA'));c.paste(t,(x,0))
c.convert('RGB').save('crops/11-before-after.png'); print(c.size)
