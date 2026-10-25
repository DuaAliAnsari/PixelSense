"""All CSS for PixelSense (kept apart so app.py stays readable)."""
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
:root{--brand:#5B4FD6;--deep:#3A2FA0;--ink:#1F2140;--muted:#6B6F8C;--line:#E7E8F2;--bg:#F5F6FB}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#E9EAF4!important;color:#1F2140!important;
  font-family:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',Roboto,sans-serif!important}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important}
.block-container,[data-testid="stMainBlockContainer"]{height:auto!important;flex:0 0 auto!important;align-self:flex-start!important;width:100%!important;margin:0 auto!important;min-height:100vh;max-width:480px!important;padding:0 24px 128px!important;background:#F5F6FB;
  min-height:100vh;box-shadow:0 0 0 1px #DDDEEC,0 24px 60px rgba(40,35,100,.12)}
[data-testid="stVerticalBlock"]{gap:.7rem}
[data-testid="stVerticalBlock"]>[data-testid="stElementContainer"],[data-testid="stElementContainer"]:has(.stButton),
.stButton,[data-testid="stButton"],[data-testid="stToggle"],[data-testid="stCheckbox"],[data-testid="stRadio"]{width:100%!important;max-width:100%!important}
[data-testid="stColumn"]>[data-testid="stVerticalBlock"]>[data-testid="stElementContainer"]{width:100%!important}
[data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:10px!important}
[data-testid="stColumn"],[data-testid="column"]{min-width:0!important}
[data-testid="stMarkdownContainer"]{margin-bottom:0!important}
[data-testid="stMarkdownContainer"] p{color:#1F2140;margin:0}
*{-webkit-tap-highlight-color:transparent}

/* ---------- inputs: the visible box is the baseweb wrapper, with a fixed height in every browser ---------- */
[data-testid="stTextInput"] [data-baseweb="input"]{background-color:#fff!important;border-radius:16px!important;
  border:1.5px solid #E7E8F2!important;height:54px!important;min-height:54px!important;overflow:hidden!important;box-shadow:0 6px 18px rgba(31,33,64,.08);
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236B6F8C' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='6.5'/%3E%3Cpath d='m20 20-4-4'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:16px center;background-size:20px}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within{border-color:#5B4FD6!important;box-shadow:0 0 0 3px rgba(91,79,214,.2)}
[data-testid="stTextInput"] [data-baseweb="base-input"]{background:transparent!important;border:0!important;height:100%!important;min-height:0!important}
[data-testid="stTextInput"] input{color:#1F2140!important;-webkit-text-fill-color:#1F2140!important;background:transparent!important;
  font-size:15px;font-weight:500;height:100%!important;padding:0 16px 0 46px!important;caret-color:#5B4FD6;box-sizing:border-box}
[data-testid="stTextInput"] input::placeholder{color:#8A8EA8!important;-webkit-text-fill-color:#8A8EA8!important;opacity:1}
[data-testid="stTextInput"] label p{color:#1F2140!important;font-weight:600}
[data-testid="InputInstructions"]{display:none!important}
[class*="st-key-nc_name"] input,[class*="st-key-nc_new"] input{padding-left:14px!important}
[class*="st-key-nc_name"] [data-baseweb="input"],[class*="st-key-nc_new"] [data-baseweb="input"]{background-image:none!important}

/* ---------- buttons ---------- */
.stButton>button{width:100%;min-height:48px;border-radius:14px;border:1.5px solid #E7E8F2;background:#fff;color:#1F2140;
  font-weight:700;font-size:14.5px;font-family:inherit;box-shadow:0 1px 2px rgba(31,33,64,.04);
  transition:transform .12s,box-shadow .12s,background .12s}
.stButton>button:hover{border-color:#CFCBF5;background:#FAF9FF;color:#5B4FD6}
.stButton>button:active{transform:scale(.98)}
.stButton>button p{color:inherit!important;margin:0}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,#6A5CF0,#4B3FC7)!important;border:none!important;color:#fff!important;
  box-shadow:0 8px 20px rgba(91,79,214,.32)}
.stButton>button[kind="primary"]:hover,.stButton>button[data-testid="stBaseButton-primary"]:hover{filter:brightness(1.07);color:#fff!important}
.stButton>button:focus-visible{outline:3px solid rgba(91,79,214,.45);outline-offset:2px}
[class*="st-key-back"] button{width:44px;height:44px;min-height:44px;padding:0;border-radius:50%;font-size:20px;
  box-shadow:0 4px 12px rgba(31,33,64,.08)}
[class*="st-key-link"] button{margin-top:6px;background:none!important;border:none!important;box-shadow:none!important;color:#5B4FD6!important;
  font-weight:700;min-height:28px;padding:0;justify-content:flex-end;font-size:13.5px}
[class*="st-key-sm_"] button{min-height:38px;border-radius:999px;font-size:13px;padding:0 14px}
[class*="st-key-danger"] button{color:#C2334D;border-color:#F3C9D1}
[class*="st-key-danger"] button:hover{background:#FFF5F7;color:#C2334D;border-color:#E8A3B0}
[class*="st-key-plain"] button{background:none!important;border:none!important;box-shadow:none!important;color:#6B6F8C!important;min-height:36px}

/* ---------- filter chips (horizontal scroll) ---------- */
[class*="st-key-chips"] [data-testid="stHorizontalBlock"]{overflow-x:auto;gap:8px!important;padding:2px 24px 8px;margin:0 -24px;
  width:calc(100% + 48px)!important;max-width:none!important;scrollbar-width:none}
[class*="st-key-chips"] [data-testid="stHorizontalBlock"]::-webkit-scrollbar{display:none}
[class*="st-key-chips"] [data-testid="stColumn"],[class*="st-key-chips"] [data-testid="column"]{flex:0 0 auto!important;
  width:auto!important;min-width:max-content!important}
[class*="st-key-chips"] .stButton>button{min-height:38px;padding:0 16px;border-radius:999px;font-size:13px;white-space:nowrap;width:auto}

/* ---------- whole-card tap target: invisible button stretched over the card ---------- */
[class*="st-key-tap_"]{position:relative}
[class*="st-key-tap_"] [data-testid="stElementContainer"]:has(button),[class*="st-key-tap_"] .element-container:has(button){
  position:absolute!important;inset:0;z-index:5;width:100%!important;height:100%!important;margin:0!important}
[class*="st-key-tap_"] .stButton{height:100%}
[class*="st-key-tap_"] .stButton>button{width:100%;height:100%;opacity:0;border-radius:20px;cursor:pointer}
.pressable{transition:transform .12s ease}
[class*="st-key-tap_"]:active .pressable{transform:scale(.985)}

/* ---------- bottom navigation + sticky action bar ---------- */
.st-key-navbar,.st-key-actionbar{position:fixed!important;bottom:0;left:50%;transform:translateX(-50%);width:min(100vw,480px);
  z-index:999;background:rgba(255,255,255,.97);backdrop-filter:blur(14px);border-top:1px solid #E7E8F2;padding:0!important;gap:0!important}
.st-key-navbar [data-testid="stHorizontalBlock"]{position:absolute!important;inset:0;gap:0!important}
.st-key-navbar [data-testid="stColumn"],.st-key-navbar [data-testid="column"]{flex:1!important}
.st-key-navbar .stButton,.st-key-navbar .stButton>button{height:76px!important;width:100%!important}
.st-key-navbar .stButton>button{opacity:0;border:none;border-radius:0;box-shadow:none;background:transparent!important}
.st-key-actionbar{padding:12px 24px 16px!important}
.nav{display:grid;grid-template-columns:repeat(5,1fr);height:76px;padding:0 4px}
.ni{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;
  font-size:11px;font-weight:700;color:#7C80A0}
.ni.on{color:#5B4FD6}
.ni .bar{position:absolute;top:0;width:26px;height:3px;border-radius:0 0 4px 4px;background:#5B4FD6}
.fabc{width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#7A6CF0,#4B3FC7);display:grid;place-items:center;
  color:#fff;margin-top:-34px;box-shadow:0 12px 26px rgba(91,79,214,.45);border:4px solid #fff}
.bdg{position:absolute;top:9px;left:calc(50% + 6px);background:#E5484D;color:#fff;font-size:10px;font-weight:800;min-width:18px;
  height:18px;border-radius:9px;display:grid;place-items:center;padding:0 5px;border:2px solid #fff;box-sizing:content-box}

/* ---------- toast / snackbar ---------- */
.st-key-snack{background:#1F2140;border-radius:16px;padding:6px 6px 6px 16px!important;box-shadow:0 10px 24px rgba(31,33,64,.25);margin-top:14px}
.st-key-snack [data-testid="stHorizontalBlock"]{align-items:center}
.st-key-snack .stButton>button{background:transparent!important;border:none!important;box-shadow:none!important;
  color:#BDB5FF!important;min-height:38px;font-weight:800}
.snack-t{color:#fff!important;font-size:13.5px;font-weight:600;line-height:1.35}

/* ---------- hero ---------- */
.st-key-hero{margin:0 -24px;width:calc(100% + 48px)!important;max-width:none!important;padding:24px 24px 26px!important;background:linear-gradient(160deg,#352A9E 0%,#5B4FD6 55%,#8174F2 100%);
  border-radius:0 0 32px 32px;box-shadow:0 14px 30px rgba(75,63,199,.25);gap:.8rem!important}
.hero-top{display:flex;align-items:center;justify-content:space-between}
.brand{display:flex;align-items:center;gap:10px;color:#fff!important;font-weight:800;font-size:17px;letter-spacing:-.3px}
.logo-sm{width:34px;height:34px;border-radius:11px;background:rgba(255,255,255,.18);display:grid;place-items:center}
.chip-w{background:rgba(255,255,255,.18);color:#fff!important;font-size:12px;font-weight:700;padding:6px 12px;border-radius:999px}
.hero-h{color:#fff!important;font-size:26px;font-weight:800;letter-spacing:-.8px;line-height:1.2;margin-top:6px}
.hero-s{color:#E4E0FF!important;font-size:13.5px;line-height:1.45;margin-top:4px}

/* ---------- content ---------- */
.h1{font-size:25px;font-weight:800;letter-spacing:-.7px;line-height:1.25;color:#1F2140!important;margin-top:20px}
.sub{font-size:13.5px;color:#6B6F8C!important;line-height:1.5;margin-top:6px;padding-bottom:10px}
.sect{display:flex;justify-content:space-between;align-items:baseline;margin-top:8px}
.sect b{font-size:18px;font-weight:800;letter-spacing:-.4px;color:#1F2140}
.sect span{font-size:12.5px;color:#6B6F8C;font-weight:600}
.lbl{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#7C80A0;margin-top:2px}
.tb-title{font-size:18px;font-weight:800;letter-spacing:-.3px;color:#1F2140!important;line-height:44px}
[class*="st-key-topbar"]{margin-top:16px}
[class*="st-key-topbar"] [data-testid="stHorizontalBlock"]{align-items:center}
[class*="st-key-topbar"] .stButton,[class*="st-key-topbar"] [data-testid="stButton"]{width:44px!important;min-width:44px}
[class*="st-key-topbar"] [data-testid="stColumn"]:first-child{min-width:48px!important;flex:0 0 48px!important;width:48px!important}
.card{background:#fff;border-radius:20px;box-shadow:0 1px 2px rgba(31,33,64,.04),0 8px 24px rgba(31,33,64,.07);overflow:hidden}
.pad{padding:16px}
.pill{display:inline-flex;align-items:center;gap:5px;border-radius:999px;padding:5px 10px;font-size:11.5px;font-weight:700;
  background:#EEEBFF;color:#4A3FC2;white-space:nowrap}
.pill.warn{background:#FFF1D6;color:#8A5200}.pill.good{background:#E3F6EC;color:#0F6B49}.pill.gray{background:#EEF0F6;color:#555A75}
.pills{display:flex;flex-wrap:wrap;gap:6px}
mark{background:#E4DFFF;color:#3A2FA0;border-radius:4px;padding:0 3px;font-weight:700}

.tile{position:relative;width:100%;height:0;padding-top:75%;border-radius:16px;overflow:hidden;background:#DCDDEA;box-shadow:0 2px 8px rgba(31,33,64,.10)}
.tile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block}
.tdot{position:absolute;top:7px;right:7px;width:13px;height:13px;border-radius:50%;background:#F5A524;border:2.5px solid #fff}
.tok{position:absolute;top:6px;right:6px;width:20px;height:20px;border-radius:50%;background:#18936A;display:grid;place-items:center;border:2px solid #fff}

.rcard{display:flex;gap:14px;padding:12px;align-items:stretch}
.rthumb{width:120px;min-width:120px;height:90px;border-radius:14px;object-fit:cover;display:block;background:#DCDDEA}
.rbody{flex:1;min-width:0;display:flex;flex-direction:column;gap:5px;justify-content:center}
.rtitle{font-weight:800;font-size:14.5px;letter-spacing:-.2px;color:#1F2140;line-height:1.25}
.rsnip{font-size:12.5px;color:#4D5170;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.chev{display:grid;place-items:center;color:#A5A8C0}

.ctile{border-radius:20px;padding:14px;min-height:112px;display:flex;flex-direction:column;justify-content:space-between}
.cic{width:40px;height:40px;border-radius:13px;background:rgba(255,255,255,.75);display:grid;place-items:center}
.cname{font-weight:800;font-size:15px;letter-spacing:-.2px;color:#1F2140;margin-top:10px}
.ccount{font-size:12px;color:#555A75;font-weight:600}
.banner{display:flex;gap:14px;align-items:center;padding:16px;border-radius:20px;background:linear-gradient(120deg,#FFF4DD,#FFE9C2);
  box-shadow:0 8px 22px rgba(194,122,0,.14)}
.banner .bic{width:46px;height:46px;border-radius:15px;background:#fff;display:grid;place-items:center;color:#C27A00}
.banner b{font-size:15px;font-weight:800;color:#4A3200;display:block}
.banner small{font-size:12.5px;color:#7A5A1C;line-height:1.4;display:block;margin-top:2px}
.crow{display:flex;gap:14px;align-items:center;padding:12px 14px}
.cthumb{width:76px;min-width:76px;height:57px;border-radius:15px;object-fit:cover;background:linear-gradient(135deg,#EEEBFF,#D9D3FF);display:grid;place-items:center;color:#5B4FD6;overflow:hidden}
.cthumb img{width:100%;height:100%;object-fit:cover}
.hero-img{position:relative;border-radius:24px;overflow:hidden;box-shadow:0 12px 30px rgba(31,33,64,.18);background:#DCDDEA}
.hero-img img{width:100%;display:block;aspect-ratio:4/3;max-height:380px;object-fit:contain;background:#E9EAF4}
.hero-img .pills{position:absolute;left:12px;bottom:12px}
.hero-img .pill{background:rgba(255,255,255,.95)}
.dtitle{font-size:22px;font-weight:800;letter-spacing:-.6px;line-height:1.2;color:#1F2140}
.ev{display:flex;gap:10px;align-items:flex-start;font-size:13.5px;color:#2B2E4D;line-height:1.45;padding:7px 0}
.ev i{flex:0 0 22px;height:22px;border-radius:50%;background:#E3F6EC;display:grid;place-items:center;margin-top:1px}
.found{background:#EAF8F1;border:1px solid #BFE8D3;border-radius:16px;padding:14px 16px}
.found small{font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#0F6B49}
.found div{font-size:14.5px;font-weight:600;color:#12392B;margin-top:4px;line-height:1.45}
.lcard{border-radius:20px;padding:16px}
.lcard.warn{background:#FFF7E6;border:1px solid #F7DDA8}.lcard.good{background:#fff;border:1px solid #E7E8F2;box-shadow:0 8px 24px rgba(31,33,64,.06)}
.lcard .big{font-size:20px;font-weight:800;letter-spacing:-.4px;color:#1F2140;margin:8px 0 4px}
.lcard p{font-size:12.8px;color:#6B6F8C;margin:0;line-height:1.45}
.empty{text-align:center;padding:34px 22px;background:#fff;border-radius:24px;box-shadow:0 8px 24px rgba(31,33,64,.07)}
.empty .ic{width:96px;height:96px;border-radius:50%;background:#EEEBFF;display:grid;place-items:center;margin:0 auto 16px;color:#5B4FD6}
.empty h3{font-size:19px;font-weight:800;letter-spacing:-.4px;margin:0 0 6px;color:#1F2140}
.empty p{font-size:13.5px;color:#6B6F8C;line-height:1.5;margin:0}
.progress{height:6px;border-radius:99px;background:#E3E1F7;overflow:hidden;margin-top:8px}
.progress i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#7A6CF0,#4B3FC7)}
.qrow{display:flex;align-items:center;gap:12px;padding:14px 16px;font-weight:600;font-size:14.5px;color:#1F2140}
.qrow .qi{width:36px;height:36px;border-radius:12px;background:#EEEBFF;display:grid;place-items:center;color:#5B4FD6}
.setrow{display:flex;align-items:center;gap:12px;padding:14px 16px;border-bottom:1px solid #EFF0F7}
.setrow:last-child{border-bottom:none}
.setrow b{font-size:14.5px;font-weight:800;color:#1F2140;display:block}
.setrow small{font-size:12.5px;color:#6B6F8C;line-height:1.4;display:block;margin-top:2px}
.setrow .si{flex:0 0 40px;height:40px;border-radius:13px;background:#EEEBFF;display:grid;place-items:center;color:#5B4FD6}
.setrow .si.off{background:#EEF0F6;color:#6B6F8C}
.info p{font-size:13.5px;color:#3B3E5E;line-height:1.55;margin:0 0 12px}.info p:last-child{margin:0}.info b{color:#1F2140}

/* ---------- welcome ---------- */
.wel-top{margin:0 -24px;padding:54px 24px 34px;background:linear-gradient(160deg,#2F2593 0%,#5B4FD6 58%,#8A7DF5 100%);
  border-radius:0 0 40px 40px;text-align:center;box-shadow:0 18px 40px rgba(75,63,199,.28);margin-bottom:24px}
.wel-logo{width:72px;height:72px;border-radius:24px;background:#fff;margin:0 auto 14px;display:grid;place-items:center;
  box-shadow:0 14px 30px rgba(20,10,90,.35);color:#5B4FD6}
.wel-name{font-size:32px;font-weight:800;letter-spacing:-1px;color:#fff!important}
.wel-tag{font-size:15px;color:#E4E0FF!important;line-height:1.45;margin-top:6px}
.collage{position:relative;height:190px;width:360px;max-width:100%;margin:26px auto 0}
.collage img{position:absolute;width:160px;height:120px;object-fit:cover;border-radius:14px;border:4px solid #fff;box-shadow:0 14px 28px rgba(15,8,80,.4)}
.feat{display:flex;gap:14px;align-items:center;padding:6px 4px}
.feat .fi{flex:0 0 46px;height:46px;border-radius:15px;background:#EEEBFF;display:grid;place-items:center;color:#5B4FD6}
.feat b{font-size:14.5px;font-weight:800;color:#1F2140;display:block}.feat small{font-size:12.8px;color:#6B6F8C;line-height:1.4}
.steps{font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase;color:#7C80A0;margin-top:22px}
[class*="st-key-sel_"]{background:#fff;border-radius:16px;padding:14px 16px;box-shadow:0 4px 16px rgba(31,33,64,.06)}
[class*="st-key-sel_"] p{font-weight:700;font-size:14.5px}

.spin{width:84px;height:84px;border-radius:50%;border:7px solid #E3E1F7;border-top-color:#5B4FD6;margin:34px auto 18px;animation:sp 1s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.stepi{display:flex;align-items:center;gap:12px;padding:13px 16px;border-bottom:1px solid #EFF0F7;font-weight:700;font-size:14.5px}
.stepi:last-child{border:none}.stepi em{margin-left:auto;font-style:normal;font-size:12.5px;font-weight:700;color:#8A8EA8}
.stepi.done em{color:#0F6B49}.stepi.run em{color:#5B4FD6}

/* ---------- dialogs ---------- */
div[data-testid="stDialog"] div[role="dialog"]{border-radius:26px!important;background:#fff!important}
div[data-testid="stDialog"] *{color:#1F2140}
div[data-testid="stDialog"] button[kind="primary"] *,div[data-testid="stDialog"] button[data-testid="stBaseButton-primary"] *{color:#fff!important}
[data-testid="stRadio"] [role="radiogroup"]{gap:8px}
[data-testid="stRadio"] label{background:#fff;border:1.5px solid #E7E8F2;border-radius:14px;padding:11px 14px;width:100%}
[data-testid="stRadio"] label:has(input:checked){border-color:#5B4FD6;background:#F3F1FF}
[data-testid="stRadio"] label p{font-weight:600}

/* ---------- fit the screen + alignment ---------- */
html,body{overflow-x:hidden!important}
.block-container,[data-testid="stMainBlockContainer"]{min-height:100dvh!important;box-sizing:border-box!important;overflow-x:clip;
  padding-bottom:calc(120px + env(safe-area-inset-bottom))!important}
@media (max-width:480px){.block-container,[data-testid="stMainBlockContainer"]{box-shadow:none!important}}
[data-testid="stHorizontalBlock"]{align-items:stretch}
.st-key-navbar,.st-key-actionbar{padding-bottom:env(safe-area-inset-bottom)!important}
.card,.ctile,.empty,.found,.lcard,.banner{box-sizing:border-box;width:100%}
.ctile{height:128px;min-height:0!important}
.cname,.rtitle,.dtitle,.ccount,.setrow b,.setrow small{overflow-wrap:anywhere}
[class*="st-key-row_"]{background:#fff;border-radius:16px;padding:8px 12px!important;box-shadow:0 4px 16px rgba(31,33,64,.06)}
[class*="st-key-row_"] [data-testid="stHorizontalBlock"]{align-items:center!important}
[class*="st-key-sm_"] button{width:100%}
.upc{display:flex;gap:14px;align-items:center;padding:12px 14px}
.dbadge{flex:0 0 52px;height:52px;border-radius:14px;background:#EEEBFF;color:#4A3FC2;display:flex;flex-direction:column;
  align-items:center;justify-content:center;line-height:1}
.dbadge b{font-size:18px;font-weight:800}.dbadge span{font-size:10px;font-weight:800;letter-spacing:.06em;margin-top:3px}
.dbadge.urgent{background:#FFF1D6;color:#8A5200}
div[data-testid="stDialog"] div[role="dialog"]{max-width:min(92vw,460px)!important}

/* =====================  V3: app bar, corner menu, bottom prompt bar, chat, people  ===================== */
.st-key-appbar{margin-top:14px;margin-bottom:2px}
.st-key-appbar [data-testid="stHorizontalBlock"]{align-items:center}
.st-key-appbar [data-testid="stColumn"]:first-child,.st-key-appbar [data-testid="stColumn"]:last-child{flex:0 0 48px!important;width:48px!important;min-width:48px!important}
.ab-title{text-align:center;font-weight:800;font-size:17px;letter-spacing:-.3px;color:#1F2140;line-height:44px}
.ibtn{width:44px;height:44px;border-radius:50%;background:#fff;display:grid;place-items:center;color:#1F2140;box-shadow:0 4px 12px rgba(31,33,64,.08)}
[class*="st-key-tap_menu"] .stButton>button,[class*="st-key-tap_newchat"] .stButton>button,[class*="st-key-tap_plus"] .stButton>button,[class*="st-key-tap_send"] .stButton>button{border-radius:50%}
.st-key-scrim,.st-key-plus_scrim{position:fixed!important;inset:0;z-index:1000;background:rgba(24,20,60,.42);padding:0!important;gap:0!important;width:100vw!important;height:100vh!important;max-width:none!important}
.st-key-plus_scrim{background:transparent;z-index:996}
.st-key-scrim [data-testid="stElementContainer"],.st-key-plus_scrim [data-testid="stElementContainer"]{position:absolute!important;inset:0;width:100%!important;height:100%!important;margin:0!important}
.st-key-scrim .stButton,.st-key-plus_scrim .stButton{height:100%}
.st-key-scrim .stButton>button,.st-key-plus_scrim .stButton>button{width:100%;height:100%;opacity:0;border-radius:0;border:none}
.st-key-drawer{position:fixed!important;top:0;bottom:0;left:50%;transform:translateX(calc(-1 * min(50vw, 240px)));width:min(84vw,320px)!important;z-index:1001;
  background:#fff;padding:22px 14px!important;overflow-y:auto;box-shadow:12px 0 40px rgba(24,20,60,.25);border-radius:0 24px 24px 0;gap:.35rem!important}
.dr-head{display:flex;align-items:center;gap:12px;padding:2px 8px 18px;font-weight:800;font-size:19px;letter-spacing:-.4px;color:#1F2140}
.dr-row{display:flex;gap:14px;align-items:center;padding:13px 14px;border-radius:14px;font-weight:700;font-size:15px;color:#1F2140}
.dr-row.on{background:#EEEBFF;color:#4A3FC2}
.dr-row small{margin-left:auto;font-size:12px;color:#7C80A0;font-weight:700}
.dr-note{font-size:12px;color:#8A8EA8;line-height:1.5;padding:14px 10px 0}

.st-key-composer{position:fixed!important;bottom:0;left:50%;transform:translateX(-50%);width:min(100vw,480px)!important;z-index:995;
  padding:12px 14px calc(14px + env(safe-area-inset-bottom))!important;background:linear-gradient(to top,#F5F6FB 74%,rgba(245,246,251,0));gap:0!important}
.st-key-composer [data-testid="stHorizontalBlock"]{align-items:center!important;gap:8px!important}
.st-key-composer [data-testid="stColumn"]:first-child,.st-key-composer [data-testid="stColumn"]:last-child{flex:0 0 46px!important;width:46px!important;min-width:46px!important}
.cbtn{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;background:#fff;color:#4A3FC2;box-shadow:0 4px 14px rgba(31,33,64,.14)}
.cbtn.send{background:linear-gradient(135deg,#6A5CF0,#4B3FC7);color:#fff;box-shadow:0 8px 20px rgba(91,79,214,.35)}
.st-key-composer_q [data-baseweb="input"]{height:48px!important;min-height:48px!important;border-radius:24px!important;background-image:none!important;
  box-shadow:0 6px 18px rgba(31,33,64,.14)!important;overflow:hidden!important}
.st-key-composer_q input{padding-left:18px!important}
.st-key-plussheet{position:fixed!important;bottom:84px;left:50%;transform:translateX(calc(-1 * min(50vw, 240px) + 14px));width:min(76vw,300px)!important;z-index:997;
  background:#fff;border-radius:20px;padding:8px!important;box-shadow:0 18px 44px rgba(24,20,60,.28);gap:2px!important}
.pl-row{display:flex;gap:12px;align-items:center;padding:12px 12px;border-radius:14px;font-weight:700;font-size:14.5px;color:#1F2140}
.pl-row i{width:34px;height:34px;border-radius:11px;background:#EEEBFF;color:#5B4FD6;display:grid;place-items:center;font-style:normal}
.pl-row small{display:block;font-size:11.5px;font-weight:600;color:#7C80A0;margin-top:1px}

.msg-u{display:flex;justify-content:flex-end;margin-top:8px}
.bub-u{max-width:84%;background:linear-gradient(135deg,#6A5CF0,#4B3FC7);color:#fff;padding:12px 16px;border-radius:20px 20px 6px 20px;
  font-size:14.5px;font-weight:600;line-height:1.45;overflow-wrap:anywhere}
.msg-a{display:flex;gap:10px;align-items:flex-start;margin-top:8px}
.av-ai{flex:0 0 34px;height:34px;border-radius:12px;background:linear-gradient(135deg,#6A5CF0,#4B3FC7);display:grid;place-items:center}
.bub-a{background:#fff;border-radius:6px 20px 20px 20px;padding:13px 16px;font-size:14.5px;line-height:1.55;color:#1F2140;
  box-shadow:0 2px 10px rgba(31,33,64,.07);overflow-wrap:anywhere;max-width:calc(100% - 44px)}
.bub-a b{font-weight:800}
.bub-a small{display:block;margin-top:6px;color:#6B6F8C;font-size:12.5px}
details.how{margin:-2px 0 0 44px;font-size:12.8px;color:#555A75}
details.how summary{cursor:pointer;font-weight:700;color:#5B4FD6;padding:4px 0}
details.how ol{margin:6px 0 4px;padding-left:18px;line-height:1.55}
.src{display:flex;gap:12px;align-items:center;padding:10px 12px}
.src .rthumb{width:84px;min-width:84px;height:63px}
.indent{margin-left:44px}
.more{font-size:12.5px;color:#6B6F8C;font-weight:600;margin:0 0 0 44px}

.pav{border-radius:50%;object-fit:cover;background:#DCDDEA;display:block}
.ptile{display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;padding:8px 0 6px}
.ptile .pav{width:84px;height:84px;box-shadow:0 6px 16px rgba(31,33,64,.16);border:3px solid #fff}
.ptile.sm .pav{width:60px;height:60px}
.ptile.sm{gap:4px;padding:2px 0}
.pname{font-weight:800;font-size:13.5px;color:#1F2140;overflow-wrap:anywhere}
.pname.un{color:#5B4FD6}
.pcount{font-size:12px;color:#6B6F8C;font-weight:600;margin-top:-3px}
.phero{display:flex;flex-direction:column;align-items:center;text-align:center;gap:6px;padding:6px 0 2px}
.phero .pav{width:112px;height:112px;border:4px solid #fff;box-shadow:0 12px 28px rgba(31,33,64,.2)}
.phero .pn{font-size:24px;font-weight:800;letter-spacing:-.6px;color:#1F2140}
.fchips{display:flex;gap:8px;flex-wrap:wrap}
.fchip{display:flex;align-items:center;gap:8px;padding:5px 14px 5px 5px;border-radius:999px;background:#fff;box-shadow:0 2px 10px rgba(31,33,64,.09);font-weight:700;font-size:13px;color:#1F2140}
.fchip .pav{width:34px;height:34px}
.monthh{display:flex;justify-content:space-between;align-items:baseline;margin-top:16px}
.monthh b{font-size:17px;font-weight:800;letter-spacing:-.3px;color:#1F2140}
.monthh span{font-size:12.5px;color:#6B6F8C;font-weight:600}
.greet h2{font-size:26px;font-weight:800;letter-spacing:-.8px;line-height:1.2;margin:18px 0 6px;color:#1F2140}
.greet p{font-size:14px;color:#6B6F8C;line-height:1.55;margin:0}
.heart{position:absolute;top:12px;right:12px;width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,.95);display:grid;place-items:center;color:#D6455D}
.tile .heart{top:6px;right:6px;width:24px;height:24px}
.consent{padding:18px}
.consent h3{margin:0 0 6px;font-size:18px;font-weight:800;letter-spacing:-.4px;color:#1F2140}
.consent p{margin:0 0 4px;font-size:13.5px;line-height:1.55;color:#4D5170}
.st-key-actionbar [data-testid="stColumn"]:first-child{flex:0 0 56px!important;width:56px!important;min-width:56px!important}
.st-key-favbtn button{font-size:22px;padding:0;color:#D6455D}
@media (max-width:480px){.st-key-composer,.st-key-actionbar,.st-key-navbar{width:100vw!important}}

/* =====================  V4: DESKTOP / FULL-PAGE LAYOUT  =====================
   Wide screens: full-page layout with a permanent left sidebar, centred content and multi-column grids.
   Phones (<=700px): the original single-column mobile layout, with the drawer menu. */
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#F5F6FB!important}
.block-container,[data-testid="stMainBlockContainer"]{max-width:1240px!important;padding:20px 40px calc(150px + env(safe-area-inset-bottom))!important;
  background:transparent!important;box-shadow:none!important;min-height:100dvh}
[data-testid="stVerticalBlock"]{gap:1rem}

/* page widths per screen: reading screens stay narrower, galleries use the full width */
[class*="st-key-v_"]{width:100%;margin-left:auto!important;margin-right:auto!important}
.st-key-v_chat,.st-key-v_detail,.st-key-v_settings,.st-key-v_person{max-width:960px}
.st-key-v_welcome{max-width:1040px}
.st-key-v_analysing{max-width:560px}

/* ---------- sidebar (computers) / drawer (phones) ---------- */
.st-key-sidebar{display:none!important}
.st-key-drawer{left:0!important;transform:none!important;width:min(86vw,320px)!important}
.dr-row{transition:background .12s}
.dr-row:not(.on):hover{background:#F3F1FF}

/* ---------- prompt bar ---------- */
.st-key-composer{width:min(100vw,920px)!important;padding:16px 24px calc(20px + env(safe-area-inset-bottom))!important}
.st-key-composer [data-testid="stColumn"]:first-child,.st-key-composer [data-testid="stColumn"]:last-child{flex:0 0 52px!important;width:52px!important;min-width:52px!important}
.cbtn{width:52px;height:52px}
.st-key-composer_q [data-baseweb="input"]{height:54px!important;min-height:54px!important;border-radius:27px!important}
.st-key-composer_q input{font-size:15.5px!important;padding-left:22px!important}
.st-key-plussheet{bottom:96px;width:min(86vw,340px)!important;transform:translateX(calc(-1 * min(50vw, 460px) + 24px))}
.st-key-actionbar{width:min(100vw,780px)!important;padding:14px 24px 18px!important;border-radius:24px 24px 0 0;
  border:1px solid #E7E8F2;border-bottom:none;box-shadow:0 -12px 32px rgba(31,33,64,.08)}
.st-key-actionbar [data-testid="stHorizontalBlock"]{gap:12px!important}
div[data-testid="stDialog"] div[role="dialog"]{max-width:min(92vw,520px)!important}

/* ---------- grids ---------- */
[class*="st-key-grid6_"],[class*="st-key-grid3_"],[class*="st-key-cards3_"]{gap:18px!important}
[class*="st-key-grid6_"] [data-testid="stHorizontalBlock"],[class*="st-key-grid3_"] [data-testid="stHorizontalBlock"],
[class*="st-key-cards3_"] [data-testid="stHorizontalBlock"]{gap:18px!important}
[class*="st-key-grid3_m"]{margin-left:44px;width:calc(100% - 44px)!important}
[class*="st-key-tap_m"][class*="_src_"],[class*="st-key-tap_m"][class*="_all"]{margin-left:44px;width:calc(100% - 44px)!important;max-width:760px}
.card.crow,.card.upc{min-height:84px;height:100%}
.ctile{height:auto}
@media (hover:hover){
  [class*="st-key-tap_"]:hover .pressable{transform:translateY(-2px)}
  [class*="st-key-tap_"]:hover .tile{box-shadow:0 10px 24px rgba(31,33,64,.2)}
  [class*="st-key-tap_"]:hover .card{box-shadow:0 2px 4px rgba(31,33,64,.05),0 14px 32px rgba(31,33,64,.12)}
  [class*="st-key-tap_"]:active .pressable{transform:scale(.985)}
}
.tile{border-radius:18px}

/* ---------- chips wrap on computers instead of scrolling sideways ---------- */
@media (min-width:701px){
  [class*="st-key-chips"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;overflow:visible!important;margin:0!important;
    width:100%!important;padding:2px 0 6px!important;gap:10px!important}
  [class*="st-key-chips"] .stButton>button{min-height:42px;font-size:13.5px;padding:0 20px}
}

/* ---------- detail screen: photo on the left, information on the right ---------- */
.st-key-stack_detail [data-testid="stHorizontalBlock"]{gap:40px!important;align-items:flex-start!important}
.st-key-stack_detail [data-testid="stColumn"] [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:10px!important}
.hero-img img{max-height:520px}
.dtitle{font-size:26px}

/* ---------- welcome ---------- */
.feats{display:flex;flex-direction:column;gap:6px}
.st-key-start{max-width:380px!important;margin:6px auto 0!important}
.st-key-start .stButton>button{min-height:54px;font-size:16px}

/* ---------- buttons never stretch across a whole desktop screen ---------- */
.st-key-faces_on,[class*="st-key-danger"],.st-key-plain_notnow{max-width:380px}
.st-key-v_person [data-testid="stHorizontalBlock"]:has(.st-key-per_rename){max-width:460px;margin:0 auto}
.empty{max-width:640px;margin:20px auto}
.consent{max-width:760px}

/* ---------- computers (>=701px) ---------- */
@media (min-width:701px){
  .wel-top{margin:0 0 28px!important;border-radius:36px!important;padding:72px 32px 56px!important}
  .wel-logo{width:84px;height:84px;border-radius:28px}
  .wel-name{font-size:48px}
  .wel-tag{font-size:19px}
  .collage{height:270px;width:600px;margin-top:34px}
  .collage img{width:240px;height:180px}
  .collage img:nth-child(3){left:calc(50% - 120px)!important}
  .feats{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
  .feat{flex-direction:column;align-items:flex-start;gap:14px;background:#fff;border-radius:22px;padding:24px;box-shadow:0 8px 24px rgba(31,33,64,.07)}
  .feat b{font-size:16px;margin-bottom:4px}.feat small{font-size:13.5px}
  .greet h2{font-size:38px;margin:36px 0 10px}
  .greet p{font-size:16px;max-width:680px}
  .h1{font-size:30px}.sub{font-size:14.5px}
  .sect b{font-size:20px}
  .monthh{margin-top:22px}.monthh b{font-size:19px}
  .tb-title{font-size:24px}
  .bub-u{max-width:70%;font-size:15.5px}.bub-a{font-size:15.5px}
  .src .rthumb{width:112px;min-width:112px;height:84px}
  .rtitle{font-size:15.5px}
  .st-key-appbar{margin-bottom:10px}
  [class*="st-key-sm_"] .stButton{display:flex;justify-content:flex-end}
  [class*="st-key-sm_"] .stButton>button{width:auto!important;min-width:150px}
  .st-key-sm_forget .stButton,.st-key-sm_hist .stButton,.st-key-sm_arrive .stButton{justify-content:flex-start}
  [class*="st-key-row_"]{padding:12px 18px!important}
}

/* ---------- full desktop with sidebar (>=1000px) ---------- */
@media (min-width:1000px){
  .st-key-sidebar{display:flex!important;flex-direction:column;position:fixed!important;top:0;bottom:0;left:0;width:272px!important;max-width:272px!important;
    z-index:990;background:#fff;border-right:1px solid #E7E8F2;padding:26px 16px!important;overflow-y:auto;gap:.35rem!important;box-sizing:border-box}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar){max-width:calc(1240px + 272px)!important;padding-left:calc(272px + 40px)!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar) .st-key-composer{left:calc(50% + 136px)!important;width:min(calc(100vw - 272px),920px)!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar) .st-key-actionbar{left:calc(50% + 136px)!important;width:min(calc(100vw - 272px),780px)!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar) .st-key-plussheet{left:calc(50% + 136px)!important;
    transform:translateX(calc(-1 * min((100vw - 272px) / 2, 460px) + 24px))!important}
  .st-key-appbar [data-testid="stColumn"]:first-child{display:none!important}
  .ab-title{text-align:left;font-size:30px;letter-spacing:-.8px;line-height:48px}
}

/* ---------- tablets: fold the detail screen and the card rows ---------- */
@media (max-width:900px){
  .st-key-stack_detail [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:16px!important}
  .st-key-stack_detail [data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important}
  .st-key-stack_detail [data-testid="stColumn"] [data-testid="stColumn"]{flex:1 1 0!important;width:auto!important}
  [class*="st-key-cards3_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important}
  [class*="st-key-cards3_"] [data-testid="stColumn"]{flex:1 1 calc(50% - 10px)!important;width:calc(50% - 10px)!important}
  .feats{grid-template-columns:1fr!important}
}

/* ---------- phones (<=700px): original mobile layout ---------- */
@media (max-width:700px){
  .block-container,[data-testid="stMainBlockContainer"]{padding:0 24px calc(120px + env(safe-area-inset-bottom))!important}
  [data-testid="stVerticalBlock"]{gap:.7rem}
  [class*="st-key-grid6_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:10px!important}
  [class*="st-key-grid6_"] [data-testid="stColumn"]{flex:0 0 calc(33.333% - 7px)!important;width:calc(33.333% - 7px)!important;min-width:0!important}
  [class*="st-key-grid3_"],[class*="st-key-grid6_"],[class*="st-key-cards3_"]{gap:10px!important}
  [class*="st-key-grid3_"] [data-testid="stHorizontalBlock"]{gap:10px!important}
  [class*="st-key-grid3_m"],[class*="st-key-tap_m"][class*="_src_"],[class*="st-key-tap_m"][class*="_all"]{margin-left:0;width:100%!important}
  [class*="st-key-cards3_"] [data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important}
  .wel-top{margin:0 -24px 24px!important}
  .feat{padding:6px 4px}
}

/* =====================  V4b: welcome, Home dashboard, Clean up  ===================== */
/* welcome */
.st-key-stack_wel{background:linear-gradient(150deg,#2F2593 0%,#5B4FD6 58%,#8A7DF5 100%);border-radius:36px;padding:56px!important;
  box-shadow:0 24px 50px rgba(75,63,199,.26);margin-bottom:28px}
.st-key-stack_wel [data-testid="stHorizontalBlock"]{align-items:center!important;gap:48px!important}
.wel-brand{display:flex;align-items:center;gap:12px;color:#fff!important;font-weight:800;font-size:20px;letter-spacing:-.3px}
.wel-logo2{width:42px;height:42px;border-radius:14px;background:#fff;display:grid;place-items:center}
.wel-h{font-size:46px;font-weight:800;letter-spacing:-1.4px;line-height:1.08;color:#fff!important;margin:30px 0 14px}
.wel-p{font-size:17px;line-height:1.55;color:#E4E0FF!important;max-width:460px;margin-bottom:28px}
.wel-note{font-size:12.5px;color:#CFC9FF!important;margin-top:12px}
.st-key-start{max-width:240px!important;margin:0!important}
.st-key-start .stButton>button{background:#fff!important;color:#3A2FA0!important;box-shadow:0 12px 26px rgba(15,8,80,.3)!important}
.st-key-start .stButton>button:hover{filter:none;background:#F3F1FF!important;color:#3A2FA0!important}
.mos{display:grid;grid-template-columns:1fr 1fr 1fr;grid-template-rows:176px 176px;gap:14px}
.mos .m{border-radius:22px;overflow:hidden;box-shadow:0 14px 30px rgba(15,8,80,.35);border:4px solid rgba(255,255,255,.92);box-sizing:border-box;background:#DCDDEA}
.mos .m img{width:100%;height:100%;object-fit:cover;display:block}
.mos .a{grid-column:1/3}.mos .b{grid-column:3;grid-row:1/3}
.feat .fi{width:46px;flex:0 0 auto}

/* snack bar */
.st-key-snack{margin-top:0!important;padding:8px 8px 8px 22px!important;border-radius:18px!important}
.snack-t{font-size:14px!important;line-height:1.4}

/* Home dashboard */
.st-key-homehero{background:linear-gradient(150deg,#2F2593 0%,#5B4FD6 60%,#8A7DF5 100%);border-radius:28px;padding:34px 38px 30px!important;
  gap:.9rem!important;box-shadow:0 18px 40px rgba(75,63,199,.22)}
.hh-t{font-size:32px;font-weight:800;letter-spacing:-.9px;color:#fff!important;line-height:1.15}
.hh-s{font-size:15px;color:#E4E0FF!important;margin-top:4px}
.st-key-homehero .stButton>button{border:none;box-shadow:0 4px 12px rgba(15,8,80,.18)}
[class*="st-key-stats4_"]{gap:18px!important}
[class*="st-key-stats4_"] [data-testid="stHorizontalBlock"]{gap:18px!important}
.stat{display:flex;align-items:center;gap:16px;background:#fff;border-radius:20px;padding:18px 20px;box-shadow:0 1px 2px rgba(31,33,64,.04),0 8px 24px rgba(31,33,64,.07)}
.stat .sic{flex:0 0 46px;height:46px;border-radius:15px;background:#EEEBFF;color:#5B4FD6;display:grid;place-items:center}
.stat .sn{font-size:26px;font-weight:800;letter-spacing:-.6px;color:#1F2140;line-height:1.1}
.stat .sl{font-size:12.5px;font-weight:600;color:#6B6F8C;margin-top:2px}
.cov{background:#fff;border-radius:20px;overflow:hidden;box-shadow:0 1px 2px rgba(31,33,64,.04),0 8px 24px rgba(31,33,64,.07);height:100%}
.cov img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block;background:#DCDDEA}
.cov .cb{padding:14px 18px 16px}
.bthumbs{display:flex;gap:-6px}.bthumbs img{width:52px;height:40px;border-radius:10px;object-fit:cover;border:2px solid #fff;margin-left:-10px;box-shadow:0 2px 6px rgba(0,0,0,.12)}
[class*="st-key-link_"] button{margin-top:10px}
.sect{margin-top:14px}
[class*="st-key-cuact_"]{max-width:520px;margin:2px 0 16px}
[class*="st-key-cuact_"] [data-testid="stHorizontalBlock"]{gap:12px!important}

@media (max-width:900px){
  .st-key-stack_wel [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:28px!important}
  .st-key-stack_wel [data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important}
  .st-key-stack_wel{padding:36px!important}
  [class*="st-key-stats4_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important}
  [class*="st-key-stats4_"] [data-testid="stColumn"]{flex:1 1 calc(50% - 10px)!important;width:calc(50% - 10px)!important}
}
@media (max-width:700px){
  .st-key-stack_wel{padding:26px 22px!important;border-radius:28px}
  .wel-h{font-size:32px}.wel-p{font-size:15px}
  .mos{grid-template-rows:120px 120px}
  .st-key-homehero{padding:24px 20px 20px!important}
  .hh-t{font-size:25px}
  .bthumbs{display:none}
  [class*="st-key-stats4_"] [data-testid="stHorizontalBlock"]{gap:10px!important}
}

/* =====================  V4c: photo editor  ===================== */
.st-key-stack_edit [data-testid="stHorizontalBlock"]{gap:40px!important;align-items:flex-start!important}
.st-key-stack_edit [data-testid="stColumn"] [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:14px!important}
.edprev img{width:100%;max-height:560px;object-fit:contain;display:block;border-radius:22px;background:#E9EAF4;box-shadow:0 12px 30px rgba(31,33,64,.16)}
.st-key-stack_edit [data-baseweb="tab-list"]{gap:6px}
.st-key-stack_edit [data-baseweb="tab"]{font-weight:700;font-size:14px;padding:10px 14px}
.stDownloadButton>button{width:100%;min-height:48px;border-radius:14px;border:1.5px solid #E7E8F2;background:#fff;color:#1F2140;font-weight:700;font-size:14.5px;margin-top:10px}
.stDownloadButton>button:hover{border-color:#CFCBF5;background:#FAF9FF;color:#5B4FD6}
.st-key-edact{margin-top:6px}
@media (max-width:900px){
  .st-key-stack_edit [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:16px!important}
  .st-key-stack_edit [data-testid="stColumn"]{flex:1 1 100%!important;width:100%!important}
  .st-key-stack_edit [data-testid="stColumn"] [data-testid="stColumn"]{flex:1 1 0!important;width:auto!important}
}
"""
