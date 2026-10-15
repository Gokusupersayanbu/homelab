/* Barras de espacio y disponibilidad. Ejemplo basado en la integración comprobada.
   Dependiente de la estructura HTML de Homepage: revisar tras actualizar. */
(() => {
  if (window.__homelabStorageBars) return;
  window.__homelabStorageBars = true;
  const diskIds = ["almacenamiento-local", "almacenamiento-lvm", "backup-emmc"];
  function getPercentage(card) {
    const elements = card.querySelectorAll("span, div, p, strong");
    for (const element of elements) {
      if (element.childElementCount !== 0) continue;
      const value = element.textContent.trim();
      if (!/^\d+(?:[.,]\d+)?\s*%$/.test(value)) continue;
      const n = parseFloat(value.replace('%','').replace(',','.'));
      if (n>=0 && n<=100) return n;
    }
    return null;
  }
  function updateBars(){
    for(const id of diskIds){
      const card=document.getElementById(id);
      if(!card) continue;
      const pct=getPercentage(card);
      if(pct===null) continue;
      let bar=card.querySelector('.hl-progress');
      if(!bar){
        const inner=card.querySelector('.service-card');
        if(!inner) continue;
        bar=document.createElement('div');
        bar.className='hl-progress';
        bar.innerHTML='<div class="hl-progress-fill"></div>';
        bar.setAttribute('role','progressbar');
        bar.setAttribute('aria-valuemin','0');
        bar.setAttribute('aria-valuemax','100');
        inner.appendChild(bar);
      }
      if(bar.dataset.percentage!==String(pct)){
        bar.dataset.percentage=String(pct);
        bar.setAttribute('aria-valuenow',String(pct));
        bar.dataset.level=pct>=90?'danger':pct>=75?'warning':'good';
        bar.querySelector('.hl-progress-fill').style.width=`${pct}%`;
      }
    }
  }
  function initialize(){
    let pending=false;
    const observer=new MutationObserver(()=>{
      if(pending)return;
      pending=true;
      requestAnimationFrame(()=>{pending=false;updateBars();});
    });
    observer.observe(document.body,{childList:true,subtree:true,characterData:true});
    updateBars();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',initialize);
  else initialize();
})();
(() => {
  if(window.__homelabOverallStatus) return;
  window.__homelabOverallStatus=true;
  function updateOverallStatus(){
    const heading=[...document.querySelectorAll('.service-group-name')].find(
      el=>el.textContent.trim().startsWith('Servicios del Homelab'));
    if(!heading)return;
    let badge=heading.querySelector('.hl-overall-status');
    if(!badge){
      badge=document.createElement('span');
      badge.className='hl-overall-status';
      badge.setAttribute('aria-live','polite');
      badge.title='Estado de los monitores de Uptime Kuma';
      heading.appendChild(badge);
    }
    const blocks=document.querySelectorAll('#uptime .service-block');
    const upText=blocks[0]?.querySelector('.service-block-value')?.textContent.trim();
    const downText=blocks[1]?.querySelector('.service-block-value')?.textContent.trim();
    let status='unknown',label='Estado no disponible';
    if(/^\d+$/.test(upText||'')&&/^\d+$/.test(downText||'')){
      const up=Number(upText),down=Number(downText),total=up+down;
      if(total>0&&down===0){status='ok';label=`${up}/${total} monitores operativos`;}
      else if(down>0){status='error';label=`${down} de ${total} monitores caidos`;}
    }
    if(badge.textContent!==label)badge.textContent=label;
    if(badge.dataset.state!==status)badge.dataset.state=status;
  }
  function initialize(){
    let pending=false;
    new MutationObserver(()=>{
      if(pending)return;
      pending=true;
      requestAnimationFrame(()=>{pending=false;updateOverallStatus();});
    }).observe(document.body,{childList:true,subtree:true,characterData:true});
    updateOverallStatus();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initialize);
  else initialize();
})();
