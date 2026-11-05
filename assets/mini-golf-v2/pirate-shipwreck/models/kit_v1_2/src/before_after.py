from PIL import Image,ImageDraw
V='../kit_v1_1/previews_kit_v1_1/';N='previews_kit_v1_2/'
T=520;im=Image.new('RGB',(3*T,2*(T+30)),(30,30,34));d=ImageDraw.Draw(im)
for r,(pre,lab) in enumerate([(V,'BEFORE kit_v1_1'),(N,'AFTER kit_v1_2')]):
    for c,n in enumerate(['s','m','l']):
        t=Image.open(f'{pre}3q_kit_rock_{n}.png').convert('RGB').resize((T,T),Image.LANCZOS);im.paste(t,(c*T,r*(T+30)+30));d.text((c*T+8,r*(T+30)+8),f'{lab}  kit_rock_{n}',fill=(240,240,240))
im.save('previews_kit_v1_2/before_after.png')
