"""All CSS for PixelSense (kept apart so app.py stays readable)."""
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{--brand:#5B4FD6;--deep:#3A2FA0;--ink:#1F2140;--muted:#6B6F8C;--line:#E7E8F2;--bg:#F5F6FB}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:#E9EAF4!important;color:#1F2140!important;
  font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Inter',system-ui,'Segoe UI',Roboto,sans-serif!important}
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

/* =====================  app bar, corner menu, bottom prompt bar, chat, people  ===================== */
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

/* =====================  DESKTOP / FULL-PAGE LAYOUT  =====================
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
.st-key-btn_faces_on,.st-key-plain_notnow{max-width:380px}
[class*="st-key-danger"] .stButton{display:flex;justify-content:flex-start}
[class*="st-key-danger"] .stButton>button{width:auto!important;min-width:180px}
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
  [class*="st-key-sm_"] .stButton{display:flex;justify-content:flex-start}
  [class*="st-key-sm_"] .stButton>button{width:auto!important;min-width:150px}
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

/* =====================  welcome, Home dashboard, Clean up  ===================== */
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

/* =====================  photo editor  ===================== */
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


GLASS = r"""
/* =====================================================================================================
   LIQUID GLASS DESIGN SYSTEM
   Four ideas, taken from Apple's Liquid Glass language, applied here:
   1. MATERIAL   translucent, blurred layers that let content and colour show through (glass), never flat grey boxes.
   2. SHAPE      large, continuous rounded corners that NEST: inner radius = outer radius - padding (concentric).
   3. TYPE       one family (SF Pro on Apple devices, Inter elsewhere), a clear scale, weights 500-700, tight tracking on titles.
   4. SPACE      an 8-point grid (4/8/12/16/24/32). Navigation FLOATS above content so the photos stay the hero.
   ===================================================================================================== */
:root{
  --sp-1:4px;--sp-2:8px;--sp-3:12px;--sp-4:16px;--sp-5:24px;--sp-6:32px;
  --r-sm:14px;--r-md:20px;--r-lg:28px;--r-xl:36px;--r-pill:999px;
  --glass:rgba(255,255,255,.56);--glass-strong:rgba(255,255,255,.78);--glass-edge:rgba(255,255,255,.82);
  --glass-shadow:0 1px 0 rgba(255,255,255,.9) inset,0 12px 32px rgba(52,44,140,.12);
  --blur:blur(26px) saturate(180%);
  --ink:#1D1F3A;--muted:#636786;--accent:#5B4FD6;--accent2:#3FA9F5;
  --t-large:34px;--t-title:22px;--t-head:17px;--t-body:15px;--t-small:13px;--t-cap:12px;
}
.stApp{background:
  radial-gradient(640px 520px at 8% 6%,rgba(122,108,240,.42),transparent 70%),
  radial-gradient(620px 520px at 96% 14%,rgba(63,169,245,.34),transparent 70%),
  radial-gradient(680px 560px at 72% 100%,rgba(255,140,175,.30),transparent 70%),
  radial-gradient(520px 440px at 0% 92%,rgba(70,214,175,.26),transparent 70%),#EEF0FA!important;background-attachment:fixed!important}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:transparent!important}

/* ---- type scale ---- */
body,.stApp{font-size:var(--t-body);letter-spacing:-.011em;-webkit-font-smoothing:antialiased}
.sect b{font-size:var(--t-title);font-weight:700;letter-spacing:-.025em}
.rtitle,.ab-title,.tb-title,.empty h3{font-weight:650;letter-spacing:-.02em}
.h1,.hh-t,.wel-h{font-weight:700;letter-spacing:-.035em}
.sub,.ccount{font-size:var(--t-small);color:var(--muted)!important}
.lbl{font-weight:600;font-size:var(--t-cap)}
.dr-row,.feat b,.stat .sn{font-weight:600}
.stButton>button{font-weight:600;letter-spacing:-.01em}

/* ---- material: every surface is glass ---- */
.card,.stat,.feat,.empty,.banner,.glass,.found,.lcard,.ctile,.cov{
  background:var(--glass)!important;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);
  border:1px solid var(--glass-edge);box-shadow:var(--glass-shadow)!important;border-radius:var(--r-lg)}
.banner{background:linear-gradient(120deg,rgba(255,244,221,.72),rgba(255,226,180,.62))!important}
.tile{border-radius:var(--r-md);box-shadow:0 1px 0 rgba(255,255,255,.7) inset,0 6px 18px rgba(52,44,140,.14);border:1px solid rgba(255,255,255,.7)}
.rthumb{border-radius:var(--r-sm)}
.pill{background:rgba(255,255,255,.65);border:1px solid rgba(255,255,255,.8);backdrop-filter:blur(10px);font-weight:600}
.pill.warn{background:rgba(255,236,196,.8)}.pill.good{background:rgba(214,246,229,.85)}.pill.gray{background:rgba(238,240,248,.8)}.pill.bad{background:rgba(255,222,226,.9);color:#9B2236}
.dbadge{border-radius:var(--r-sm);background:rgba(238,235,255,.85);box-shadow:0 1px 0 rgba(255,255,255,.9) inset}
.dbadge.urgent{background:rgba(255,236,196,.9)}
.setrow .si,.feat .fi,.stat .sic,.banner .bic{border-radius:var(--r-sm);background:rgba(255,255,255,.7);box-shadow:0 1px 0 rgba(255,255,255,.9) inset}

/* ---- buttons: capsules with a specular edge ---- */
.stButton>button{border-radius:var(--r-pill);background:var(--glass-strong);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);
  border:1px solid var(--glass-edge);box-shadow:0 1px 0 rgba(255,255,255,.95) inset,0 4px 14px rgba(52,44,140,.10)}
.stButton>button:hover{background:rgba(255,255,255,.92);border-color:rgba(255,255,255,.95)}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,rgba(122,108,240,.96),rgba(75,63,199,.96))!important;border:1px solid rgba(255,255,255,.35)!important;
  box-shadow:0 1px 0 rgba(255,255,255,.45) inset,0 10px 24px rgba(91,79,214,.34)!important}
[class*="st-key-back"] button{border-radius:50%}

/* ---- inputs ---- */
[data-testid="stTextInput"] [data-baseweb="input"]{background-color:var(--glass-strong)!important;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);
  border:1px solid var(--glass-edge)!important;box-shadow:0 1px 0 rgba(255,255,255,.95) inset,0 8px 24px rgba(52,44,140,.12)!important;border-radius:var(--r-pill)!important}

/* ---- navigation FLOATS: the sidebar is an inset glass panel, the prompt bar a glass capsule ---- */
.st-key-drawer{background:var(--glass-strong)!important;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);
  border:1px solid var(--glass-edge);border-radius:0 var(--r-lg) var(--r-lg) 0!important}
.dr-row{border-radius:var(--r-md);transition:background .15s,transform .12s}
.dr-row.on{background:rgba(91,79,214,.14)!important;box-shadow:0 1px 0 rgba(255,255,255,.7) inset,0 0 0 1px rgba(91,79,214,.12) inset}
.dr-row:not(.on):hover{background:rgba(255,255,255,.6)!important}
.dr-row small{background:rgba(91,79,214,.12);color:#4A3FC2;border-radius:var(--r-pill);padding:2px 8px;font-weight:700}
.dr-row small:empty{display:none}
.dr-note{color:var(--muted)}
@media (min-width:1000px){
  .st-key-sidebar{top:var(--sp-4)!important;bottom:var(--sp-4)!important;left:var(--sp-4)!important;width:256px!important;max-width:256px!important;
    background:var(--glass)!important;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);border:1px solid var(--glass-edge)!important;
    border-radius:var(--r-xl)!important;box-shadow:var(--glass-shadow)!important;padding:var(--sp-5) var(--sp-3)!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar){padding-left:calc(256px + 16px + 40px)!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar) .st-key-composer{left:calc(50% + 136px)!important}
}
.st-key-composer{background:none!important}
.cbtn{background:var(--glass-strong);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border:1px solid var(--glass-edge);
  box-shadow:0 1px 0 rgba(255,255,255,.95) inset,0 8px 22px rgba(52,44,140,.16)}
.cbtn.send{background:linear-gradient(135deg,#7A6CF0,#4B3FC7);border-color:rgba(255,255,255,.35)}
.ibtn{background:var(--glass-strong);border:1px solid var(--glass-edge);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px)}
.st-key-plussheet{background:var(--glass-strong)!important;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);border:1px solid var(--glass-edge);border-radius:var(--r-lg)!important}
.st-key-actionbar{background:var(--glass-strong)!important;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur)}
.st-key-snack{background:rgba(29,31,58,.78)!important;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);border:1px solid rgba(255,255,255,.18);border-radius:var(--r-lg)!important}
div[data-testid="stDialog"] div[role="dialog"]{background:var(--glass-strong)!important;-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);
  border:1px solid var(--glass-edge);border-radius:var(--r-xl)!important;box-shadow:0 30px 80px rgba(40,30,120,.28)!important}

/* ---- hero panels: saturated colour under a glass sheen ---- */
.st-key-homehero,.st-key-stack_wel{border-radius:var(--r-xl)!important;
  background:linear-gradient(150deg,rgba(47,37,147,.96),rgba(91,79,214,.94) 58%,rgba(63,169,245,.86))!important;
  box-shadow:0 1px 0 rgba(255,255,255,.35) inset,0 24px 56px rgba(75,63,199,.30)!important;border:1px solid rgba(255,255,255,.28)}
.hh-t{font-size:var(--t-large)}
.st-key-why .stButton>button{background:rgba(255,255,255,.18)!important;color:#fff!important;border:1px solid rgba(255,255,255,.5)!important;box-shadow:none!important}
.st-key-why{max-width:240px!important;margin:0!important}
.st-key-start .stButton>button,.st-key-start .stButton>button[kind="primary"],.st-key-start .stButton>button[data-testid="stBaseButton-primary"]{
  background:rgba(255,255,255,.94)!important;color:#3A2FA0!important;border:1px solid #fff!important;box-shadow:0 1px 0 #fff inset,0 12px 28px rgba(15,8,80,.30)!important}
.st-key-start .stButton>button p{color:#3A2FA0!important}
[class*="st-key-chips"] .stButton>button{background:rgba(255,255,255,.22);color:#fff;border:1px solid rgba(255,255,255,.45)}
[class*="st-key-chips"] .stButton>button:hover{background:rgba(255,255,255,.4);color:#fff}
.st-key-homehero [class*="st-key-chips"] .stButton>button p{color:#fff!important}

/* ---- activity screen (analysing): glass card + glass spinner ---- */
.spin{border:6px solid rgba(255,255,255,.7);border-top-color:var(--accent);box-shadow:0 8px 30px rgba(91,79,214,.25),0 1px 0 rgba(255,255,255,.9) inset;background:var(--glass)}
.stepi{border-bottom:1px solid rgba(255,255,255,.7)}
.empty .ic{background:rgba(255,255,255,.7)}

/* ---- Needs attention ---- */
.att-hero{display:flex;align-items:center;gap:var(--sp-5);padding:var(--sp-5) var(--sp-5);flex-wrap:wrap}
.att-hero .ah-n{font-size:var(--t-large);font-weight:700;letter-spacing:-.04em;color:var(--ink);line-height:1.05}
.att-hero .ah-l{font-size:var(--t-small);color:var(--muted);margin-top:2px;max-width:220px}
.ah-sep{width:1px;align-self:stretch;background:rgba(91,79,214,.18)}
[class*="st-key-att_img"],[class*="st-key-att_m"]{background:var(--glass);-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);border:1px solid var(--glass-edge);
  border-radius:var(--r-lg);box-shadow:var(--glass-shadow);padding:var(--sp-4)!important;gap:var(--sp-3)!important}
.att-row{display:flex;gap:var(--sp-3);align-items:center}
.att-thumb{width:96px;height:72px;border-radius:var(--r-sm);object-fit:cover;flex:0 0 96px;box-shadow:0 4px 12px rgba(52,44,140,.16)}
.att-body{flex:1;min-width:0;display:flex;flex-direction:column;gap:6px}
.att-proof{font-size:var(--t-cap);color:var(--muted);line-height:1.45}
.att-proof i{color:var(--ink);background:rgba(228,223,255,.7);border-radius:6px;padding:1px 6px;font-style:normal;font-weight:500}
[class*="st-key-sm_att_"] [data-testid="stHorizontalBlock"]{gap:var(--sp-2)!important}
[class*="st-key-sm_att_"]{max-width:420px}
[class*="st-key-sm_att_"] .stButton{display:flex;justify-content:flex-start!important}
[class*="st-key-sm_att_"] .stButton>button{min-width:0!important;width:100%!important}
.calm{display:flex;flex-direction:column;gap:2px;font-size:var(--t-body)}
.calm small{color:var(--muted)}
.health{display:flex;gap:var(--sp-5);align-items:center;padding:var(--sp-4) var(--sp-5);margin-top:var(--sp-2)}

/* ---- Study mode ---- */
.st-key-studybar{position:fixed!important;top:12px;left:50%;transform:translateX(-50%);z-index:1000;width:min(720px,calc(100vw - 24px))!important;
  display:flex!important;flex-direction:row!important;flex-wrap:nowrap!important;align-items:center!important;gap:var(--sp-3)!important;padding:10px 12px 10px 20px!important;border-radius:var(--r-lg);
  background:rgba(29,31,58,.86);-webkit-backdrop-filter:var(--blur);backdrop-filter:var(--blur);border:1px solid rgba(255,255,255,.2);box-shadow:0 12px 32px rgba(20,16,70,.3)}
.st-key-studybar>div{width:auto!important;min-width:0!important}
.st-key-studybar>div:first-child{flex:1 1 0!important}
.st-key-studybar>div:last-child{flex:0 0 auto!important;width:max-content!important}
.st-key-studybar .stButton{width:max-content!important}
.sb-t span{display:block;font-size:var(--t-cap);color:rgba(255,255,255,.65);font-weight:600}
.sb-t b{display:block;color:#fff;font-size:14px;font-weight:600;line-height:1.3}
.st-key-studybar .stButton>button{min-height:40px;white-space:nowrap;width:auto;padding:0 18px}
.st-key-sm_stb .stButton>button,.st-key-sm_bl .stButton>button,.st-key-sm_addd .stButton>button,.st-key-sm_study .stButton>button{width:auto;min-width:180px}

/* ---- Why PixelSense ---- */
.about-hero{padding:var(--sp-6)}
.about-h{font-size:var(--t-large);font-weight:700;letter-spacing:-.04em;line-height:1.12;color:var(--ink);margin:var(--sp-2) 0 var(--sp-3);max-width:640px}
.about-hero p{font-size:16px;line-height:1.55;color:var(--muted);max-width:640px;margin:0}
.loop{display:grid;grid-template-columns:1fr 1fr 1.2fr;gap:var(--sp-5);margin-bottom:var(--sp-3)}
.loop span{display:block;font-size:var(--t-cap);font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#8A8EA8;margin-bottom:6px}
.loop b{font-size:var(--t-head);font-weight:650;letter-spacing:-.02em;line-height:1.3;color:var(--ink)}
.loop p{margin:0;font-size:14px;line-height:1.5;color:var(--muted)}
.loop .lp-c p{color:var(--ink)}
.loop .lp-c{border-left:3px solid rgba(91,79,214,.5);padding-left:var(--sp-4)}
@media (max-width:760px){.loop{grid-template-columns:1fr;gap:var(--sp-3)}.att-thumb{width:72px;height:56px;flex-basis:72px}.att-hero{gap:var(--sp-4)}.ah-sep{display:none}}
@media (max-width:480px){.att-thumb{display:none}}

/* ---- Your data ---- */
.dmap{display:flex;gap:var(--sp-4);align-items:flex-start;margin-bottom:var(--sp-2)}
.dmap .si{flex:0 0 40px;height:40px;border-radius:var(--r-sm);display:grid;place-items:center;color:var(--accent);background:rgba(255,255,255,.7)}
.dm-t{display:flex;justify-content:space-between;gap:var(--sp-3);align-items:baseline;flex-wrap:wrap}
.dm-t b{font-size:var(--t-head);font-weight:650;letter-spacing:-.02em}
.dm-t em{font-style:normal;font-size:var(--t-small);font-weight:600;color:var(--accent)}
.dmap p{margin:4px 0 8px;font-size:14px;line-height:1.5;color:var(--muted)}
.dm-m{font-size:var(--t-cap);color:var(--ink);line-height:1.6}
.dm-m span{font-weight:600;color:#8A8EA8;text-transform:uppercase;letter-spacing:.06em;margin-right:4px}
.st-key-sm_dl [data-testid="stDownloadButton"] button{border-radius:var(--r-pill);min-height:38px;font-weight:600;width:auto;min-width:150px}
.st-key-sm_dl [data-testid="stHorizontalBlock"]{justify-content:flex-start;gap:12px!important;flex-wrap:wrap}
.st-key-sm_dl [data-testid="stColumn"]{flex:0 0 auto!important;width:auto!important;min-width:0!important}
.st-key-sm_dl .stButton>button,.st-key-sm_dl [data-testid="stDownloadButton"] button{width:auto!important;min-width:180px}

@supports not ((backdrop-filter:blur(1px)) or (-webkit-backdrop-filter:blur(1px))){
  .card,.stat,.feat,.empty,.glass,.st-key-sidebar,.st-key-drawer,.st-key-plussheet,.st-key-actionbar,[class*="st-key-att_img"]{background:#fff!important}
}
@media (prefers-reduced-motion:reduce){*{animation-duration:.01ms!important;transition-duration:.01ms!important}}
"""
CSS = CSS + GLASS

CSS = CSS + r"""
/* ---------- v5 polish: visible outlines, readable chips, consistent spacing ---------- */
.stButton>button{background:#fff;color:#1F2140;border:1.5px solid #D5D2F3;box-shadow:0 2px 8px rgba(31,33,64,.06);font-weight:600}
.stButton>button:hover{border-color:#5B4FD6;background:#F7F6FF;color:#4B3FC7}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{border:none!important}
/* filter / suggestion chips: dark text on a solid pill, selected = brand colour */
[class*="st-key-chips"] .stButton>button{background:#fff;color:#1F2140;border:1.5px solid #D5D2F3;box-shadow:none}
[class*="st-key-chips"] .stButton>button p{color:#1F2140!important}
[class*="st-key-chips"] .stButton>button:hover{background:#F1EFFF;border-color:#5B4FD6}
[class*="st-key-chips"] .stButton>button[kind="primary"],[class*="st-key-chips"] .stButton>button[data-testid="stBaseButton-primary"]{background:linear-gradient(135deg,#6A5CF0,#4B3FC7)!important;color:#fff!important}
[class*="st-key-chips"] .stButton>button[kind="primary"] p,[class*="st-key-chips"] .stButton>button[data-testid="stBaseButton-primary"] p{color:#fff!important}
.st-key-homehero [class*="st-key-chips"] .stButton>button{background:rgba(255,255,255,.2);border:1.5px solid rgba(255,255,255,.55);color:#fff}
.st-key-homehero [class*="st-key-chips"] .stButton>button p{color:#fff!important}
.st-key-homehero [class*="st-key-chips"] .stButton>button:hover{background:rgba(255,255,255,.38)}
/* two-button action rows: same width, same height, same gap */
[class*="st-key-cuact_"] [data-testid="stHorizontalBlock"]{gap:12px!important;max-width:460px}
[class*="st-key-cuact_"] .stButton>button{min-height:46px;width:100%}
/* settings rows: action button sits at the right edge of the row */
[class*="st-key-row_"] [class*="st-key-sm_"] .stButton{justify-content:flex-end}
[class*="st-key-row_"] [class*="st-key-sm_"] .stButton>button{min-width:130px;width:auto!important}
/* face-groups consent: both buttons share one width and left edge */
.st-key-btn_faces_on,.st-key-plain_notnow{max-width:380px;margin-left:0!important}
.st-key-plain_notnow .stButton>button{background:transparent!important;border:none!important;box-shadow:none!important;color:#6B6F8C!important;font-weight:600}
.st-key-plain_notnow [data-testid="stElementContainer"],.st-key-plain_notnow{background:none!important;box-shadow:none!important;border:none!important}
/* month headings and section headings breathe */
.st-key-sm_addd .stButton{justify-content:flex-end}
.monthh{margin-top:28px;margin-bottom:2px}
.sect{margin-top:22px}

/* ---------- v6 alignment: fixed widths, one left edge ---------- */
.st-key-consent_btns{max-width:380px!important;width:100%!important;margin:0!important}
.st-key-consent_btns .stButton>button{width:100%!important;min-height:48px}
.st-key-consent_btns,.st-key-consent_btns *,.st-key-plain_notnow,.st-key-plain_notnow *{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}
.st-key-plain_notnow,.st-key-plain_notnow [data-testid="stElementContainer"],.st-key-plain_notnow [data-testid="stButton"]{background:none!important;box-shadow:none!important;border:none!important;max-width:100%!important}
.st-key-plain_notnow .stButton>button{background:none!important;border:none!important;box-shadow:none!important;color:#6B6F8C!important}
/* researcher tools: three buttons, one width, one left edge */
.st-key-sm_arrive,.st-key-sm_study,.st-key-danger_reset{width:100%!important;max-width:100%!important}
.st-key-sm_arrive .stButton,.st-key-sm_study .stButton,.st-key-danger_reset .stButton{display:flex!important;justify-content:flex-start!important}
.st-key-sm_arrive .stButton>button,.st-key-sm_study .stButton>button,.st-key-danger_reset .stButton>button{width:260px!important;min-width:260px!important;max-width:100%!important;min-height:44px}
/* top-right action buttons sit on the right edge of the page */
.st-key-sm_new .stButton{display:flex!important;justify-content:flex-end!important}
.st-key-sm_new .stButton>button{width:auto!important;min-width:110px}

/* face consent: Not now is a normal outlined button, same size as the primary */
.st-key-consent_btns [data-testid="stVerticalBlock"]{gap:12px!important}
.st-key-consent_btns .stButton>button{background:#fff;border:1.5px solid #D5D2F3!important;color:#1F2140}
.st-key-consent_btns .stButton>button[kind="primary"],.st-key-consent_btns .stButton>button[data-testid="stBaseButton-primary"]{background:linear-gradient(135deg,#6A5CF0,#4B3FC7)!important;border:none!important;color:#fff}
"""

# =====================================================================================================
# v7 FLAT: matches DESIGN_REFERENCE.png (flat white cards, thin lavender borders, solid purple actions,
# small rounded controls). Keeps the desktop layout: permanent left sidebar, full-width content.
# Loaded last, so it overrides the Liquid Glass layer above without touching any layout rule.
# =====================================================================================================
CSS = CSS + r"""
:root{--b:#4F46C6;--b-d:#4238B4;--tint:#EEEBFF;--tint-2:#F6F5FF;--line:#E6E7F2;--page:#F4F5FB;--ink:#1B1D3A;--muted:#6C7090;
  --r-card:16px;--r-ctl:12px}

/* ---- type: Inter everywhere (Streamlit's own heading font was leaking through) ---- */
html,body,.stApp,.stApp div,.stApp p,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp label,.stApp li,.stApp button,.stApp input,.stApp textarea,.stApp select,
.stApp span:not([data-testid="stIconMaterial"]){font-family:'Inter','Segoe UI',system-ui,-apple-system,Roboto,sans-serif!important}
.stApp{color:var(--ink)}

/* ---- page: flat light lavender, no gradient blobs, no blur anywhere ---- */
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--page)!important}
.stApp{background-image:none!important;background-color:var(--page)!important}
.card,.stat,.feat,.empty,.banner,.glass,.found,.lcard,.ctile,.cov,.pill,.dbadge,.tile,.cbtn,.ibtn,.stButton>button,
.st-key-sidebar,.st-key-drawer,.st-key-plussheet,.st-key-actionbar,.st-key-snack,.st-key-composer,div[data-testid="stDialog"] div[role="dialog"],
[data-testid="stTextInput"] [data-baseweb="input"],[class*="st-key-att_img"],[class*="st-key-att_m"],.st-key-studybar,.spin{
  -webkit-backdrop-filter:none!important;backdrop-filter:none!important}

/* ---- cards: white, 1px lavender-grey border, whisper shadow ---- */
.card,.stat,.feat,.empty,.cov,.glass,.lcard.good,[class*="st-key-att_img"],[class*="st-key-att_m"],[class*="st-key-row_"]{
  background:#fff!important;border:1px solid var(--line)!important;border-radius:var(--r-card)!important;
  box-shadow:0 1px 2px rgba(27,29,58,.04)!important}
.ctile{border:1px solid rgba(27,29,58,.05)!important;border-radius:var(--r-card)!important;box-shadow:none!important}
.banner{background:#FFF6E4!important;border:1px solid #F4DDAB!important;border-radius:var(--r-card)!important;box-shadow:none!important}
.lcard.warn{background:#FFF7E6!important;border:1px solid #F4DDAB!important;border-radius:var(--r-card)!important;box-shadow:none!important}
.found{background:#EAF8F1!important;border:1px solid #BFE8D3!important;border-radius:var(--r-card)!important;box-shadow:none!important}
@media (hover:hover){
  [class*="st-key-tap_"]:hover .card,[class*="st-key-tap_"]:hover .cov,[class*="st-key-tap_"]:hover .stat{border-color:#CFCBF0!important;
    box-shadow:0 4px 14px rgba(79,70,198,.10)!important}
  [class*="st-key-tap_"]:hover .pressable{transform:none}
  [class*="st-key-tap_"]:hover .tile{box-shadow:0 4px 14px rgba(27,29,58,.16)}
}
.tile{border:1px solid var(--line);border-radius:14px;box-shadow:none}
.cov{overflow:hidden}
.rthumb,.att-thumb{border-radius:10px}
.stat .sic,.feat .fi,.setrow .si,.dmap .si,.banner .bic,.qrow .qi{background:var(--tint)!important;color:var(--b)!important;border-radius:12px!important;box-shadow:none!important}
.banner .bic{background:#fff!important;color:#C27A00!important}
.dbadge{background:var(--tint);color:var(--b-d);box-shadow:none;border-radius:12px}
.dbadge.urgent{background:#FFF1D6;color:#8A5200}
.empty .ic{background:var(--tint)!important}
.empty,.card{overflow:hidden}

/* ---- pills / tags: lavender tag, amber "needs review" outline ---- */
.pill{background:var(--tint);color:#3B33A0;border:1px solid transparent;font-weight:600}
.pill.warn{background:#FFF6E4;color:#8A5200;border:1px solid #F4DDAB}
.pill.good{background:#E6F6EE;color:#0F6B49}
.pill.gray{background:#EFF0F6;color:#555A75}
.pill.bad{background:#FFE9EC;color:#9B2236}
.hero-img .pill{background:#fff;border:1px solid var(--line)}
mark{background:#E4DFFF;color:#3A2FA0}

/* ---- buttons: small rounded rectangles, outlined secondary, solid purple primary ---- */
.stButton>button{border-radius:var(--r-ctl);background:#fff;border:1px solid #D8D5F2;color:var(--b);box-shadow:none;font-weight:600;font-size:14px;min-height:44px}
.stButton>button p{color:inherit!important}
.stButton>button:hover{background:var(--tint-2);border-color:var(--b);color:var(--b-d)}
.stButton>button[kind="primary"],.stButton>button[data-testid="stBaseButton-primary"]{background:var(--b)!important;border:none!important;color:#fff!important;box-shadow:none!important}
.stButton>button[kind="primary"]:hover,.stButton>button[data-testid="stBaseButton-primary"]:hover{background:var(--b-d)!important;filter:none;color:#fff!important}
[class*="st-key-back"] button{border-radius:50%!important;background:#fff;border:1px solid var(--line);box-shadow:none}
[class*="st-key-link"] button{background:none!important;border:none!important;color:var(--b)!important;min-height:28px}
[class*="st-key-sm_"] button{border-radius:var(--r-ctl);min-height:42px}
[class*="st-key-danger"] button{color:#C2334D;border-color:#F3C9D1}
[class*="st-key-plain"] button,.st-key-plain_notnow .stButton>button{background:none!important;border:none!important;color:var(--muted)!important}
.st-key-consent_btns .stButton>button{border:1px solid #D8D5F2!important;background:#fff;color:var(--b)}
.st-key-consent_btns .stButton>button[kind="primary"],.st-key-consent_btns .stButton>button[data-testid="stBaseButton-primary"]{background:var(--b)!important;border:none!important;color:#fff}
.stDownloadButton>button{border-radius:var(--r-ctl);border:1px solid #D8D5F2;color:var(--b);background:#fff}
.stButton>button:focus-visible{outline:3px solid rgba(79,70,198,.35);outline-offset:2px}

/* ---- chips: lavender pills, selected = solid purple (as in the Library / Search filters) ---- */
[class*="st-key-chips"] .stButton>button{background:#EFEDFD;border:1px solid transparent;color:#3B33A0;border-radius:999px;min-height:38px;font-weight:600;box-shadow:none}
[class*="st-key-chips"] .stButton>button p{color:inherit!important}
[class*="st-key-chips"] .stButton>button:hover{background:#E4E0FB;border-color:transparent;color:#2F2790}
[class*="st-key-chips"] .stButton>button[kind="primary"],[class*="st-key-chips"] .stButton>button[data-testid="stBaseButton-primary"]{background:var(--b)!important;color:#fff!important}
[class*="st-key-chips"] .stButton>button[kind="primary"] p,[class*="st-key-chips"] .stButton>button[data-testid="stBaseButton-primary"] p{color:#fff!important}

/* ---- inputs ---- */
[data-testid="stTextInput"] [data-baseweb="input"],[data-testid="stTextArea"] [data-baseweb="textarea"],[data-testid="stNumberInput"] [data-baseweb="input"],[data-testid="stDateInput"] [data-baseweb="input"],[data-baseweb="select"]>div{
  background-color:#fff!important;border:1px solid var(--line)!important;border-radius:var(--r-ctl)!important;box-shadow:none!important}
[data-testid="stTextInput"] [data-baseweb="input"]{height:50px!important;min-height:50px!important}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within{border-color:var(--b)!important;box-shadow:0 0 0 3px rgba(79,70,198,.16)!important}
[data-testid="stRadio"] label{border:1px solid var(--line);border-radius:var(--r-ctl);background:#fff}
[data-testid="stRadio"] label:has(input:checked){border-color:var(--b);background:var(--tint-2)}
[class*="st-key-sel_"]{background:#fff;border:1px solid var(--line);border-radius:var(--r-ctl);box-shadow:none}

/* ---- Ask screen: one flat prompt bar, plain heading ---- */
.greet h2{font-weight:700;letter-spacing:-.03em;color:var(--ink)}
.greet p{color:var(--muted)}
.st-key-composer{background:linear-gradient(to top,var(--page) 68%,rgba(244,245,251,0))!important}
.cbtn{background:#fff;border:1px solid var(--line);box-shadow:none;color:var(--b)}
.cbtn.send{background:var(--b);border-color:var(--b);color:#fff;box-shadow:0 6px 16px rgba(79,70,198,.30)}
.st-key-composer_q [data-baseweb="input"]{border-radius:27px!important;box-shadow:0 2px 12px rgba(27,29,58,.06)!important}
.ibtn{background:#fff;border:1px solid var(--line);box-shadow:none}
.st-key-plussheet{background:#fff!important;border:1px solid var(--line);border-radius:var(--r-card)!important;box-shadow:0 12px 32px rgba(27,29,58,.14)!important}
.pl-row i{background:var(--tint);color:var(--b)}
.bub-u{background:var(--b);border-radius:16px 16px 4px 16px}
.av-ai{background:var(--b);border-radius:11px}
.bub-a{border:1px solid var(--line);box-shadow:none;border-radius:4px 16px 16px 16px}
details.how summary{color:var(--b)}

/* ---- sidebar: flat white column, lavender active row, solid purple logo ---- */
.logo-sm{background:var(--b)!important;border-radius:11px;width:36px;height:36px}
.dr-head{font-weight:700;font-size:19px;letter-spacing:-.03em;color:var(--ink)}
.dr-row{border-radius:var(--r-ctl);font-weight:600;font-size:14.5px;color:#2B2E4D;padding:11px 14px}
.dr-row.on{background:var(--tint)!important;color:var(--b)!important;box-shadow:none!important}
.dr-row:not(.on):hover{background:var(--tint-2)!important}
.dr-row small{background:var(--tint);color:var(--b);border-radius:999px;padding:2px 8px;font-weight:700}
.dr-note{color:#8A8EA8}
.st-key-drawer{background:#fff!important;border:none!important;border-radius:0 20px 20px 0!important}
@media (min-width:1000px){
  .st-key-sidebar{top:0!important;bottom:0!important;left:0!important;width:252px!important;max-width:252px!important;background:#fff!important;
    border:none!important;border-right:1px solid var(--line)!important;border-radius:0!important;box-shadow:none!important;padding:26px 14px!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar){padding-left:calc(252px + 44px)!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar) .st-key-composer{left:calc(50% + 126px)!important;width:min(calc(100vw - 252px),920px)!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar) .st-key-actionbar{left:calc(50% + 126px)!important;width:min(calc(100vw - 252px),780px)!important}
  [data-testid="stMainBlockContainer"]:has(.st-key-sidebar) .st-key-plussheet{left:calc(50% + 126px)!important;
    transform:translateX(calc(-1 * min((100vw - 252px) / 2, 460px) + 24px))!important}
}
.st-key-actionbar{background:#fff!important;border:1px solid var(--line);box-shadow:0 -8px 24px rgba(27,29,58,.06)!important}

/* ---- headings: bold, dark, no glass-era tracking ---- */
.sect b{font-weight:700;letter-spacing:-.02em;font-size:20px;color:var(--ink)}
.sect span{color:var(--muted);font-weight:500}
.ab-title{font-weight:700;color:var(--ink)}
.ab-title.two{display:flex;flex-direction:column;justify-content:center;line-height:1.15;text-align:left}
.ab-title.two small{font-size:14px;font-weight:500;color:var(--muted);letter-spacing:0}
.ab-title.two b{font-size:28px;font-weight:700;letter-spacing:-.03em;color:var(--ink)}
.me{width:44px;height:44px;border-radius:50%;background:var(--tint);color:var(--b);display:grid;place-items:center;font-weight:700;font-size:16px;margin-left:auto}
.st-key-home_q{max-width:640px;margin:2px 0 6px}
.h1,.dtitle,.rtitle,.wel-h,.hh-t{color:var(--ink)}
.snack-t{color:#fff!important}
.st-key-snack{background:#1B1D3A!important;border:none!important;border-radius:14px!important}

/* ---- welcome: soft lavender splash (like screen 1), purple Get started ---- */
.st-key-stack_wel{background:linear-gradient(135deg,#E8E4FD 0%,#F3F1FF 48%,#E3EFFC 100%)!important;border:1px solid #DFDBF6!important;
  box-shadow:none!important;border-radius:24px!important}
.wel-brand,.wel-h{color:var(--ink)!important}
.wel-p{color:var(--muted)!important}
.wel-note{color:#8A8EA8!important}
.wel-logo2{background:var(--b);border-radius:12px}
.mos .m{border:3px solid #fff;box-shadow:0 8px 22px rgba(27,29,58,.18);border-radius:16px}
.st-key-start .stButton>button,.st-key-start .stButton>button[kind="primary"],.st-key-start .stButton>button[data-testid="stBaseButton-primary"]{
  background:var(--b)!important;color:#fff!important;border:none!important;box-shadow:0 8px 20px rgba(79,70,198,.28)!important}
.st-key-start .stButton>button:hover{background:var(--b-d)!important;color:#fff!important}
.st-key-start .stButton>button p{color:#fff!important}
.st-key-why .stButton>button{background:#fff!important;color:var(--b)!important;border:1px solid #D8D5F2!important}
.st-key-homehero{background:var(--tint)!important;border:1px solid #DFDBF6!important;box-shadow:none!important;border-radius:24px!important}
.st-key-homehero .hh-t{color:var(--ink)!important}.st-key-homehero .hh-s{color:var(--muted)!important}

/* ---- dialogs, spinner, progress ---- */
div[data-testid="stDialog"] div[role="dialog"]{background:#fff!important;border:1px solid var(--line);border-radius:20px!important;box-shadow:0 24px 60px rgba(27,29,58,.22)!important}
.spin{background:none;box-shadow:none;border:6px solid #E3E1F7;border-top-color:var(--b)}
.progress i{background:var(--b)}
.att-proof i{background:var(--tint);color:var(--ink)}
.att-hero .ah-n,.about-h{color:var(--ink)}
.ah-sep{background:var(--line)}
.setrow,.stepi{border-bottom:1px solid #EFF0F7}
.loop .lp-c{border-left-color:var(--b)}
.dm-t em{color:var(--b)}
"""

# v7b: text inputs across Streamlit versions (newer builds expose data-testid="stTextInputRootElement" instead of baseweb)
CSS = CSS + r"""
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]{background-color:#fff!important;border:1px solid var(--line)!important;
  border-radius:var(--r-ctl)!important;height:50px!important;min-height:50px!important;box-shadow:none!important;overflow:hidden;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%236C7090' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='6.5'/%3E%3Cpath d='m20 20-4-4'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:16px center;background-size:20px}
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]:focus-within{border-color:var(--b)!important;box-shadow:0 0 0 3px rgba(79,70,198,.16)!important}
[data-testid="stTextInput"] [data-testid="stTextInputRootElement"]>div,[data-testid="stTextInput"] [data-testid="stTextInputRootElement"] [data-baseweb="base-input"]{background:transparent!important;border:0!important}
.st-key-composer_q [data-testid="stTextInputRootElement"],.st-key-composer_q [data-baseweb="input"]{height:54px!important;min-height:54px!important;border-radius:27px!important;
  background-image:none!important;border:1px solid var(--line)!important;box-shadow:0 2px 12px rgba(27,29,58,.06)!important}
[class*="st-key-nc_name"] [data-testid="stTextInputRootElement"],[class*="st-key-nc_new"] [data-testid="stTextInputRootElement"],
[class*="st-key-md_"] [data-testid="stTextInputRootElement"],[class*="st-key-st_"] [data-testid="stTextInputRootElement"],[class*="st-key-per_"] [data-testid="stTextInputRootElement"]{background-image:none!important}
[class*="st-key-nc_name"] input,[class*="st-key-nc_new"] input,[class*="st-key-md_"] input,[class*="st-key-st_"] input,[class*="st-key-per_"] input{padding-left:14px!important}
"""

CSS = CSS + r"""
.st-key-start .stButton,.st-key-start [data-testid="stElementContainer"]{max-width:260px!important}
.st-key-home_q,.st-key-home_q [data-testid="stTextInput"]{max-width:640px!important}
"""

CSS = CSS + r"""
img.me{object-fit:cover;border:2px solid #fff;box-shadow:0 0 0 1px var(--line);display:block}
"""

CSS = CSS + r"""
/* labelled Home button on the results and photo-details screens */
[class*="st-key-homebtn_"]{display:flex;justify-content:flex-end;width:100%!important;max-width:100%!important}
[class*="st-key-homebtn_"] .stButton{width:auto!important;max-width:none!important}
[class*="st-key-homebtn_"] .stButton>button{width:auto!important;min-width:0!important;padding:0 18px;min-height:44px;gap:6px}
"""

CSS = CSS + r"""
/* keep the title bar (and its Home button) in view while scrolling a long set of results */
.st-key-v_chat .st-key-appbar,.st-key-v_results .st-key-appbar{position:sticky;top:0;z-index:60;background:var(--page);margin:0!important;padding:14px 0 10px!important}
"""

CSS = CSS + r"""
/* newer Streamlit wraps keyed blocks in a layout wrapper: the wrapper is what has to stick */
.st-key-v_chat [data-testid="stLayoutWrapper"]:has(> .st-key-appbar),.st-key-v_results [data-testid="stLayoutWrapper"]:has(> .st-key-appbar){
  position:sticky;top:0;z-index:60;background:var(--page)}
.st-key-v_chat [data-testid="stLayoutWrapper"]>.st-key-appbar,.st-key-v_results [data-testid="stLayoutWrapper"]>.st-key-appbar{position:static}
"""

CSS = CSS + r"""
/* the Home button needs its natural width (the app bar's last column is otherwise fixed at 48px for the old icon button) */
.st-key-v_chat .st-key-appbar [data-testid="stColumn"]:last-child,.st-key-v_results .st-key-appbar [data-testid="stColumn"]:last-child,
[class*="st-key-topbar_"] [data-testid="stColumn"]:last-child:not(:first-child){flex:1 1 auto!important;width:auto!important;min-width:110px!important}
[class*="st-key-homebtn_"] .stButton>button{white-space:nowrap}
"""

# editor: prompt row and example chips
CSS += """
.st-key-chips_edit [data-testid="stHorizontalBlock"]{gap:8px!important;flex-wrap:wrap!important}
.st-key-chips_edit [data-testid="stColumn"]{flex:0 0 auto!important;width:auto!important;min-width:0!important}
.st-key-chips_edit .stButton>button{min-height:34px;padding:0 14px;font-size:13px;width:auto}
"""
