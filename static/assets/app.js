/* ===== یدک‌پخش — کدهای مشترک همهٔ صفحات ===== */
const $=(s,r=document)=>r.querySelector(s),$$=(s,r=document)=>[...r.querySelectorAll(s)];
const fa=n=>Number(n).toLocaleString('fa-IR');
const toEn=s=>String(s==null?'':s).replace(/[۰-۹]/g,d=>'۰۱۲۳۴۵۶۷۸۹'.indexOf(d)).replace(/[٠-٩]/g,d=>'٠١٢٣٤٥٦٧٨٩'.indexOf(d));
const norm=s=>toEn(String(s).toLowerCase()).replace(/ي/g,'ی').replace(/ك/g,'ک');
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const LS={get(k,d){try{const v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}},del(k){try{localStorage.removeItem(k)}catch(e){}}};
const qs=k=>new URLSearchParams(location.search).get(k);
const fdate=t=>new Date(t).toLocaleDateString('fa-IR',{year:'numeric',month:'long',day:'numeric'});
const safeNext=n=>/^\/(?!\/)[\w\-\/]*([?#][^\s]*)?$/.test(n||'')?n:'';
const P={menu:'<path d="M4 7h16M4 12h16M4 17h16"/>',search:'<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',cart:'<path d="M3 4h2l2.4 11h10.2L20 7H6.2"/><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/>',user:'<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',call:'<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',down:'<path d="M6 9l6 6 6-6"/>',left:'<path d="M15 6l-6 6 6 6"/>',right:'<path d="M9 6l6 6-6 6"/>',plus:'<path d="M12 5v14M5 12h14"/>',minus:'<path d="M5 12h14"/>',close:'<path d="M6 6l12 12M18 6L6 18"/>',gift:'<rect x="3" y="8" width="18" height="13" rx="1"/><path d="M12 8v13M3 12h18M12 8c-3 0-4-4-1.5-4S12 8 12 8zm0 0c3 0 4-4 1.5-4S12 8 12 8z"/>',about:'<path d="M4 21V8l8-5 8 5v13M9 21v-6h6v6"/>',org:'<circle cx="9" cy="9" r="3"/><circle cx="17" cy="10" r="2.5"/><path d="M3 19c0-3 3-5 6-5s6 2 6 5M15 15c3 0 6 1 6 4"/>',partner:'<path d="M3 12l5-5 4 3 4-3 5 5-9 8z"/>',truck:'<path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="17.5" r="1.7"/><circle cx="17" cy="17.5" r="1.7"/>',shield:'<path d="M12 3l8 3v6c0 4.5-3.3 8-8 9-4.7-1-8-4.5-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',headset:'<path d="M4 12a8 8 0 0116 0v4a2 2 0 01-2 2h-1v-6h3M4 12v4a2 2 0 002 2h1v-6H4"/>',card:'<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18M7 15h3"/>',question:'<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 114 2c-1 .7-1.5 1-1.5 2M12 17h.01"/>',location:'<path d="M12 21s7-6 7-11a7 7 0 10-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',home:'<path d="M3 11l9-8 9 8M5 10v10h5v-6h4v6h5V10"/>',instagram:'<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',telegram:'<path d="M21 4L10 14M21 4l-6 17-5-7-7-3z"/>',email:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>'};
const A='fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"';
const CI={
brake:`<circle cx="32" cy="32" r="26"/><circle cx="32" cy="32" r="9"/><circle cx="32" cy="32" r="2.5" fill="currentColor"/><circle cx="32" cy="15" r="2.5"/><circle cx="32" cy="49" r="2.5"/><circle cx="15" cy="32" r="2.5"/><circle cx="49" cy="32" r="2.5"/><circle cx="20" cy="20" r="2.5"/><circle cx="44" cy="44" r="2.5"/><circle cx="44" cy="20" r="2.5"/><circle cx="20" cy="44" r="2.5"/>`,
filter:`<rect x="14" y="16" width="36" height="38" rx="5"/><path d="M18 16v-4h28v4M22 24v22M30 24v22M38 24v22M46 24v22M12 54h40"/>`,
plug:`<path d="M26 6h12v12H26zM28 18v10h8V18M22 28h20v10H22zM26 38v12M38 38v12M32 38v18M28 56h8"/>`,
shock:`<path d="M32 4v14M28 18h8v8M32 26v34M20 28l24 4-24 4 24 4-24 4 24 4-24 4M26 60h12"/>`,
battery:`<rect x="6" y="20" width="52" height="34" rx="4"/><path d="M14 20v-6h8v6M42 20v-6h8v6M16 37h10M44 31v12M38 37h12"/>`,
oil:`<path d="M26 6h12v8l8 8v32a4 4 0 01-4 4H22a4 4 0 01-4-4V22l8-8zM18 32h28M18 44h28M44 8l8 6"/>`,
bearing:`<circle cx="32" cy="32" r="26"/><circle cx="32" cy="32" r="16"/><circle cx="32" cy="32" r="6"/><circle cx="32" cy="20" r="2"/><circle cx="32" cy="44" r="2"/><circle cx="20" cy="32" r="2"/><circle cx="44" cy="32" r="2"/>`,
belt:`<circle cx="18" cy="32" r="12"/><circle cx="46" cy="22" r="8"/><circle cx="46" cy="44" r="8"/><path d="M18 20L46 14M18 44l28 8M54 22v22"/>`,
bulb:`<path d="M22 40c-6-4-8-9-8-14a18 18 0 0136 0c0 5-2 10-8 14v6H22zM24 52h16M27 58h10M28 46v-10l4 4 4-4v10"/>`,
wiper:`<path d="M6 50L58 24M6 50l6 6M18 44l4 8M30 38l4 8M42 32l4 8"/>`,
tire:`<circle cx="32" cy="32" r="27"/><circle cx="32" cy="32" r="16"/><circle cx="32" cy="32" r="4"/><path d="M32 16v12M32 36v12M16 32h12M36 32h12M21 21l8 8M35 35l8 8M43 21l-8 8M29 35l-8 8"/>`,
tools:`<path d="M44 8a12 12 0 00-11 17L10 48a5 5 0 007 7l23-23a12 12 0 0017-11l-8 8-7-2-2-7z"/>`
};
const svg=(k,cls)=>`<svg class="${cls||''}" viewBox="0 0 64 64" ${A}>${CI[k]||CI.bearing}</svg>`;
const ico=n=>`<svg class="ic" viewBox="0 0 24 24">${P[n]||''}</svg>`;
function paintIcons(r=document){$$('[data-i]',r).forEach(e=>{if(!e.dataset.done){e.insertAdjacentHTML('afterbegin',ico(e.dataset.i));e.dataset.done=1}})}


Object.assign(P,{
 filter:'<path d="M4 6h16M7 12h10M10 18h4"/>',sort:'<path d="M7 4v16M7 20l-3-3M7 20l3-3M17 20V4M17 4l-3 3M17 4l3 3"/>',
 check:'<path d="M5 12.5l4.5 4.5L19 7.5"/>',edit:'<path d="M4 20h4L19 9l-4-4L4 16z"/><path d="M13.5 6.5l4 4"/>',
 logout:'<path d="M9 4H5v16h4M16 8l4 4-4 4M20 12H9"/>',box:'<path d="M3 8l9-5 9 5v8l-9 5-9-5zM3 8l9 5 9-5M12 13v8"/>',
 wallet:'<rect x="3" y="6" width="18" height="13" rx="2"/><path d="M3 10h18M16 14.5h2"/>',trash:'<path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 11v6M14 11v6"/>',
 lock:'<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 018 0v3"/>',clock:'<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
 dash:'<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="5" rx="1"/><rect x="13" y="10" width="8" height="11" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/>',
 info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',gps:'<circle cx="12" cy="12" r="3"/><circle cx="12" cy="12" r="8"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3"/>',
 warn:'<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',mail:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>'});

/* ===== توابع کمکی داده ===== */
const has=(p,f)=>p.flags.includes(f),byId=id=>PRODUCTS.find(p=>p.id==id),catName=id=>(CATS.find(c=>c.id===id)||{n:''}).n;
const wprice=p=>p.wprice;
const toFa=s=>String(s==null?'':s).replace(/\d/g,d=>'۰۱۲۳۴۵۶۷۸۹'[d]);
/* تصویر محصول؛ اگر عکس نداشت پیکتوگرام */
const pic=p=>p.img?`<img src="${p.img}" alt="${esc(p.name)}" loading="lazy" draggable="false">`:svg(p.icon);
const picI=i=>i.img?`<img src="${i.img}" alt="" loading="lazy" draggable="false">`:svg(i.icon||'bearing');
const cic=c=>c.img?`<img src="${c.img}" alt="${esc(c.n)}" loading="lazy" draggable="false">`:svg(c.ic);

/* ===== ارتباط با سرور ===== */
function csrf(){const m=document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);return m?decodeURIComponent(m[1]):''}
async function api(url,data,method){
  const opt={method:method||(data?'POST':'GET'),credentials:'same-origin',headers:{'Accept':'application/json','X-CSRFToken':csrf()}};
  if(data){opt.headers['Content-Type']='application/json';opt.body=JSON.stringify(data)}
  let r,j={};try{r=await fetch(url,opt)}catch(e){throw Object.assign(new Error('ارتباط با سرور برقرار نشد'),{status:0,data:{}})}
  try{j=await r.json()}catch(e){}
  if(!r.ok||j.ok===false)throw Object.assign(new Error(j.error||'خطای سرور'),{status:r.status,data:j});
  return j}

async function apiForm(url,fd){
  const r=await fetch(url,{method:'POST',credentials:'same-origin',headers:{'Accept':'application/json','X-CSRFToken':csrf()},body:fd});
  let j={};try{j=await r.json()}catch(e){}
  if(!r.ok||j.ok===false)throw Object.assign(new Error(j.error||'خطای سرور'),{status:r.status,data:j});
  return j}
function resizeImage(file,max){return new Promise((res,rej)=>{const img=new Image(),url=URL.createObjectURL(file);
  img.onload=()=>{const k=Math.min(1,max/Math.max(img.width,img.height)),c=document.createElement('canvas');c.width=Math.round(img.width*k);c.height=Math.round(img.height*k);
    c.getContext('2d').drawImage(img,0,0,c.width,c.height);URL.revokeObjectURL(url);c.toBlob(b=>b?res(b):rej(new Error('resize')),'image/jpeg',0.86)};
  img.onerror=()=>{URL.revokeObjectURL(url);rej(new Error('bad image'))};img.src=url})}
const validNid=v=>{v=toEn(v).trim();if(!/^\d{10}$/.test(v)||/^(\d)\1{9}$/.test(v))return false;let s=0;for(let i=0;i<9;i++)s+=(+v[i])*(10-i);const r=s%11,c=+v[9];return r<2?c===r:c===11-r};

/* ===== حساب کاربر (ME از سرور می‌آید) ===== */
const AUTH={
 me:()=>ME,phone:()=>ME?ME.phone:null,
 complete:u=>!!(u&&u.complete),debt:u=>Number(u&&u.debt)||0,
 canBuy:()=>!!(ME&&ME.canBuy),
 blocked:u=>!!(u&&u.blocked)
};
const curPage=()=>location.pathname+location.search+location.hash;
function requireAuth(opts={}){const next=encodeURIComponent(curPage()),u=ME;
  if(!u){location.replace('/login/?next='+next);return false}
  if(opts.complete!==false&&!u.complete){location.replace('/register/?next='+next);return false}
  return true}

/* ===== لینک‌های صفحهٔ دسته‌بندی ===== */
function catHref(o){const h=new URLSearchParams();['list','cat','sub','group','title','terms','brand','q','find'].forEach(k=>{if(o[k])h.set(k,o[k])});return '/category/#'+h}

/* ===== toast ===== */
function toast(t){const e=$('#toast');if(!e)return;e.textContent=t;e.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('on'),2600)}

/* ===== سبد خرید ===== */
let CART=[];const KEY='yadakpakhsh_cart_v2',cartHooks=[];
CART=LS.get(KEY,[]).filter(c=>byId(c.id)).map(c=>({id:c.id,q:c.q,mode:'w'}));
const store=()=>LS.set(KEY,CART);
const cartTotal=()=>CART.reduce((a,c)=>a+wprice(byId(c.id))*c.q,0);
function debtBlock(){const u=ME;if(u&&u.complete){if(u.blocked){toast('حساب شما مسدود است و امکان خرید ندارید');return true}if(AUTH.debt(u)>0){toast('به دلیل بدهی معوق، تا تسویه حساب امکان خرید ندارید');return true}}return false}
function addCart(id,mode,q){const p=byId(id);if(!p||p.stock<1)return false;
  if(debtBlock())return false;
  if(q<p.min){q=p.min;toast('حداقل تعداد عمده '+fa(p.min)+' عدد است')}else toast('به سبد خرید اضافه شد');
  const it=CART.find(c=>c.id===id);if(it)it.q=Math.min(p.stock,it.q+q);else CART.push({id,mode:'w',q:Math.min(q,p.stock)});
  store();renderCart();syncBadges();return true}
function setQty(i,q){const c=CART[i];if(!c)return;const p=byId(c.id),lo=Math.min(p.min,p.stock);
  if(q<lo){toast('حداقل تعداد عمده '+fa(p.min)+' عدد است');q=lo}
  c.q=Math.min(q,p.stock);store();renderCart();syncBadges()}
function removeAt(i){CART.splice(i,1);store();renderCart();syncBadges()}
function clearCart(){CART=[];store();renderCart();syncBadges()}
function renderCart(){
  const n=CART.reduce((a,c)=>a+c.q,0);$$('.cnt').forEach(e=>e.textContent=fa(n));
  const ct=$('#cartCountTxt');if(ct)ct.textContent=n?fa(n)+' کالا':'';
  const body=$('#miniBody');
  if(body){if(!CART.length)body.innerHTML='<div class="emptyMsg">سبد خرید خالی است.<br>از بخش محصولات قطعه مورد نظر را اضافه کنید.</div>';
  else body.innerHTML=CART.map((c,i)=>{const p=byId(c.id),u=wprice(p);
    return `<div class="mini"><div class="rightItem">${pic(p)}<span class="rm" data-rm="${i}">×</span></div><div style="flex:1"><a class="t" href="/product/?id=${p.id}" style="display:block">${esc(p.name)}</a><small>${esc(p.model)?'کد: '+esc(p.model)+' · ':''}${esc(p.unit||'عدد')} · ${fa(u)} تومان</small><div class="pr"><div class="q"><button data-ci="${i}" data-d="-1">−</button><b>${fa(c.q)}</b><button data-ci="${i}" data-d="1">+</button></div><b>${fa(u*c.q)} <small style="display:inline">تومان</small></b></div></div></div>`}).join('');
  $('#miniTotal').textContent=fa(cartTotal())+' تومان'}
  cartHooks.forEach(f=>f())}

/* ===== کارت محصول ===== */
function card(p){
  const out=p.stock<1,u='/product/?id='+p.id;
  return `<li class="product${out?' outofstock':''}" data-id="${p.id}" data-mode="w" data-q="${p.min}">
  <span class="product-model">${esc(p.model)}</span>
  <a class="imageBox" href="${u}" aria-label="${esc(p.name)}">${pic(p)}</a>
  <div class="wholesaleNumber active"><i data-i="plus"></i> ${fa(p.min)} عدد</div>
  <div class="titleBox"><a class="title" href="${u}"><h2 class="woocommerce-loop-product__title">${esc(p.name)}</h2></a></div>
  ${out?`<div class="priceChanger stock"><span>ناموجود</span></div><div class="priceBox"><div class="nostock">—</div></div>`
   :`<div class="priceChanger single"><span class="active">قیمت عمده</span></div><div class="priceBox"></div>`}
  <div class="addToCartWithQty"><div class="buttonShow" data-add><span class="bs"></span></div>
   <div class="quantityGlobal"><div class="submit" data-add>ثبت</div><div class="plus-minus"><div class="items" data-q="1">+</div><div class="num">۱</div><div class="items" data-q="-1">−</div></div></div></div>
  </li>`}
function paintCard(el){const p=byId(el.dataset.id),box=$('.priceBox',el);
  if(p.stock<1)return;
  box.innerHTML=`<div class="main">${fa(wprice(p))}<span class="cur">تومان</span></div>`;
  $('.num',el).textContent=fa(el.dataset.q);
  const inC=CART.filter(c=>c.id==p.id).reduce((a,c)=>a+c.q,0);
  $('.bs',el).innerHTML=inC?fa(inC):ico('cart')}
function mount(el,list){el.innerHTML=list.map(card).join('');paintIcons(el);$$('li.product',el).forEach(paintCard)}
function syncBadges(){$$('li.product').forEach(paintCard)}
const matchP=t=>{t=norm(t).trim();return t?PRODUCTS.filter(p=>norm(p.name+' '+p.model+' '+p.brand+' '+catName(p.cat)).includes(t)):[]};

/* ===== اجزای مشترک صفحه: هدر، فوتر، منو، سبد کوچک ===== */
const DEFAULT_LOGO=`<svg width="46" height="46" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#FFC700"/><g fill="none" stroke="#27282A" stroke-width="4" stroke-linecap="round"><circle cx="32" cy="32" r="12"/><circle cx="32" cy="32" r="3" fill="#27282A"/><path d="M32 8v8M32 48v8M8 32h8M48 32h8M15 15l6 6M43 43l6 6M49 15l-6 6M21 43l-6 6"/></g></svg>`;
const logoHTML=()=>`${SITE.logo?`<img src="${SITE.logo}" alt="${esc(SITE.name)}" style="height:46px;width:auto;max-width:160px;object-fit:contain">`:DEFAULT_LOGO}<div><b>${esc(SITE.name)}</b><small>${esc(SITE.tagline)}</small></div>`;
const phoneParts=()=>{const p=SITE.phone||'',i=p.indexOf('-');return i>0?[toFa(p.slice(0,i+1)),toFa(p.slice(i+1))]:['',toFa(p)]};
const telHref=()=>'tel:'+(SITE.phone||'').replace(/[^\d+]/g,'');
const searchBox=ph=>`<div class="search"><div class="search-box"><input class="search-input q" type="search" placeholder="${ph}" aria-label="جستجو" autocomplete="off"><button class="search-button" data-i="search" aria-label="جستجو"></button></div><div class="datafetch"></div></div>`;
function headerHTML(){
  const u=ME,lh='/login/?next='+encodeURIComponent(curPage()),pp=phoneParts(),
   dLogin=u?`<a href="/account/" class="login">${u.photo?`<img class="av" src="${u.photo}" alt="">`:'<i data-i="user"></i>'} ${esc(u.first||'حساب من')}</a>`:`<a href="${lh}" class="login"><i data-i="user"></i> ورود | عضویت</a>`,
   mLogin=u?`<a href="/account/" class="btnGlobal gradiant">حساب من</a>`:`<a href="${lh}" class="btnGlobal gradiant">ورود | عضویت</a>`,
   tl=SITE.topLinks.map(t=>`<a href="${t.u}"><span class="image">${t.img?`<img src="${t.img}" alt="" style="width:20px;height:20px;object-fit:contain">`:`<svg class="ic" viewBox="0 0 24 24">${P[t.i]||''}</svg>`}</span>${esc(t.t)}</a>`).join('');
  return `<div class="menuHoverBlackBg"></div>
<header class="smh" id="hdr">
  <div class="top"><div class="all"><div class="flex jb ac">
    <div class="customIcons" id="topIcons">${tl}</div>
    <div class="left"><div class="text"><span>${esc(SITE.topText)}</span></div><a href="${telHref()}" class="phoneNumber"><i data-i="call"></i><span>${pp[0]}</span>${pp[1]}</a></div>
  </div></div></div>
  <div class="justMobile"><div class="middle"><div class="all"><div class="flex jb ac">
    <div class="right" style="gap:0"><i class="menuBtn" id="ham" data-i="menu"></i><a href="/" class="logo">${logoHTML()}</a></div>
    <div class="left">${mLogin}</div>
  </div></div></div>
  <div class="mobBottom">${searchBox('جستجو')}<div class="icons"><span class="cartM" data-cartopen><i data-i="cart"></i><span class="counter cnt">۰</span></span></div></div></div>
  <div class="justDesktop">
    <div class="middle"><div class="all"><div class="flex jb ac">
      <div class="right"><a href="/" class="logo">${logoHTML()}</a>${searchBox('جستجوی نام قطعه، کد فنی یا برند...')}</div>
      <div class="left">${dLogin}<div class="cartHeader" id="cartHeader"><div class="cartBtnCircle" data-cartopen><i data-i="cart" style="display:flex"></i><span class="counter cnt">۰</span></div></div></div>
    </div></div></div>
    <div class="bottom"><div class="all"><div class="flex jb ac">
      <div id="navigation"><ul id="navul">${CATS.map(c=>`<li class="level-0 hasMega"><a href="${catHref({cat:c.id})}">${c.n}<span class="dd">▾</span></a><div class="mega"><div class="l1list">${c.g.map(([t,items],i)=>`<div class="l1${i===0?' is_hovered':''}"><a class="a" href="${catHref({cat:c.id,group:t})}">${t}<i>${ico('left')}</i></a><ul class="sub">${items.map(x=>`<li><a href="${catHref({cat:c.id,sub:x})}">${x}</a></li>`).join('')}</ul></div>`).join('')}</div></div></li>`).join('')}<li class="level-0"><a href="/#brands">برندها</a></li><li class="level-0"><a href="/blog/">مقالات</a></li><li class="level-0"><a href="/contact/">تماس با ما</a></li></ul></div>
      <a href="/guide/" class="help"><i data-i="question"></i>راهنمای خرید</a>
    </div></div></div>
  </div>
</header>`}
function footerHTML(){const pp=phoneParts();return `<footer id="contact">
  <div class="all"><div class="top">
    <div class="address"><i data-i="location"></i><div><div class="item"><b>آدرس فروشگاه مرکزی:</b><span>${esc(SITE.address)}</span></div></div></div>
    <div class="phone"><div><p>${esc(SITE.phoneFooterText)}</p><a href="${telHref()}" class="phoneNumber dark" style="color:var(--blackBoldText)"><i data-i="call"></i><span style="color:var(--grayIcon)">${pp[0]}</span>${pp[1]}</a></div></div>
  </div>
  <div class="middle">
    ${SITE.footer.map(c=>`<div class="box"><div class="boxTitleGlobal">${esc(c.title)}</div><ul>${c.links.map(l=>`<li><a href="${l.u}">${esc(l.t)}</a></li>`).join('')}</ul></div>`).join('')}
    <div class="box"><div class="boxTitleGlobal">تماس با ما</div><p>تلفن: ${toFa(SITE.phone)}<br>ایمیل: ${esc(SITE.email)}<br>ساعت کاری: ${esc(SITE.hours)}</p><div class="trust"><span>نماد اعتماد</span><span>ساماندهی</span></div></div>
  </div>
  <div class="bottomLinks">${CATS.map(c=>`<a href="${catHref({cat:c.id})}">${c.n}</a>`).join('')}${BRANDS.slice(0,3).map(b=>`<a href="${catHref({brand:b})}">${esc(b)}</a>`).join('')}</div></div>
  <div class="copy"><div class="all"><div class="copyRight">
    <p>© تمامی حقوق برای <span>${esc(SITE.copyright||SITE.name)}</span> محفوظ است.</p>
    <div class="socialGlobal">${SITE.instagram?`<a href="${SITE.instagram}" target="_blank" rel="noopener" aria-label="اینستاگرام" data-i="instagram"></a>`:''}${SITE.telegram?`<a href="${SITE.telegram}" target="_blank" rel="noopener" aria-label="تلگرام" data-i="telegram"></a>`:''}<a href="/contact/" aria-label="ایمیل" data-i="email"></a></div>
  </div></div></div>
</footer>`}
function extrasHTML(){const u=ME;return `
<nav class="bottomNavigation"><a class="item" href="/"><i data-i="home"></i>خانه</a><a class="item" id="bnCats"><i data-i="menu"></i>دسته‌بندی</a><a class="item" data-cartopen><i data-i="cart"></i>سبد خرید<span class="counter cnt" style="top:4px;right:calc(50% - 22px)">۰</span></a><a class="item" href="${u?'/account/':'/login/?next='+encodeURIComponent(curPage())}"><i data-i="user"></i>${u?'حساب من':'ورود'}</a></nav>
<div class="quickCart" id="quickCart" role="dialog" aria-label="سبد خرید"><div class="topSection"><b>سبد خرید</b><span id="cartCountTxt"></span><button class="btnGlobal" data-cartopen>بستن</button></div><div id="miniBody"></div><div class="bottomSection"><div class="tot"><span>جمع سبد خرید</span><b id="miniTotal">۰ تومان</b></div><button class="btnGlobal" id="checkout">مشاهده سبد و ثبت سفارش</button></div></div>
<div class="blackbg" id="bb"></div>
<div class="nav-drill" id="drill"><i class="x" data-i="close" id="drillX"></i><div class="parent"><ul id="drillUl">${CATS.map(c=>`<li><div class="a"><span>${c.n}</span><i>${ico('down')}</i></div><div class="in"><a href="${catHref({cat:c.id})}"><b>همهٔ ${c.n}</b></a>${c.g.flatMap(g=>g[1]).map(x=>`<a href="${catHref({cat:c.id,sub:x})}">${x}</a>`).join('')}</div></li>`).join('')}<li><a class="pl" href="/blog/">مقالات آموزشی</a></li><li><a class="pl" href="/guide/">راهنمای خرید</a></li><li><a class="pl" href="/contact/">تماس با ما</a></li><li><a class="pl" href="/about/">درباره ما</a></li></ul></div></div>
<div class="toast" id="toast"></div>`}

document.body.insertAdjacentHTML('afterbegin',headerHTML());
const _main=$('main');if(_main)_main.insertAdjacentHTML('afterend',footerHTML());
document.body.insertAdjacentHTML('beforeend',extrasHTML());
const qc=$('#quickCart');

/* منو فقط با حرکت واقعی ماوس باز می‌شود، نه با اسکرول زیر ماوس */
let lastScroll=0;
const closeMega=()=>{$$('#navul li.hasMega.open').forEach(x=>x.classList.remove('open'));document.body.classList.remove('menuHover')};
addEventListener('scroll',()=>{lastScroll=Date.now();closeMega()},{passive:true});
$$('#navul li.hasMega').forEach(l0=>{
  l0.addEventListener('mousemove',e=>{if(!e.isTrusted||Date.now()-lastScroll<400||(!e.movementX&&!e.movementY)||l0.classList.contains('open'))return;closeMega();l0.classList.add('open');document.body.classList.add('menuHover');$$('.l1',l0).forEach((x,i)=>x.classList.toggle('is_hovered',i===0))});
  l0.addEventListener('mouseleave',closeMega);
  $$('.l1',l0).forEach(l1=>l1.addEventListener('mouseenter',()=>{$$('.l1',l0).forEach(x=>x.classList.toggle('is_hovered',x===l1))}))});
const topbar=$('header .top');const setSticky=()=>{$('#hdr').style.top=-(topbar.offsetHeight)+'px'};setSticky();addEventListener('resize',setSticky);addEventListener('load',setSticky);

/* منوی موبایل */
$('#drillUl').addEventListener('click',e=>{const a=e.target.closest('.a');if(a)a.parentElement.classList.toggle('on')});
function openDrill(){$('#drill').classList.add('on');$('#bb').classList.add('on')}
function closeDrill(){$('#drill').classList.remove('on');$('#bb').classList.remove('on')}
$('#ham').onclick=openDrill;$('#bnCats').onclick=openDrill;$('#drillX').onclick=closeDrill;$('#bb').onclick=closeDrill;
addEventListener('keydown',e=>{if(e.key==='Escape'){closeDrill();qc.classList.remove('open')}});

/* سبد کوچک */
$('#miniBody').addEventListener('click',e=>{const b=e.target.closest('[data-rm],[data-ci]');if(!b)return;
  if(b.dataset.rm!==undefined)removeAt(+b.dataset.rm);else{const c=CART[+b.dataset.ci];setQty(+b.dataset.ci,c.q+ +b.dataset.d)}});
function placeCart(){if(innerWidth>1050){const r=$('.cartBtnCircle').getBoundingClientRect(),w=qc.offsetWidth;qc.style.top=(r.bottom+10)+'px';qc.style.left=Math.max(12,Math.min(r.left,innerWidth-w-12))+'px'}else{qc.style.top='';qc.style.left=''}}
document.addEventListener('click',e=>{const o=e.target.closest('[data-cartopen]');if(o){e.preventDefault();placeCart();qc.classList.toggle('open');return}
  if(!e.composedPath().includes(qc))qc.classList.remove('open')});
$('#checkout').onclick=()=>{if(!CART.length){toast('سبد خرید خالی است');return}location.href='/cart/'};

/* کارت‌ها: تعداد و افزودن */
document.addEventListener('click',e=>{const li=e.target.closest('li.product');if(!li)return;const p=byId(li.dataset.id);
  const q=e.target.closest('.items[data-q]');if(q){let v=+li.dataset.q+ +q.dataset.q;const lo=Math.min(p.min,p.stock);v=Math.max(lo,Math.min(v,p.stock));li.dataset.q=v;paintCard(li);return}
  if(e.target.closest('[data-add]'))addCart(p.id,li.dataset.mode,+li.dataset.q)});

/* جستجو: پیشنهاد سریع → صفحهٔ کالا؛ Enter → نتایج در صفحهٔ دسته‌بندی */
$$('.search').forEach(s=>{const inp=$('.q',s),dd=$('.datafetch',s),btn=$('.search-button',s);
  inp.addEventListener('input',()=>{if(!inp.value.trim()){dd.classList.remove('on');return}const r=matchP(inp.value);
    dd.innerHTML=r.length?r.slice(0,6).map(p=>`<a class="search-item" href="/product/?id=${p.id}"><div class="si">${pic(p)}</div><div class="content">${esc(p.name)}<small>${esc(p.brand)} · ${esc(p.model)} · ${fa(wprice(p))} تومان</small></div></a>`).join(''):'<div class="empty">قطعه‌ای با این نام پیدا نشد.</div>';dd.classList.add('on')});
  const go=()=>{dd.classList.remove('on');const q=inp.value.trim();if(q)location.href=catHref({q})};
  btn.onclick=go;inp.addEventListener('keydown',e=>{if(e.key==='Enter')go()})});
document.addEventListener('click',e=>{if(!e.target.closest('.search'))$$('.datafetch').forEach(d=>d.classList.remove('on'))});

/* ===== نقشهٔ ایران =====
   اگر در assets/config.js کلید نشان (neshanKey) بگذارید، نقشهٔ «نشان» نمایش داده می‌شود؛
   در غیر این‌صورت نقشهٔ OpenStreetMap که روی محدودهٔ ایران قفل شده است. ===== */
const CFG=window.YP_CONFIG||{};
const IRAN={center:[32.4279,53.688],zoom:5,minZoom:5,maxZoom:18,bounds:[[24,43.5],[40.5,64]]};
const BLANK_TILE='data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7';
function loadScript(src){return new Promise((res,rej)=>{const s=document.createElement('script');s.src=src;s.onload=res;s.onerror=rej;document.head.appendChild(s)})}
function loadCss(href){const c=document.createElement('link');c.rel='stylesheet';c.href=href;document.head.appendChild(c)}
async function loadLeaflet(){
  if(window.L)return window.L;
  const srcs=[];
  if(CFG.neshanKey)srcs.push({neshan:true,css:'https://static.neshan.org/sdk/leaflet/1.4.0/leaflet.css',js:'https://static.neshan.org/sdk/leaflet/1.4.0/leaflet.js'});
  srcs.push({css:'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.css',js:'https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js'},{css:'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',js:'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'});
  for(const s of srcs){try{
    loadCss(s.css);await Promise.race([loadScript(s.js),new Promise((_,r)=>setTimeout(r,8000))]);
    if(window.L){window.__neshan=!!s.neshan;return window.L}}catch(e){}}
  throw new Error('leaflet')}
const PIN='<svg viewBox="0 0 36 44" width="36" height="44"><path d="M18 43S3 28 3 16a15 15 0 0130 0c0 12-15 27-15 27z" fill="#FFC700" stroke="#27282A" stroke-width="2.5"/><circle cx="18" cy="16" r="5.5" fill="#27282A"/></svg>';
function mapPicker(el,{lat,lng,onPick,onFail,readonly}){
  const api={move(){}};let cur=(lat!=null&&lng!=null)?{lat:+lat,lng:+lng}:null;
  loadLeaflet().then(L=>{
    const center=cur?[cur.lat,cur.lng]:IRAN.center,zoom=cur?16:IRAN.zoom;let map;
    if(window.__neshan){map=new L.Map(el,{key:CFG.neshanKey,maptype:CFG.neshanType||'standard-day',poi:true,traffic:false,center,zoom,minZoom:IRAN.minZoom,maxZoom:IRAN.maxZoom})}
    else{map=L.map(el,{scrollWheelZoom:!readonly,minZoom:IRAN.minZoom,maxZoom:IRAN.maxZoom}).setView(center,zoom);
      L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:IRAN.maxZoom,maxNativeZoom:IRAN.maxZoom,errorTileUrl:BLANK_TILE,attribution:'© OpenStreetMap'}).addTo(map)}
    try{map.setMinZoom(IRAN.minZoom);map.setMaxZoom(IRAN.maxZoom);map.setMaxBounds(IRAN.bounds)}catch(e){}
    const icon=L.divIcon({className:'pinIc',html:PIN,iconSize:[36,44],iconAnchor:[18,44]});let mk=null;
    const put=(la,ln,pan)=>{cur={lat:+(+la).toFixed(6),lng:+(+ln).toFixed(6)};
      if(!mk){mk=L.marker([la,ln],{icon,draggable:!readonly}).addTo(map);mk.on('dragend',()=>{const q=mk.getLatLng();put(q.lat,q.lng,false)})}else mk.setLatLng([la,ln]);
      if(pan)map.setView([la,ln],Math.max(map.getZoom(),16));onPick&&onPick(cur)};
    if(cur){mk=L.marker([cur.lat,cur.lng],{icon,draggable:!readonly}).addTo(map);if(!readonly)mk.on('dragend',()=>{const q=mk.getLatLng();put(q.lat,q.lng,false)})}
    if(!readonly)map.on('click',e=>put(e.latlng.lat,e.latlng.lng,false));
    api.move=(la,ln)=>put(la,ln,true);
    setTimeout(()=>map.invalidateSize(),250);addEventListener('resize',()=>map.invalidateSize());
  }).catch(()=>{el.innerHTML='<div class="mapFail">نقشه بارگذاری نشد (اینترنت یا دسترسی به سرور نقشه). از دکمهٔ «موقعیت فعلی من» یا مختصات دستی استفاده کنید.</div>';onFail&&onFail()});
  return api}
const osmLink=(la,ln)=>`https://www.openstreetmap.org/?mlat=${la}&mlon=${ln}#map=17/${la}/${ln}`;

document.body.dataset.ready='1';
paintIcons();renderCart();

/* فلش‌های اسلایدر محصولات */
document.addEventListener('click',e=>{const b=e.target.closest('[data-sc]');if(!b)return;const el=document.getElementById(b.dataset.sc);if(el)el.scrollBy({left:b.dataset.d*el.clientWidth*.7,behavior:'smooth'})});

/* ===== نمایش بزرگ تصویر ===== */
Object.assign(P,{zoom:'<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.5-4.5M11 8v6M8 11h6"/>'});
const pdfBadge=()=>`<span class="pdfIc"><svg viewBox="0 0 30 36"><path d="M3 1h16l8 8v26H3z" fill="#e53935"/><path d="M19 1v8h8" fill="#ff8a80"/></svg><b>PDF</b></span>`;
function openLightbox(list,start){
  if(!list||!list.length)return;
  let i=start||0,zoom=false,tx=0,ty=0,drag=null,moved=false;
  const el=document.createElement('div');el.className='lightbox';
  el.innerHTML=`<button class="lbX" aria-label="بستن">×</button>${list.length>1?'<button class="lbN lbPrev" aria-label="قبلی">›</button><button class="lbN lbNext" aria-label="بعدی">‹</button>':''}<div class="lbStage"></div><div class="lbHint">برای بزرگ‌نمایی روی تصویر کلیک کنید؛ در حالت بزرگ‌شده با ماوس بکشید</div><div class="lbCount"></div>`;
  document.body.appendChild(el);document.body.classList.add('noScroll');
  const stage=$('.lbStage',el);
  const apply=()=>{const im=stage.querySelector('img');if(im){im.style.transform=zoom?`translate(${tx}px,${ty}px) scale(2.4)`:'';im.style.cursor=zoom?'grab':'zoom-in';im.style.transition=drag?'none':''}};
  function show(n){i=(n+list.length)%list.length;const it=list[i];stage.innerHTML=it.src?`<img src="${it.src}" alt="" draggable="false">`:`<div class="lbSvg">${it.html}</div>`;zoom=false;tx=ty=0;apply();$('.lbCount',el).textContent=list.length>1?fa(i+1)+' / '+fa(list.length):''}
  function close(){document.removeEventListener('keydown',key);removeEventListener('mouseup',up);removeEventListener('mousemove',move);el.remove();document.body.classList.remove('noScroll')}
  const key=e=>{if(e.key==='Escape')close();else if(e.key==='ArrowLeft')show(i+1);else if(e.key==='ArrowRight')show(i-1)};
  const move=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;if(Math.abs(dx)+Math.abs(dy)>4)moved=true;if(zoom){tx=drag.tx+dx/2.4;ty=drag.ty+dy/2.4;apply()}};
  const up=()=>{drag=null;apply()};
  document.addEventListener('keydown',key);addEventListener('mouseup',up);addEventListener('mousemove',move);
  el.addEventListener('mousedown',e=>{if(e.target.closest('.lbStage img')){drag={x:e.clientX,y:e.clientY,tx,ty};moved=false;e.preventDefault()}});
  el.addEventListener('click',e=>{
    if(e.target.closest('.lbX'))return close();
    if(e.target.closest('.lbPrev'))return show(i-1);
    if(e.target.closest('.lbNext'))return show(i+1);
    if(e.target.closest('.lbStage img')){if(!moved){zoom=!zoom;if(!zoom)tx=ty=0;apply()}moved=false;return}
    if(e.target.closest('.lbSvg'))return;
    close()});
  show(i)}

/* ===== کشیدن با ماوس برای عناصر افقی که از صفحه بیرون می‌زنند ===== */
(function(){
  let el=null,sx=0,sl=0,moved=false;
  const scroller=t=>{while(t&&t!==document.body&&t.nodeType===1){const cs=getComputedStyle(t);if(/(auto|scroll)/.test(cs.overflowX)&&t.scrollWidth>t.clientWidth+2)return t;t=t.parentElement}return null};
  document.addEventListener('mousedown',e=>{moved=false;if(e.button!==0||e.target.closest('input,textarea,select,[contenteditable],.lightbox'))return;const s=scroller(e.target);if(!s)return;el=s;sx=e.clientX;sl=s.scrollLeft});
  addEventListener('mousemove',e=>{if(!el)return;const dx=e.clientX-sx;if(!moved&&Math.abs(dx)>6){moved=true;el.classList.add('dragging')}if(moved){el.scrollLeft=sl-dx;e.preventDefault()}});
  addEventListener('mouseup',()=>{if(el){el.classList.remove('dragging');el=null}});
  document.addEventListener('click',e=>{if(moved){e.preventDefault();e.stopPropagation();moved=false}},true);
  document.addEventListener('dragstart',e=>{if(e.target.closest&&e.target.closest('a,img'))e.preventDefault()});
})();
