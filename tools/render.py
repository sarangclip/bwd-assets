import json,sys,re,pathlib
from playwright.sync_api import sync_playwright
spec=json.load(open(sys.argv[1])); out=sys.argv[2]
tpl=pathlib.Path(__file__).with_name('template.html').resolve()
bg=pathlib.Path(spec['image']).resolve().as_uri()
hl=re.sub(r'\*(.+?)\*',r'<em>\1</em>',spec['headline'])
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1350})
    pg.goto(tpl.as_uri())
    pg.evaluate("""s=>{const $=i=>document.getElementById(i);
      $('bg').style.backgroundImage=`url("${s.bg}")`; if(s.pos)$('bg').style.setProperty('--pos',s.pos);
      $('hl').innerHTML=s.hl; $('cat').textContent=s.cat||''; if(!s.cat)$('cat').remove();
      $('date').textContent=s.date; $('src').textContent='Sumber: '+s.src;
      if(s.label)$('label').textContent=s.label; else $('label').remove();
      let fs=88; const h=$('hl'); h.style.setProperty('--fs',fs+'px');
      while((h.getBoundingClientRect().height>fs*1.08*4.2||h.scrollWidth>h.clientWidth)&&fs>56){fs-=2;h.style.setProperty('--fs',fs+'px');}
    }""",dict(bg=bg,pos=spec.get('focus'),hl=hl,cat=spec.get('category'),date=spec['date'],src=spec['source'],label=spec.get('label')))
    pg.wait_for_timeout(300); pg.screenshot(path=out); b.close()
