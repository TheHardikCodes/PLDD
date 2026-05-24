"""
LeafScan v4 — Complete Farmer's Friend App
Run: python app.py  |  Open: http://localhost:5000
"""
import os
from flask import Flask, request, jsonify, render_template_string
from predict import predict_image

app = Flask(__name__)
UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="dark" data-lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">

<title>LeafScan - AI Plant Disease Detector</title>

<meta name="description" content="LeafScan is a free AI-powered plant disease detection tool for farmers.">

<meta name="keywords" content="LeafScan, plant disease detection, AI farming, crop disease detector">

<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
[data-theme="dark"]{
  --bg:#04090a;--bg2:#0a1210;--bg3:#101a14;--bg4:#162118;
  --brd:rgba(110,251,92,.08);--brd2:rgba(110,251,92,.15);--brd3:rgba(110,251,92,.26);
  --tx:#dff0df;--tx2:#7aaa82;--tx3:#3d6644;
  --g:#5dffa0;--g2:#38e07a;--g3:#13834a;
  --gd:rgba(93,255,160,.09);--gg:rgba(93,255,160,.2);--gs:rgba(93,255,160,.04);
  --r:#ff6b7a;--rd:rgba(255,107,122,.11);--y:#ffd97a;--yd:rgba(255,217,122,.11);
  --gold:#f5c842;--goldd:rgba(245,200,66,.12);
  --sh:0 2px 16px rgba(0,0,0,.55);--shb:0 24px 70px rgba(0,0,0,.75);
  --card-glow:0 0 0 1px rgba(93,255,160,.06),0 8px 32px rgba(0,0,0,.4);
}
[data-theme="light"]{
  --bg:#f4f9f1;--bg2:#ffffff;--bg3:#e8f3e4;--bg4:#d8ecd2;
  --brd:rgba(0,0,0,.07);--brd2:rgba(0,0,0,.13);--brd3:rgba(0,0,0,.22);
  --tx:#152515;--tx2:#366036;--tx3:#7aaa7a;
  --g:#0e7a3a;--g2:#12a050;--g3:#38e07a;
  --gd:rgba(14,122,58,.09);--gg:rgba(14,122,58,.2);--gs:rgba(14,122,58,.04);
  --r:#c41a2a;--rd:rgba(196,26,42,.09);--y:#a07800;--yd:rgba(160,120,0,.1);
  --gold:#a07800;--goldd:rgba(160,120,0,.1);
  --sh:0 2px 12px rgba(0,0,0,.07);--shb:0 20px 60px rgba(0,0,0,.1);
  --card-glow:0 0 0 1px rgba(14,122,58,.06),0 4px 16px rgba(0,0,0,.06);
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'Plus Jakarta Sans',sans-serif;background:var(--bg);color:var(--tx);min-height:100vh;overflow-x:hidden;transition:background .4s,color .4s;cursor:none}
img{max-width:100%}
/* ══ CURSOR ══ */
#cD,#cR,#cT{position:fixed;border-radius:50%;pointer-events:none;z-index:9999;top:0;left:0;will-change:transform}
#cD{width:6px;height:6px;background:var(--g);margin:-3px 0 0 -3px;transition:transform .08s,background .25s;box-shadow:0 0 6px var(--gg)}
#cR{width:36px;height:36px;border:1.5px solid var(--g);margin:-18px 0 0 -18px;opacity:.45;transition:width .3s cubic-bezier(.34,1.56,.64,1),height .3s cubic-bezier(.34,1.56,.64,1),opacity .3s,border-color .3s,transform .08s}
#cT{width:4px;height:4px;background:rgba(93,255,160,.5);margin:-2px 0 0 -2px;transition:none}
body.cg #cD{transform:scale(0) !important}
body.cg #cR{width:48px;height:48px;opacity:.6;border-color:var(--g);border-width:1px;background:rgba(93,255,160,.06)}
body.cg #cT{display:none}
body.cc #cD{background:#fff;box-shadow:0 0 16px #fff;transform:scale(3) !important}
body.cc #cR{width:16px;height:16px;opacity:.8;border-color:#fff}
@media(hover:none){#cD,#cR,#cT{display:none}body{cursor:auto}}
/* ══ CAMERA ══ */
.cam-row{display:flex;gap:8px;margin-top:.8rem}
.cam-btn{flex:1;display:flex;align-items:center;justify-content:center;gap:7px;padding:.7rem;border-radius:10px;border:1px solid var(--brd2);background:color-mix(in srgb,var(--bg3) 80%,transparent);color:var(--tx2);font-family:inherit;font-size:.76rem;font-weight:700;cursor:pointer;transition:all .25s;backdrop-filter:blur(8px)}
.cam-btn:hover{background:var(--gd);color:var(--g);border-color:var(--gg);transform:translateY(-2px);box-shadow:0 6px 18px rgba(0,0,0,.15)}
.cam-btn.cam-alt:hover{background:var(--bg4);color:var(--tx);border-color:var(--brd3)}
.cam-ico{font-size:1rem}
#camModal{position:fixed;inset:0;z-index:600;display:none;background:rgba(0,0,0,.9);backdrop-filter:blur(12px);animation:fadeIn .25s ease}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
.cam-box{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(420px,calc(100vw - 2rem));background:var(--bg2);border:1px solid var(--brd2);border-radius:20px;overflow:hidden;box-shadow:0 28px 80px rgba(0,0,0,.8)}
.cam-hd{display:flex;align-items:center;justify-content:space-between;padding:.8rem 1.1rem;border-bottom:1px solid var(--brd);background:color-mix(in srgb,var(--bg3) 50%,transparent)}
.cam-close{background:none;border:none;color:var(--tx3);font-size:1rem;cursor:pointer;padding:4px 8px;border-radius:6px;transition:all .2s}
.cam-close:hover{background:var(--rd);color:var(--r)}
.cam-view{position:relative;background:#000;aspect-ratio:4/3;overflow:hidden}
#camVideo{width:100%;height:100%;object-fit:cover;display:block}
.cam-overlay{position:absolute;inset:0;pointer-events:none}
.cam-guide{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:70%;height:70%;display:flex;align-items:center;justify-content:center}
.cg-corner{position:absolute;width:22px;height:22px;border-color:rgba(93,255,160,.85);border-style:solid;filter:drop-shadow(0 0 4px var(--g))}
.cg-corner.tl{top:0;left:0;border-width:2.5px 0 0 2.5px;border-radius:4px 0 0 0}
.cg-corner.tr{top:0;right:0;border-width:2.5px 2.5px 0 0;border-radius:0 4px 0 0}
.cg-corner.bl{bottom:0;left:0;border-width:0 0 2.5px 2.5px;border-radius:0 0 0 4px}
.cg-corner.br{bottom:0;right:0;border-width:0 2.5px 2.5px 0;border-radius:0 0 4px 0}
.cg-hint{position:absolute;bottom:-24px;left:50%;transform:translateX(-50%);font-size:.65rem;color:rgba(93,255,160,.75);white-space:nowrap;font-weight:700;letter-spacing:.06em;text-transform:uppercase}
.cam-foot{display:flex;align-items:center;justify-content:space-between;padding:.9rem 1.5rem;background:color-mix(in srgb,var(--bg3) 40%,transparent)}
.cam-flip{background:color-mix(in srgb,var(--bg4) 70%,transparent);border:1px solid var(--brd2);color:var(--tx2);font-size:1.1rem;width:42px;height:42px;border-radius:50%;cursor:pointer;transition:all .22s;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(8px)}
.cam-flip:hover{background:var(--bg4);color:var(--tx);transform:rotate(180deg)}
.cam-snap{width:62px;height:62px;border-radius:50%;background:transparent;border:2.5px solid var(--g);cursor:pointer;position:relative;display:flex;align-items:center;justify-content:center;transition:all .2s;box-shadow:0 0 20px var(--gg)}
.cam-snap:hover{transform:scale(1.08);box-shadow:0 0 30px var(--gg)}
.cam-snap:active{transform:scale(.93)}
.snap-ring{width:46px;height:46px;border-radius:50%;background:var(--g);transition:all .15s;box-shadow:0 0 16px var(--gg)}
.cam-snap:active .snap-ring{transform:scale(.82)}
/* ══ VALIDATION BADGE ══ */
.val-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 10px;border-radius:99px;font-size:.67rem;font-weight:800;letter-spacing:.05em;backdrop-filter:blur(10px)}
.val-leaf{background:rgba(93,255,160,.2);color:#5dffa0;border:1px solid rgba(93,255,160,.3)}
.val-warn{background:rgba(255,165,0,.2);color:#ffa500;border:1px solid rgba(255,165,0,.3)}
.val-err{background:rgba(255,80,80,.2);color:#ff5050;border:1px solid rgba(255,80,80,.3)}
/* ══ CANVAS ══ */
#bgC{position:fixed;inset:0;z-index:0;pointer-events:none;opacity:.45}
/* ══ LAYOUT ══ */
.page{position:relative;z-index:1;max-width:1160px;margin:0 auto;padding:0 1.5rem}
/* ══ NAV ══ */
nav{display:flex;align-items:center;justify-content:space-between;padding:1rem 0;border-bottom:1px solid var(--brd);position:sticky;top:0;z-index:100;background:color-mix(in srgb,var(--bg) 78%,transparent);backdrop-filter:blur(24px) saturate(1.4);-webkit-backdrop-filter:blur(24px) saturate(1.4);margin:0 -1.5rem;padding-left:1.5rem;padding-right:1.5rem}
.logo{display:flex;align-items:center;gap:11px;font-weight:800;font-size:1.05rem;letter-spacing:-.04em;color:var(--tx);text-decoration:none}
.logo-m{width:32px;height:32px;border-radius:9px;background:linear-gradient(135deg,var(--g),var(--g2));display:grid;place-items:center;font-size:16px;transition:transform .45s cubic-bezier(.34,1.56,.64,1),box-shadow .3s;box-shadow:0 0 0 0 var(--gg)}
.logo:hover .logo-m{transform:rotate(22deg) scale(1.12);box-shadow:0 0 0 6px var(--gd),0 0 28px var(--gg)}
.nav-r{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.nbadge{display:flex;align-items:center;gap:5px;padding:5px 11px;border-radius:99px;background:var(--gd);border:1px solid var(--gg);color:var(--g);font-size:.64rem;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.ldot{width:5px;height:5px;border-radius:50%;background:var(--g);animation:lpulse 1.8s infinite}
@keyframes lpulse{0%,100%{box-shadow:0 0 0 0 var(--gg)}55%{box-shadow:0 0 0 6px transparent}}
.cb{display:flex;align-items:center;gap:5px;padding:5px 12px;border-radius:99px;border:1px solid var(--brd2);background:color-mix(in srgb,var(--bg3) 80%,transparent);color:var(--tx2);font-family:inherit;font-size:.67rem;font-weight:700;cursor:pointer;transition:all .22s;letter-spacing:.05em;text-transform:uppercase;white-space:nowrap;backdrop-filter:blur(8px)}
.cb:hover{background:var(--bg4);color:var(--tx);border-color:var(--brd3);transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.15)}
.cb.on{background:var(--gd);color:var(--g);border-color:var(--gg)}
/* Lang dropdown */
.lw{position:relative}
.ldrop{position:absolute;top:calc(100% + 8px);right:0;min-width:152px;background:var(--bg2);border:1px solid var(--brd2);border-radius:14px;padding:5px;z-index:300;display:none;box-shadow:var(--shb);animation:popIn .22s cubic-bezier(.34,1.56,.64,1)}
.lw.open .ldrop{display:block}
@keyframes popIn{from{opacity:0;transform:scale(.86) translateY(-10px)}to{opacity:1;transform:none}}
.lopt{display:flex;align-items:center;gap:9px;padding:8px 10px;border-radius:9px;cursor:pointer;transition:background .15s;font-size:.8rem;font-weight:600;color:var(--tx2)}
.lopt:hover{background:var(--bg3);color:var(--tx)}.lopt.sel{background:var(--gd);color:var(--g)}
/* ══ FARMER BG ══ */
#farmerBg{position:fixed;inset:0;z-index:0;background-size:cover;background-position:center;background-repeat:no-repeat;transition:opacity 1s ease;opacity:0;pointer-events:none}
#farmerBg::after{content:'';position:absolute;inset:0;background:var(--bg-overlay,rgba(4,9,10,.84));transition:background .5s}
[data-theme="light"] #farmerBg::after{background:rgba(244,249,241,.8)}
#farmerBg.visible{opacity:1}
/* ══ QUOTE BANNER — UPGRADED ══ */
.qbanner{position:relative;z-index:2;margin:.5rem 0 1.6rem;padding:1.4rem 1.8rem;border-radius:16px;background:color-mix(in srgb,var(--bg2) 70%,transparent);border:1px solid var(--brd2);backdrop-filter:blur(20px) saturate(1.3);-webkit-backdrop-filter:blur(20px) saturate(1.3);overflow:hidden;transition:all .35s cubic-bezier(.22,1,.36,1);cursor:pointer;box-shadow:var(--card-glow)}
.qbanner::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:linear-gradient(180deg,var(--g),var(--g2),var(--gold));border-radius:4px 0 0 4px}
.qbanner::after{content:'';position:absolute;top:-60px;right:-60px;width:180px;height:180px;border-radius:50%;background:radial-gradient(circle,var(--gd) 0%,transparent 70%);pointer-events:none;transition:transform .5s}
.qbanner:hover{border-color:var(--gg);box-shadow:0 0 0 1px var(--gg),0 12px 40px rgba(0,0,0,.2);transform:translateY(-1px)}
.qbanner:hover::after{transform:scale(1.4)}
.q-inner{display:flex;align-items:flex-start;gap:14px;position:relative}
.q-leaf{font-size:1.8rem;flex-shrink:0;animation:qLeaf 4s ease-in-out infinite;filter:drop-shadow(0 0 8px var(--gg))}
@keyframes qLeaf{0%,100%{transform:rotate(-6deg) scale(1)}50%{transform:rotate(6deg) scale(1.08)}}
.q-body{flex:1;text-align:left}
.q-text{font-family:'Instrument Serif',serif;font-size:1.22rem;font-style:italic;color:var(--tx);line-height:1.55;letter-spacing:-.01em;animation:qFade .5s ease}
@keyframes qFade{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.q-author{font-size:.7rem;color:var(--g);margin-top:.5rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;opacity:.8}
.q-hint{display:flex;align-items:center;gap:5px;font-size:.62rem;color:var(--tx3);margin-top:.4rem;font-weight:600}
.q-hint span{animation:rotateSpin 3s linear infinite;display:inline-block;opacity:.5}
@keyframes rotateSpin{to{transform:rotate(360deg)}}
/* ══ TOOLTIP ══ */
.tip-host{position:relative;display:inline-flex;align-items:center;gap:4px;cursor:help}
.tip-host .tip-ico{font-size:.72rem;color:var(--g);opacity:.7;transition:opacity .2s}
.tip-host:hover .tip-ico{opacity:1}
.ttip{position:absolute;bottom:calc(100% + 8px);left:50%;transform:translateX(-50%) scale(.88);min-width:210px;max-width:270px;background:var(--bg2);border:1px solid var(--brd2);border-radius:12px;padding:.8rem 1rem;font-size:.73rem;color:var(--tx2);line-height:1.55;z-index:999;opacity:0;pointer-events:none;transition:all .22s cubic-bezier(.34,1.56,.64,1);box-shadow:var(--shb);font-style:normal;text-align:left}
.ttip::after{content:\'\';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:5px solid transparent;border-top-color:var(--brd2)}
.tip-host:hover .ttip{opacity:1;transform:translateX(-50%) scale(1)}
.ttip-title{font-weight:800;color:var(--tx);font-size:.76rem;margin-bottom:4px;display:flex;align-items:center;gap:5px}
/* ══ FACT CHIP ══ */
.fact-strip{display:flex;gap:7px;overflow-x:auto;padding-bottom:4px;margin:.8rem 0;scrollbar-width:none}
.fact-strip::-webkit-scrollbar{display:none}
.fact-chip{flex-shrink:0;display:flex;align-items:center;gap:7px;padding:6px 13px;border-radius:99px;background:color-mix(in srgb,var(--bg3) 90%,transparent);border:1px solid var(--brd2);font-size:.68rem;font-weight:600;color:var(--tx2);white-space:nowrap;cursor:default;transition:all .25s;backdrop-filter:blur(8px)}
.fact-chip:hover{background:var(--gd);color:var(--g);border-color:var(--gg);transform:translateY(-2px);box-shadow:0 4px 14px rgba(0,0,0,.15)}
.fact-chip span:first-child{font-size:.88rem}
/* ══ HERO ══ */
.hero{padding:3.2rem 0 2rem;text-align:center}
.heyebrow{display:inline-flex;align-items:center;gap:7px;font-size:.67rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--g);background:var(--gd);padding:5px 15px;border-radius:99px;border:1px solid var(--gg);margin-bottom:1.2rem;animation:fUp .6s .1s both;box-shadow:0 0 20px var(--gs)}
.hero h1{font-family:\'Instrument Serif\',serif;font-size:clamp(2.3rem,5.5vw,4.6rem);line-height:1.04;letter-spacing:-.03em;margin-bottom:.9rem;animation:fUp .6s .2s both}
.hero h1 em{font-style:italic;color:var(--g);text-shadow:0 0 30px var(--gg)}
.hero p{font-size:.96rem;color:var(--tx2);max-width:440px;margin:0 auto 1.6rem;line-height:1.72;animation:fUp .6s .3s both;font-weight:500}
@keyframes fUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
.stats{display:flex;align-items:center;justify-content:center;gap:1.6rem;margin-bottom:2.2rem;flex-wrap:wrap;animation:fUp .6s .4s both}
.stat{text-align:center;padding:.5rem 1rem;border-radius:12px;cursor:default;transition:all .25s;position:relative}
.stat::before{content:\'\';position:absolute;inset:0;border-radius:12px;background:var(--gd);opacity:0;transition:opacity .25s}
.stat:hover::before{opacity:1}
.stat:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.12)}
.stn{font-size:1.5rem;font-weight:800;color:var(--tx);line-height:1;position:relative}.stn em{font-style:normal;color:var(--g)}
.stl{font-size:.62rem;color:var(--tx3);margin-top:3px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;position:relative}
.stsep{width:1px;height:22px;background:var(--brd2)}
/* ══ TABS ══ */
.tabs{display:flex;gap:3px;background:color-mix(in srgb,var(--bg2) 90%,transparent);border:1px solid var(--brd);border-radius:14px;padding:4px;margin-bottom:1.4rem;overflow-x:auto;box-shadow:var(--card-glow);backdrop-filter:blur(12px)}
.tab{flex:1;min-width:76px;padding:.52rem .6rem;border-radius:10px;border:none;background:transparent;color:var(--tx3);font-family:inherit;font-size:.72rem;font-weight:700;cursor:pointer;transition:all .25s;white-space:nowrap;text-align:center;letter-spacing:.01em}
.tab:hover{color:var(--tx2);background:color-mix(in srgb,var(--bg3) 70%,transparent)}
.tab.on{background:linear-gradient(135deg,var(--gd),color-mix(in srgb,var(--gd) 55%,transparent));color:var(--g);box-shadow:0 0 0 1px var(--gg) inset,0 2px 14px var(--gs)}
/* ══ GRID ══ */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem}

/* ══ TAB PANELS ══ */
.tab-panel{display:none}
.tab-panel.on{display:block;animation:tabReveal .38s cubic-bezier(.22,1,.36,1) both}
@keyframes tabReveal{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@media(max-width:700px){.grid{grid-template-columns:1fr}}
.col{display:flex;flex-direction:column;gap:1.1rem}
/* ══ CARD ══ */
.card{background:color-mix(in srgb,var(--bg2) 88%,transparent);border:1px solid var(--brd);border-radius:16px;overflow:hidden;box-shadow:var(--card-glow);transition:border-color .28s,box-shadow .3s,transform .28s;backdrop-filter:blur(16px) saturate(1.3);-webkit-backdrop-filter:blur(16px) saturate(1.3)}
.card:hover{border-color:var(--brd2);transform:translateY(-2px);box-shadow:0 0 0 1px var(--brd2),0 16px 48px rgba(0,0,0,.2)}
.chd{padding:.9rem 1.2rem;border-bottom:1px solid var(--brd);display:flex;align-items:center;gap:9px;background:color-mix(in srgb,var(--bg3) 35%,transparent)}
.xico{width:30px;height:30px;border-radius:8px;background:linear-gradient(135deg,var(--bg4),var(--bg3));display:grid;place-items:center;font-size:14px;flex-shrink:0;transition:transform .36s cubic-bezier(.34,1.56,.64,1);box-shadow:0 2px 6px rgba(0,0,0,.12)}
.card:hover .xico{transform:scale(1.22) rotate(-10deg)}
.cttl{font-size:.8rem;font-weight:800;color:var(--tx);letter-spacing:-.01em}
.csub{font-size:.63rem;color:var(--tx3);margin-top:1px;font-weight:500}
.cbd{padding:1.1rem}
/* ══ DROP ZONE ══ */
.dz{border:1.5px dashed var(--brd2);border-radius:12px;padding:2.4rem 1rem;text-align:center;cursor:pointer;transition:all .32s;position:relative;overflow:hidden}
.dz::before{content:\'\';position:absolute;inset:0;background:radial-gradient(ellipse at 50% 60%,var(--gd) 0%,transparent 68%);opacity:0;transition:opacity .38s}
.dz:hover::before,.dz.over::before{opacity:1}
.dz:hover,.dz.over{border-color:var(--g);border-style:solid;box-shadow:0 0 0 4px var(--gs),0 8px 28px rgba(0,0,0,.15)}
.dz-orb{width:60px;height:60px;border-radius:50%;border:1.5px solid var(--brd2);margin:0 auto .95rem;display:grid;place-items:center;font-size:24px;position:relative;transition:all .36s cubic-bezier(.34,1.56,.64,1);background:color-mix(in srgb,var(--bg3) 80%,transparent)}
.dz-orb::before{content:\'\';position:absolute;inset:-13px;border-radius:50%;border:1px dashed var(--gg);opacity:.35;animation:dzSpin 10s linear infinite}
.dz-orb::after{content:\'\';position:absolute;inset:-24px;border-radius:50%;border:1px dashed var(--g);opacity:.12;animation:dzSpin 18s linear infinite reverse}
@keyframes dzSpin{to{transform:rotate(360deg)}}
.dz:hover .dz-orb,.dz.over .dz-orb{transform:scale(1.14);box-shadow:0 0 0 14px var(--gd),0 0 0 28px var(--gs);border-color:var(--g);background:var(--gd)}
.dzt{font-size:.86rem;font-weight:700;color:var(--tx);margin-bottom:4px;position:relative}
.dzs{font-size:.72rem;color:var(--tx3);position:relative}.dzs b{color:var(--g)}
#fI{display:none}
/* Preview */
#pW{display:none;margin-top:.9rem;position:relative;border-radius:12px;overflow:hidden;box-shadow:0 6px 24px rgba(0,0,0,.22)}
#pW img{width:100%;max-height:230px;object-fit:cover;display:block;transition:transform .45s ease}
#pW:hover img{transform:scale(1.03)}
.pover{position:absolute;inset:0;background:linear-gradient(to bottom,transparent 38%,rgba(0,0,0,.65));opacity:0;transition:opacity .3s}
#pW:hover .pover{opacity:1}
.pchips{position:absolute;top:8px;right:8px;display:flex;gap:5px;z-index:2}
.pchip{backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.14);border-radius:99px;padding:4px 10px;font-size:.64rem;font-weight:700}
.pcn{background:rgba(0,0,0,.72);color:rgba(255,255,255,.82)}
.pcc{background:rgba(93,255,160,.18);color:#5dffa0;cursor:pointer;transition:background .2s}
.pcc:hover{background:rgba(93,255,160,.34)}
/* ══ ANALYZE BTN ══ */
.abtn{display:flex;align-items:center;justify-content:center;gap:9px;width:100%;margin-top:1rem;padding:1rem;background:linear-gradient(135deg,var(--g) 0%,var(--g2) 100%);color:#030d05;border:none;border-radius:11px;font-family:inherit;font-size:.92rem;font-weight:800;cursor:pointer;letter-spacing:.01em;transition:all .28s;position:relative;overflow:hidden;box-shadow:0 4px 22px rgba(93,255,160,.22),0 0 0 0 var(--gd)}
.abtn::before{content:\'\';position:absolute;inset:0;background:linear-gradient(135deg,rgba(255,255,255,.24),rgba(255,255,255,0));transform:translateX(-100%);transition:transform .44s ease}
.abtn:hover::before{transform:translateX(100%)}
.abtn:hover{box-shadow:0 0 0 5px var(--gd),0 14px 40px rgba(93,255,160,.3);transform:translateY(-2px)}
.abtn:active{transform:translateY(0) scale(.98)}.abtn:disabled{opacity:.25;cursor:not-allowed;transform:none;box-shadow:none;background:var(--bg4);color:var(--tx3)}
.abtn:disabled::before{display:none}
.aarrow{transition:transform .32s cubic-bezier(.34,1.56,.64,1)}
.abtn:hover .aarrow{transform:translateX(7px)}
/* ══ LOADER ══ */
#ldr{display:none;margin-top:1.1rem}
.sbox{position:relative;border-radius:13px;overflow:hidden;border:1px solid var(--brd2);box-shadow:0 0 0 1px var(--brd)}
.simg{width:100%;max-height:200px;object-fit:cover;display:block;filter:saturate(1.7) brightness(.28) hue-rotate(15deg)}
.corners span{position:absolute;width:20px;height:20px;border-color:var(--g);border-style:solid;filter:drop-shadow(0 0 5px var(--g));animation:cpulse 2s ease-in-out infinite}
.corners span:nth-child(1){top:8px;left:8px;border-width:2px 0 0 2px;border-radius:3px 0 0 0}
.corners span:nth-child(2){top:8px;right:8px;border-width:2px 2px 0 0;border-radius:0 3px 0 0}
.corners span:nth-child(3){bottom:8px;left:8px;border-width:0 0 2px 2px;border-radius:0 0 0 3px}
.corners span:nth-child(4){bottom:8px;right:8px;border-width:0 2px 2px 0;border-radius:0 0 3px 0}
@keyframes cpulse{0%,100%{opacity:1}50%{opacity:.3}}
.sbeam{position:absolute;left:0;right:0;height:3px;animation:beamAnim 2s ease-in-out infinite;background:linear-gradient(90deg,transparent 0%,var(--g) 22%,rgba(255,255,255,.95) 50%,var(--g) 78%,transparent 100%);box-shadow:0 0 18px var(--g),0 0 40px var(--gg),0 0 80px var(--gs)}
@keyframes beamAnim{0%{top:0;opacity:0}5%{opacity:1}95%{opacity:1}100%{top:100%;opacity:0}}
.sfoot{display:flex;justify-content:space-between;padding:.55rem .9rem;background:color-mix(in srgb,var(--bg3) 75%,transparent);border-top:1px solid var(--brd);backdrop-filter:blur(10px)}
.slbl{font-size:.67rem;color:var(--g);font-weight:800;letter-spacing:.13em;text-transform:uppercase;display:flex;align-items:center;gap:6px;text-shadow:0 0 12px var(--gg)}
.spct{font-family:monospace;font-size:.7rem;color:var(--g);font-weight:700}
.srow{display:flex;flex-wrap:wrap;gap:4px;margin-top:.7rem}
.step{font-size:.6rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;padding:3px 9px;border-radius:99px;background:color-mix(in srgb,var(--bg3) 80%,transparent);border:1px solid var(--brd);color:var(--tx3);transition:all .44s;backdrop-filter:blur(6px)}
.step.on{background:var(--gd);border-color:var(--gg);color:var(--g);box-shadow:0 0 14px var(--gs)}
.step.ok{color:var(--tx2);border-color:var(--brd2)}
/* ══ RESULT ══ */
#rCard{display:none}
.rhero{display:flex;align-items:center;gap:13px;padding:1rem 1.15rem;border-radius:14px;margin-bottom:.9rem;position:relative;overflow:hidden}
.rhero::before{content:\'\';position:absolute;inset:0;opacity:.5}
.rhero.H{background:linear-gradient(135deg,color-mix(in srgb,var(--gd) 120%,transparent),color-mix(in srgb,var(--gd) 40%,transparent));border:1px solid var(--gg)}
.rhero.H::before{background:radial-gradient(ellipse at 90% 50%,var(--gg),transparent 65%)}
.rhero.D{background:linear-gradient(135deg,color-mix(in srgb,var(--rd) 130%,transparent),color-mix(in srgb,var(--rd) 40%,transparent));border:1px solid rgba(255,107,122,.28)}
.rhero.D::before{background:radial-gradient(ellipse at 90% 50%,rgba(255,107,122,.22),transparent 65%)}
.rorb{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;font-size:20px;flex-shrink:0;transition:transform .42s cubic-bezier(.34,1.56,.64,1);position:relative;z-index:1}
.rhero:hover .rorb{transform:scale(1.22) rotate(16deg)}
.H .rorb{background:rgba(93,255,160,.16);box-shadow:0 0 20px rgba(93,255,160,.22)}
.D .rorb{background:rgba(255,107,122,.16);box-shadow:0 0 20px rgba(255,107,122,.22)}
.rtag{font-size:.63rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;margin-bottom:3px;position:relative;z-index:1}
.H .rtag{color:var(--g)}.D .rtag{color:var(--r)}
.rnm{font-size:.92rem;font-weight:700;color:var(--tx);position:relative;z-index:1;line-height:1.3}
/* Info grid */
.ig2{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:.9rem}
.ic{background:color-mix(in srgb,var(--bg3) 75%,transparent);border:1px solid var(--brd);border-radius:10px;padding:.78rem;transition:all .25s;backdrop-filter:blur(10px)}
.ic:hover{border-color:var(--brd2);transform:scale(1.025);box-shadow:0 4px 16px rgba(0,0,0,.1)}
.icl{font-size:.6rem;color:var(--tx3);font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px}
.icv{font-size:.83rem;font-weight:700;color:var(--tx)}
/* Conf bar */
.cbw{margin-bottom:.9rem}
.cbt{display:flex;justify-content:space-between;margin-bottom:6px}
.cbl{font-size:.6rem;color:var(--tx3);font-weight:700;text-transform:uppercase;letter-spacing:.09em}
.cbv{font-size:.88rem;font-weight:800;color:var(--g);text-shadow:0 0 12px var(--gg)}
.cbg{height:6px;border-radius:99px;background:var(--bg4);overflow:hidden;box-shadow:inset 0 1px 4px rgba(0,0,0,.2)}
.cbf{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--g3),var(--g));transition:width 1.3s cubic-bezier(.22,1,.36,1);box-shadow:0 0 10px var(--gg);width:0}
/* Donut */
.donut-wrap{display:flex;align-items:center;justify-content:center;gap:1.5rem;margin:.5rem 0 1rem;flex-wrap:wrap}
.donut-svg{width:110px;height:110px;flex-shrink:0;filter:drop-shadow(0 0 16px var(--gs))}
.donut-legend{display:flex;flex-direction:column;gap:6px}
.dl-item{display:flex;align-items:center;gap:7px;font-size:.74rem;font-weight:600;color:var(--tx2)}
.dl-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
/* Preds */
.preds{display:flex;flex-direction:column;gap:5px}
.pr{display:flex;align-items:center;gap:8px;padding:.6rem .88rem;background:color-mix(in srgb,var(--bg3) 72%,transparent);border:1px solid var(--brd);border-radius:10px;transition:all .25s;opacity:0;transform:translateX(-10px);animation:prIn .4s forwards;backdrop-filter:blur(8px)}
.pr:nth-child(1){animation-delay:.04s}.pr:nth-child(2){animation-delay:.09s}
.pr:nth-child(3){animation-delay:.14s}.pr:nth-child(4){animation-delay:.19s}.pr:nth-child(5){animation-delay:.24s}
@keyframes prIn{to{opacity:1;transform:none}}
.pr:hover{background:var(--bg4);border-color:var(--brd2);transform:translateX(5px);box-shadow:0 4px 14px rgba(0,0,0,.1)}
.prk{width:20px;height:20px;border-radius:6px;background:var(--bg4);border:1px solid var(--brd2);display:grid;place-items:center;font-size:.6rem;font-weight:800;color:var(--tx3);flex-shrink:0}
.pr:first-child .prk{background:var(--gd);border-color:var(--gg);color:var(--g);box-shadow:0 0 8px var(--gs)}
.prn{flex:1;font-size:.75rem;font-weight:600;color:var(--tx)}
.mbar{flex:0 0 48px;height:3px;border-radius:99px;background:var(--bg4);overflow:hidden}
.mfill{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--g3),var(--g));transition:width .95s ease}
.ppct{font-size:.7rem;font-weight:800;color:var(--tx2);min-width:36px;text-align:right}
.ppill{font-size:.58rem;font-weight:800;letter-spacing:.07em;text-transform:uppercase;padding:2px 7px;border-radius:99px;flex-shrink:0}
.ppH{background:var(--gd);color:var(--g);border:1px solid var(--gg)}
.ppD{background:var(--rd);color:var(--r);border:1px solid rgba(255,107,122,.22)}
/* Action row */
.arow{display:flex;gap:6px;margin-top:.9rem}
.actb{flex:1;display:flex;align-items:center;justify-content:center;gap:5px;padding:.58rem;border-radius:9px;font-family:inherit;font-size:.7rem;font-weight:700;cursor:pointer;border:1px solid var(--brd2);background:color-mix(in srgb,var(--bg3) 75%,transparent);color:var(--tx2);transition:all .24s;backdrop-filter:blur(8px)}
.actb:hover{background:var(--bg4);color:var(--tx);border-color:var(--brd3);transform:translateY(-2px);box-shadow:0 6px 18px rgba(0,0,0,.14)}
.actb:active{transform:translateY(0) scale(.97)}
/* ══ REPORT CARD ══ */
.report-box{background:color-mix(in srgb,var(--bg3) 68%,transparent);border:1px solid var(--brd2);border-radius:12px;padding:1rem;margin-top:.9rem;animation:fUp .4s both;backdrop-filter:blur(12px)}
.report-title{font-size:.78rem;font-weight:800;color:var(--tx);margin-bottom:.7rem;display:flex;align-items:center;gap:7px;flex-wrap:wrap}
.sev-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:99px;font-size:.62rem;font-weight:800;letter-spacing:.07em}
.sev-low{background:var(--gd);color:var(--g);border:1px solid var(--gg)}
.sev-med{background:var(--yd);color:var(--y);border:1px solid var(--y)}
.sev-high{background:var(--rd);color:var(--r);border:1px solid var(--r)}
.sugg-list{list-style:none;display:flex;flex-direction:column;gap:6px}
.sugg-item{display:flex;align-items:flex-start;gap:8px;font-size:.76rem;color:var(--tx2);line-height:1.56;padding:.5rem .6rem;border-radius:8px;transition:background .2s}
.sugg-item:hover{background:color-mix(in srgb,var(--bg4) 70%,transparent)}
.sugg-ico{font-size:.95rem;flex-shrink:0;margin-top:1px}
.sugg-item b{color:var(--tx)}
/* ══ HISTORY ══ */
.hl{display:flex;flex-direction:column;gap:5px;max-height:380px;overflow-y:auto;padding-right:2px}
.hl::-webkit-scrollbar{width:3px}
.hl::-webkit-scrollbar-thumb{background:var(--brd2);border-radius:99px}
.hi{display:flex;align-items:center;gap:8px;padding:.6rem .88rem;border-radius:10px;background:color-mix(in srgb,var(--bg3) 72%,transparent);border:1px solid var(--brd);cursor:pointer;transition:all .22s;animation:fUp .28s both;backdrop-filter:blur(8px)}
.hi:hover{border-color:var(--brd2);background:var(--bg4);transform:translateX(4px);box-shadow:0 4px 14px rgba(0,0,0,.1)}
.hth{width:36px;height:36px;border-radius:7px;object-fit:cover;flex-shrink:0;border:1px solid var(--brd);transition:transform .25s}
.hi:hover .hth{transform:scale(1.1) rotate(-2deg)}
.hi-info{flex:1;min-width:0}
.hin{font-size:.73rem;font-weight:700;color:var(--tx);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.him{font-size:.6rem;color:var(--tx3);margin-top:1px}
.hdot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.dG{background:var(--g);box-shadow:0 0 7px var(--gg)}.dR{background:var(--r);box-shadow:0 0 7px rgba(255,107,122,.4)}
.empty{text-align:center;padding:1.8rem .5rem;color:var(--tx3)}
.empt-e{font-size:1.5rem;margin-bottom:.4rem;opacity:.3}
#cwrap{margin-top:.8rem;height:85px;display:none}
/* ══ STATS ══ */
.sg{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.sc{background:color-mix(in srgb,var(--bg3) 76%,transparent);border:1px solid var(--brd);border-radius:10px;padding:.72rem;text-align:center;transition:all .24s;backdrop-filter:blur(8px)}
.sc:hover{border-color:var(--brd2);transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,.12)}
.scl{font-size:.58rem;color:var(--tx3);font-weight:700;text-transform:uppercase;letter-spacing:.09em;margin-bottom:3px}
.scv{font-size:1.2rem;font-weight:800;color:var(--tx)}
.hb{height:4px;border-radius:99px;background:var(--bg4);overflow:hidden;margin-top:7px}
.hbf{height:100%;border-radius:99px;background:linear-gradient(90deg,var(--g3),var(--g));transition:width .9s ease;box-shadow:0 0 8px var(--gg)}
/* ══ TIPS ══ */
.tip{display:flex;align-items:flex-start;gap:9px;padding:.6rem 0;border-bottom:1px solid var(--brd);transition:all .22s}
.tip:last-child{border:none;padding-bottom:0}
.tip:hover{padding-left:5px}
.tipn{width:18px;height:18px;border-radius:5px;background:color-mix(in srgb,var(--bg3) 78%,transparent);border:1px solid var(--brd2);display:grid;place-items:center;font-size:.6rem;font-weight:800;color:var(--tx3);flex-shrink:0;transition:all .22s}
.tip:hover .tipn{background:var(--gd);border-color:var(--gg);color:var(--g);box-shadow:0 0 10px var(--gs)}
.tipt{font-size:.73rem;color:var(--tx2);line-height:1.58}.tipt b{color:var(--tx)}
/* ══ FEEDBACK ══ */
.fb-star-row{display:flex;gap:8px;justify-content:center;margin-bottom:1rem}
.fbstar{font-size:1.75rem;cursor:pointer;transition:transform .22s cubic-bezier(.34,1.56,.64,1),filter .22s;filter:grayscale(1) opacity(.32)}
.fbstar.on,.fbstar:hover{filter:drop-shadow(0 0 10px var(--gold));transform:scale(1.32)}
.fbtag-row{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:1rem;justify-content:center}
.fbtag{padding:5px 12px;border-radius:99px;border:1px solid var(--brd2);background:color-mix(in srgb,var(--bg3) 76%,transparent);color:var(--tx2);font-size:.71rem;font-weight:600;cursor:pointer;transition:all .22s;backdrop-filter:blur(6px)}
.fbtag:hover,.fbtag.on{background:var(--gd);color:var(--g);border-color:var(--gg);box-shadow:0 0 12px var(--gs)}
textarea.fbtxt{width:100%;background:color-mix(in srgb,var(--bg3) 76%,transparent);border:1px solid var(--brd2);border-radius:10px;padding:.82rem;color:var(--tx);font-family:inherit;font-size:.78rem;resize:vertical;min-height:72px;transition:border-color .22s,box-shadow .22s;outline:none;backdrop-filter:blur(8px)}
textarea.fbtxt:focus{border-color:var(--g);box-shadow:0 0 0 3px var(--gd)}
.fbsend{margin-top:.75rem;width:100%;padding:.74rem;background:linear-gradient(135deg,var(--gd),color-mix(in srgb,var(--gd) 55%,transparent));color:var(--g);border:1px solid var(--gg);border-radius:10px;font-family:inherit;font-size:.8rem;font-weight:800;cursor:pointer;transition:all .25s;backdrop-filter:blur(10px)}
.fbsend:hover{background:linear-gradient(135deg,var(--g),var(--g2));color:#030d05;transform:translateY(-1px);box-shadow:0 8px 26px rgba(93,255,160,.24)}
/* ══ TUTORIAL ══ */
#tut{position:fixed;inset:0;z-index:500;display:none}
.tut-bg{position:absolute;inset:0;background:rgba(0,0,0,.82);backdrop-filter:blur(8px)}
.tut-box{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) scale(.9);background:color-mix(in srgb,var(--bg2) 94%,transparent);border:1px solid var(--brd2);border-radius:22px;padding:2.3rem;max-width:400px;width:calc(100% - 2rem);box-shadow:var(--shb);animation:tutIn .44s cubic-bezier(.34,1.56,.64,1) forwards;backdrop-filter:blur(24px)}
@keyframes tutIn{to{transform:translate(-50%,-50%) scale(1)}}
.tut-step{display:none}.tut-step.on{display:block}
.tut-ico{font-size:3.2rem;text-align:center;margin-bottom:.85rem;animation:bounce .68s ease infinite alternate;filter:drop-shadow(0 0 18px var(--gg))}
@keyframes bounce{to{transform:translateY(-8px)}}
.tut-h{font-family:\'Instrument Serif\',serif;font-size:1.58rem;text-align:center;margin-bottom:.6rem;color:var(--tx);line-height:1.14}
.tut-h em{font-style:italic;color:var(--g)}
.tut-p{font-size:.82rem;color:var(--tx2);text-align:center;line-height:1.7;margin-bottom:1.2rem}
.tut-dots{display:flex;justify-content:center;gap:6px;margin-bottom:1.2rem}
.tut-dot{width:7px;height:7px;border-radius:50%;background:var(--brd2);transition:all .28s}
.tut-dot.on{background:var(--g);width:24px;border-radius:99px;box-shadow:0 0 10px var(--gg)}
.tut-btns{display:flex;gap:8px}
.tut-skip{flex:1;padding:.66rem;border-radius:10px;border:1px solid var(--brd2);background:transparent;color:var(--tx2);font-family:inherit;font-size:.78rem;font-weight:700;cursor:pointer;transition:all .22s}
.tut-skip:hover{background:var(--bg3);color:var(--tx)}
.tut-next{flex:2;padding:.66rem;border-radius:10px;border:none;background:linear-gradient(135deg,var(--g),var(--g2));color:#030d05;font-family:inherit;font-size:.8rem;font-weight:800;cursor:pointer;transition:all .24s;box-shadow:0 4px 18px rgba(93,255,160,.22)}
.tut-next:hover{transform:translateY(-1px);box-shadow:0 8px 28px rgba(93,255,160,.3)}
/* ══ TOAST ══ */
#toast{position:fixed;bottom:1.8rem;left:50%;transform:translateX(-50%) translateY(70px);background:color-mix(in srgb,var(--bg2) 92%,transparent);border:1px solid var(--brd2);border-radius:99px;padding:.55rem 1.4rem;font-size:.75rem;font-weight:700;color:var(--tx);z-index:999;opacity:0;transition:all .42s cubic-bezier(.34,1.56,.64,1);pointer-events:none;white-space:nowrap;box-shadow:var(--shb);backdrop-filter:blur(18px)}
#toast.show{opacity:1;transform:translateX(-50%) translateY(0)}
/* ══ RIPPLE ══ */
.rhost{position:relative;overflow:hidden}
.rip{position:absolute;border-radius:50%;background:rgba(93,255,160,.14);pointer-events:none;transform:scale(0);animation:ripA .58s linear forwards}
@keyframes ripA{to{transform:scale(5);opacity:0}}
/* ══ RESPONSIVE ══ */
@media(max-width:480px){
  .stats{gap:.9rem}.stn{font-size:1.15rem}
  .hero h1{font-size:2rem}.hero p{font-size:.88rem}
  .cbd{padding:.85rem}.chd{padding:.75rem 1rem}
  .tabs{gap:2px}.tab{font-size:.67rem;padding:.45rem .48rem}
  .nav-r .nbadge{display:none}
  .ig2{grid-template-columns:1fr}
  .arow .actb span{display:none}
  .q-text{font-size:1.05rem}
}
/* ══ FOOTER ══ */
footer{text-align:center;padding:1.8rem 0 1.2rem;color:var(--tx3);font-size:.68rem;border-top:1px solid var(--brd);margin-top:2rem}
footer b{color:var(--tx2)}

/* ══ DEVELOPER CARDS ══ */
.dev-row{display:flex;flex-direction:column;gap:10px}
.dev-card{display:flex;align-items:center;gap:12px;padding:.85rem;background:color-mix(in srgb,var(--bg3) 70%,transparent);border:1px solid var(--brd);border-radius:12px;transition:all .25s;cursor:default}
.dev-card:hover{border-color:var(--brd2);transform:translateX(4px);box-shadow:0 4px 16px rgba(0,0,0,.12)}
.dev-avatar{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,var(--g3),var(--g));display:grid;place-items:center;font-size:1.1rem;font-weight:800;color:#030d05;flex-shrink:0;box-shadow:0 4px 12px rgba(93,255,160,.2)}
.dev-info{flex:1;min-width:0}
.dev-name{font-size:.84rem;font-weight:800;color:var(--tx);margin-bottom:2px}
.dev-role{font-size:.65rem;color:var(--tx3);font-weight:600;margin-bottom:4px}
.dev-mail{font-size:.68rem;color:var(--g);text-decoration:none;font-weight:600;transition:opacity .2s;word-break:break-all}
.dev-mail:hover{opacity:.7}
/* ══ FLOATING PARTICLES (hero) ══ */
.hero-particles{position:absolute;inset:0;pointer-events:none;overflow:hidden;z-index:0}
.hp{position:absolute;border-radius:50%;background:var(--g);animation:hpFloat linear infinite;opacity:0}
@keyframes hpFloat{0%{transform:translateY(100%) scale(0);opacity:0}10%{opacity:.6}90%{opacity:.2}100%{transform:translateY(-120vh) scale(1.2) rotate(180deg);opacity:0}}
/* ══ CARD ENTRANCE ANIMATION ══ */
.card{animation:cardEntrance .5s cubic-bezier(.22,1,.36,1) both}
@keyframes cardEntrance{from{opacity:0;transform:translateY(16px) scale(.98)}to{opacity:1;transform:none}}
.col .card:nth-child(1){animation-delay:.05s}
.col .card:nth-child(2){animation-delay:.12s}
.col .card:nth-child(3){animation-delay:.19s}
/* ══ SCAN RESULT ENTRANCE ══ */
#rCard.show-anim{animation:resultPop .45s cubic-bezier(.34,1.56,.64,1)}
@keyframes resultPop{from{opacity:0;transform:scale(.94) translateY(10px)}to{opacity:1;transform:none}}
/* ══ HISTORY COUNT BADGE ══ */
.hist-badge{display:inline-flex;align-items:center;justify-content:center;min-width:18px;height:18px;border-radius:99px;background:var(--g);color:#030d05;font-size:.6rem;font-weight:800;padding:0 5px;margin-left:6px;transition:transform .3s cubic-bezier(.34,1.56,.64,1)}
.hist-badge.bump{transform:scale(1.4)}
/* ══ NAV SCAN COUNT ══ */
.scan-count{font-size:.62rem;font-weight:800;color:var(--g);background:var(--gd);border:1px solid var(--gg);border-radius:99px;padding:2px 8px;transition:all .3s}
/* ══ PROGRESS RING on scan button ══ */
.abtn-progress{position:absolute;top:-2px;left:-2px;right:-2px;bottom:-2px;border-radius:13px;border:2px solid transparent;pointer-events:none;transition:border-color .3s}
.abtn.loading .abtn-progress{border-color:var(--g);animation:borderSpin 1s linear infinite}
@keyframes borderSpin{0%{clip-path:inset(0 100% 0 0)}100%{clip-path:inset(0 0% 0 0)}}

</style>
</head>
<body>

<div id="cD"></div><div id="cR"></div><div id="cT"></div>
<canvas id="bgC"></canvas>
<div id="farmerBg"></div>

<!-- ══ TUTORIAL ══ -->
<div id="tut">
  <div class="tut-bg" onclick="closeTut()"></div>
  <div class="tut-box">
    <div class="tut-step on" id="ts0">
      <div class="tut-ico">🌿</div>
      <div class="tut-h">Welcome to <em>LeafScan</em></div>
      <p class="tut-p">Your AI-powered farming assistant. Detect crop diseases instantly and get practical treatment advice — in your language.</p>
    </div>
    <div class="tut-step" id="ts1">
      <div class="tut-ico">📷</div>
      <div class="tut-h"><em>Upload</em> a Leaf Photo</div>
      <p class="tut-p">Take a clear photo of the affected leaf in natural daylight. Drag & drop it or click the upload zone. Works with JPG, PNG, or WEBP.</p>
    </div>
    <div class="tut-step" id="ts2">
      <div class="tut-ico">🔬</div>
      <div class="tut-h">Get Instant <em>Diagnosis</em></div>
      <p class="tut-p">Click "Analyze Leaf" — our AI scans it in seconds and tells you: is it healthy or diseased? What disease? How serious?</p>
    </div>
    <div class="tut-step" id="ts3">
      <div class="tut-ico">💊</div>
      <div class="tut-h"><em>Treatment</em> Suggestions</div>
      <p class="tut-p">Get a personalized report with practical steps — what spray to use, how often, preventive measures, and when to consult an expert.</p>
    </div>
    <div class="tut-step" id="ts4">
      <div class="tut-ico">🌾</div>
      <div class="tut-h">You're All <em>Set!</em></div>
      <p class="tut-p">Switch language using the top-right button. Use dark/light mode toggle for comfort. Your scan history is saved in this session.</p>
    </div>
    <div class="tut-dots">
      <div class="tut-dot on" id="td0"></div><div class="tut-dot" id="td1"></div>
      <div class="tut-dot" id="td2"></div><div class="tut-dot" id="td3"></div><div class="tut-dot" id="td4"></div>
    </div>
    <div class="tut-btns">
      <button class="tut-skip" onclick="closeTut()">Skip Tour</button>
      <button class="tut-next" id="tutNext" onclick="nextTut()">Next →</button>
    </div>
  </div>
</div>

<div class="page">

<!-- ══ NAV ══ -->
<nav>
  <a class="logo" href="#"><div class="logo-m">🌿</div><span>LeafScan</span></a>
  <div class="nav-r">
    <div class="nbadge"><span class="ldot"></span><span data-i="nav_live">AI Online</span></div>
    <span class="scan-count" id="navCount" style="display:none">0 scans</span>
    <button class="cb" id="tutBtn" onclick="openTut()">❓ <span data-i="tutorial">Tutorial</span></button>
    <button class="cb" id="themeBtn" onclick="toggleTheme()"><span id="tIco">🌙</span><span id="tTxt">Dark</span></button>
    <div class="lw" id="lw">
      <button class="cb" id="lBtn" onclick="toggleLD()"><span id="lFlag">🇺🇸</span><span id="lNm">EN</span></button>
      <div class="ldrop" id="lDrop">
        <div class="lopt sel" onclick="setLang('en')">🇺🇸 English</div>
        <div class="lopt" onclick="setLang('hi')">🇮🇳 हिंदी</div>
        <div class="lopt" onclick="setLang('bn')">🇮🇳 বাংলা</div>
        <div class="lopt" onclick="setLang('ta')">🇮🇳 தமிழ்</div>
        <div class="lopt" onclick="setLang('te')">🇮🇳 తెలుగు</div>
        <div class="lopt" onclick="setLang('mr')">🇮🇳 मराठी</div>
        <div class="lopt" onclick="setLang('gu')">🇮🇳 ગુજરાતી</div>
        <div class="lopt" onclick="setLang('pa')">🇮🇳 ਪੰਜਾਬੀ</div>
      </div>
    </div>
  </div>
</nav>

<!-- ══ HERO ══ -->
<div class="hero" style="position:relative">
  <div class="hero-particles" id="heroParts"></div>
  <div class="heyebrow">🔬 <span data-i="eyebrow">Plant Disease Detection</span></div>
  <h1 data-i="h1">Diagnose your <em>crops</em> instantly</h1>
  <p data-i="hero_p">Upload any leaf photo — AI identifies diseases & plant health in seconds.</p>

  <!-- MOTIVATIONAL QUOTE BANNER -->
  <div class="qbanner" onclick="newQuote()" title="Click for new quote">
    <div class="q-inner">
      <span class="q-leaf">🌾</span>
      <div style="flex:1;text-align:left">
        <div class="q-text" id="qText">Loading...</div>
        <div class="q-author" id="qAuthor"></div>
      </div>
      <span class="q-refresh">↻</span>
    </div>
  </div>

  <!-- QUICK FACT CHIPS -->
  <div class="fact-strip" id="factStrip"></div>

  <div class="stats">
    <div class="stat"><div class="stn"><em>27</em></div><div class="stl" data-i="s1">Disease Classes</div></div>
    <div class="stsep"></div>
    <div class="stat"><div class="stn"><em>2.5K</em>+</div><div class="stl" data-i="s2">Training Images</div></div>
    <div class="stsep"></div>
    <div class="stat"><div class="stn"><em>86</em>%</div><div class="stl" data-i="s3">Val Accuracy</div></div>
    <div class="stsep"></div>
    <div class="stat"><div class="stn">CPU</div><div class="stl" data-i="s4">Optimized</div></div>
  </div>
</div>

<!-- ══ TABS ══ -->
<div class="tabs">
  <button class="tab on" onclick="showTab('scan')" data-i="tab_scan">🔍 Scan</button>
  <button class="tab" onclick="showTab('history')" data-i="tab_hist">🕒 History<span class="hist-badge" id="histBadge" style="display:none">0</span></button>
  <button class="tab" onclick="showTab('stats')" data-i="tab_stats">📊 Stats</button>
  <button class="tab" onclick="showTab('tips')" data-i="tab_tips">💡 Tips</button>
  <button class="tab" onclick="showTab('feedback')" data-i="tab_fb">⭐ Feedback</button>
</div>

<!-- ══ TAB: SCAN ══ -->
<div class="tab-panel on" id="tp-scan">
<div class="grid">
  <div class="col">
    <div class="card">
      <div class="chd"><div class="xico">📷</div><div><div class="cttl" data-i="upload_title">Upload Leaf</div><div class="csub" data-i="upload_sub">JPG · PNG · WEBP</div></div></div>
      <div class="cbd">
        <div class="dz rhost" id="dz" onclick="document.getElementById('fI').click()">
          <div class="dz-orb">🍃</div>
          <div class="dzt" data-i="dzt">Drop image here</div>
          <div class="dzs" data-i="dzs"><b>Click to browse</b> or drag & drop</div>
          <input type="file" id="fI" accept="image/*">
        </div>
        <!-- CAMERA ROW -->
        <div class="cam-row">
          <button class="cam-btn rhost" onclick="openCamera()"><span class="cam-ico">📸</span><span data-i="take_photo">Take Photo</span></button>
          <button class="cam-btn cam-alt rhost" onclick="document.getElementById('fI').click()"><span class="cam-ico">🖼</span><span data-i="choose_file">Choose File</span></button>
        </div>
        <!-- CAMERA MODAL -->
        <div id="camModal" style="display:none">
          <div class="cam-box">
            <div class="cam-hd"><span style="font-size:.8rem;font-weight:700;color:var(--tx)">📸 <span data-i="camera_title">Camera</span></span><button class="cam-close" onclick="closeCamera()">✕</button></div>
            <div class="cam-view"><video id="camVideo" autoplay playsinline muted></video>
              <div class="cam-overlay"><div class="cam-guide">
                <div class="cg-corner tl"></div><div class="cg-corner tr"></div>
                <div class="cg-corner bl"></div><div class="cg-corner br"></div>
                <span class="cg-hint" data-i="cam_hint">Position leaf inside frame</span>
              </div></div>
            </div>
            <div class="cam-foot">
              <button class="cam-flip" onclick="flipCamera()" title="Flip">🔄</button>
              <button class="cam-snap rhost" onclick="snapPhoto()"><div class="snap-ring"></div></button>
              <button class="cam-flip" onclick="closeCamera()">✕</button>
            </div>
          </div>
          <canvas id="camCanvas" style="display:none"></canvas>
        </div>
        </div>
        <div id="pW"><img id="pImg" src="" alt=""><div class="pover"></div>
          <div class="pchips"><span class="pchip pcn" id="fnC">—</span><span class="pchip pcc" onclick="document.getElementById('fI').click()" data-i="change">Change ↺</span></div>
          <div id="valBadge" style="display:none;position:absolute;bottom:8px;left:8px;z-index:3"></div>
        </div>
          <div class="pchips"><span class="pchip pcn" id="fnC">—</span><span class="pchip pcc" onclick="document.getElementById('fI').click()" data-i="change">Change ↺</span></div>
        </div>
        <button class="abtn rhost" id="aBtn" disabled onclick="analyze()">
          <span data-i="analyze_btn">Analyze Leaf</span><span class="aarrow">→</span>
        </button>
      </div>
    </div>

    <div id="ldr">
      <div class="sbox"><img id="sImg" class="simg" src="" alt="">
        <div class="corners"><span></span><span></span><span></span><span></span></div>
        <div class="sbeam"></div>
      </div>
      <div class="sfoot">
        <div class="slbl"><span data-i="scanning">SCANNING</span><span><span style="animation:blink 1.2s infinite">.</span><span style="animation:blink 1.2s .15s infinite">.</span><span style="animation:blink 1.2s .3s infinite">.</span></span></div>
        <div class="spct" id="sPct">0%</div>
      </div>
      <div class="srow">
        <span class="step" id="s0" data-i="step0">Loading</span>
        <span class="step" id="s1" data-i="step1">Preprocessing</span>
        <span class="step" id="s2" data-i="step2">Features</span>
        <span class="step" id="s3" data-i="step3">Classifying</span>
        <span class="step" id="s4" data-i="step4">Report</span>
      </div>
    </div>
    <style>@keyframes blink{0%,100%{opacity:.2}50%{opacity:1}}</style>

    <div class="card" id="rCard">
      <div class="chd"><div class="xico">🔬</div><div><div class="cttl" data-i="result_title">Analysis Result</div><div class="csub" id="rMeta">—</div></div></div>
      <div class="cbd">
        <div class="rhero" id="rHero"><div class="rorb" id="rOrb"></div>
          <div><div class="rtag" id="rTag"></div><div class="rnm" id="rNm"></div></div>
        </div>
        <div class="ig2">
          <div class="ic"><div class="icl" data-i="plant_lbl">Plant</div><div class="icv" id="rPlant">—</div></div>
          <div class="ic"><div class="icl" data-i="disease_lbl">Disease</div><div class="icv" id="rDis" style="font-size:.74rem">—</div></div>
        </div>

        <!-- DONUT CHART -->
        <div class="donut-wrap">
          <svg class="donut-svg" viewBox="0 0 36 36" id="donutSvg">
            <circle cx="18" cy="18" r="15.915" fill="none" stroke="var(--bg4)" stroke-width="3.5"/>
            <circle cx="18" cy="18" r="15.915" fill="none" stroke="var(--g)" stroke-width="3.5"
              stroke-dasharray="0 100" stroke-dashoffset="25" id="donutArc"
              style="transition:stroke-dasharray 1.2s cubic-bezier(.22,1,.36,1);stroke-linecap:round"/>
            <text x="18" y="18" text-anchor="middle" dominant-baseline="middle" font-size="7" font-weight="800" fill="var(--g)" id="donutTxt">0%</text>
          </svg>
          <div class="donut-legend" id="donutLeg"></div>
        </div>

        <div class="cbw">
          <div class="cbt"><span class="cbl" data-i="conf_lbl">Confidence</span><span class="cbv" id="cVal">0%</span></div>
          <div class="cbg"><div class="cbf" id="cFill"></div></div>
        </div>
        <div class="preds" id="predList"></div>

        <!-- EDUCATIONAL TOOLTIPS ROW -->
        <div id="eduRow" style="display:none;margin:.9rem 0 0">
          <div style="font-size:.64rem;color:var(--tx3);font-weight:700;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px">💡 Did You Know?</div>
          <div class="fact-strip" id="eduFacts"></div>
        </div>

        <!-- PERSONALIZED REPORT -->
        <div class="report-box" id="reportBox" style="display:none">
          <div class="report-title">
            📋 <span data-i="report_title">Personalized Report</span>
            <span class="sev-badge" id="sevBadge"></span>
          </div>
          <ul class="sugg-list" id="suggList"></ul>
        </div>

        <div class="arow">
          <button class="actb rhost" onclick="copyRes()">📋 <span data-i="copy">Copy</span></button>
          <button class="actb rhost" onclick="dlRes()">⬇ <span data-i="save">Save</span></button>
          <button class="actb rhost" onclick="shareRes()">↗ <span data-i="share">Share</span></button>
          <button class="actb rhost" onclick="printReport()">🖨 <span data-i="print">Print</span></button>
        </div>
      </div>
    </div>
  </div>

  <div class="col">
    <div class="card">
      <div class="chd"><div class="xico">🕒</div><div><div class="cttl" data-i="hist_title">Scan History</div><div class="csub" id="hCnt" data-i="hist_sub">0 scans</div></div></div>
      <div class="cbd" style="padding:.75rem 1rem">
        <div class="hl" id="hList"><div class="empty"><div class="empt-e">🌱</div><span data-i="no_scans">No scans yet</span></div></div>
        <div id="cwrap"><canvas id="hChart"></canvas></div>
      </div>
    </div>
    <div class="card">
      <div class="chd"><div class="xico">💡</div><div><div class="cttl" data-i="tips_title">Quick Tips</div><div class="csub" data-i="tips_sub">Better accuracy</div></div></div>
      <div class="cbd">
        <div class="tip"><div class="tipn">1</div><div class="tipt" data-i="tip1">Use <b>natural daylight</b> — avoid flash</div></div>
        <div class="tip"><div class="tipn">2</div><div class="tipt" data-i="tip2"><b>Fill the frame</b> with the affected leaf</div></div>
        <div class="tip"><div class="tipn">3</div><div class="tipt" data-i="tip3">Keep image <b>sharp and focused</b></div></div>
        <div class="tip"><div class="tipn">4</div><div class="tipt" data-i="tip4">Scan <b>multiple leaves</b> to confirm</div></div>
        <div class="tip"><div class="tipn">5</div><div class="tipt" data-i="tip5">Best for: <b>Apple, Tomato, Potato, Corn, Grape</b></div></div>
      </div>
    </div>
  </div>
</div>
</div>

<!-- ══ TAB: HISTORY ══ -->
<div class="tab-panel" id="tp-history">
  <div class="card"><div class="chd"><div class="xico">🕒</div><div><div class="cttl" data-i="hist_title">Scan History</div><div class="csub" id="hCnt2">All sessions</div></div></div>
    <div class="cbd">
      <div class="hl" id="hListFull" style="max-height:500px"><div class="empty"><div class="empt-e">🌱</div><span data-i="no_scans">No scans yet</span></div></div>
      <div style="height:160px;margin-top:1rem"><canvas id="hChart2"></canvas></div>
    </div>
  </div>
</div>

<!-- ══ TAB: STATS ══ -->
<div class="tab-panel" id="tp-stats">
  <div class="grid">
    <div class="col">
      <div class="card"><div class="chd"><div class="xico">📊</div><div><div class="cttl" data-i="stats_title">Session Stats</div><div class="csub" data-i="stats_sub">Live counters</div></div></div>
        <div class="cbd">
          <div class="sg">
            <div class="sc"><div class="scl" data-i="total">Total</div><div class="scv" id="sT">0</div></div>
            <div class="sc"><div class="scl" data-i="healthy_lbl">Healthy</div><div class="scv" style="color:var(--g)" id="sH">0</div></div>
            <div class="sc"><div class="scl" data-i="diseased_lbl">Diseased</div><div class="scv" style="color:var(--r)" id="sD">0</div></div>
          </div>
          <div class="hb"><div class="hbf" id="hBF" style="width:0%"></div></div>
          <div style="display:flex;justify-content:space-between;margin-top:5px">
            <span style="font-size:.6rem;color:var(--g);font-weight:700" data-i="healthy_pct">Healthy %</span>
            <span style="font-size:.6rem;color:var(--tx3);font-weight:700" id="hPct">—</span>
          </div>
          <div style="height:160px;margin-top:1rem"><canvas id="pieChart"></canvas></div>
        </div>
      </div>
    </div>
    <div class="col">
      <div class="card"><div class="chd"><div class="xico">🏆</div><div><div class="cttl" data-i="top_diseases">Top Diseases Found</div><div class="csub" data-i="this_session">This session</div></div></div>
        <div class="cbd"><div id="diseaseRank" class="preds"><div class="empty"><div class="empt-e">🔬</div><span data-i="no_scans">No data yet</span></div></div></div>
      </div>
    </div>
  </div>
</div>

<!-- ══ TAB: TIPS ══ -->
<div class="tab-panel" id="tp-tips">
  <div class="grid">
    <div class="col">
      <div class="card"><div class="chd"><div class="xico">📸</div><div><div class="cttl" data-i="photo_tips">Photo Tips</div><div class="csub">Best practices</div></div></div>
        <div class="cbd">
          <div class="tip"><div class="tipn">1</div><div class="tipt" data-i="tip1">Use <b>natural daylight</b> — avoid flash shadows</div></div>
          <div class="tip"><div class="tipn">2</div><div class="tipt" data-i="tip2"><b>Fill the frame</b> with the affected leaf</div></div>
          <div class="tip"><div class="tipn">3</div><div class="tipt" data-i="tip3">Keep image <b>sharp and in focus</b></div></div>
          <div class="tip"><div class="tipn">4</div><div class="tipt" data-i="tip4">Scan <b>multiple leaves</b> to confirm diagnosis</div></div>
          <div class="tip"><div class="tipn">5</div><div class="tipt" data-i="tip5">Best for: <b>Apple, Tomato, Potato, Corn, Grape</b></div></div>
          <div class="tip"><div class="tipn">6</div><div class="tipt" data-i="tip6">Avoid <b>wet or dirty</b> leaves — wipe gently first</div></div>
          <div class="tip"><div class="tipn">7</div><div class="tipt" data-i="tip7">Scan early morning for <b>best visibility</b></div></div>
        </div>
      </div>
    </div>
    <div class="col">
      <div class="card"><div class="chd"><div class="xico">🌾</div><div><div class="cttl" data-i="general_tips">General Advice</div><div class="csub">Crop care</div></div></div>
        <div class="cbd">
          <div class="tip"><div class="tipn">💧</div><div class="tipt" data-i="gtip1"><b>Water properly</b> — avoid overwatering. Wet soil causes fungal diseases</div></div>
          <div class="tip"><div class="tipn">🌬</div><div class="tipt" data-i="gtip2"><b>Good air circulation</b> — don't crowd plants. Space them well</div></div>
          <div class="tip"><div class="tipn">✂️</div><div class="tipt" data-i="gtip3"><b>Remove infected leaves</b> immediately to stop spreading</div></div>
          <div class="tip"><div class="tipn">🧪</div><div class="tipt" data-i="gtip4"><b>Neem oil spray</b> — effective organic prevention for many diseases</div></div>
          <div class="tip"><div class="tipn">📅</div><div class="tipt" data-i="gtip5"><b>Rotate crops</b> every season to prevent soil-borne diseases</div></div>
          <div class="tip"><div class="tipn">🔍</div><div class="tipt" data-i="gtip6"><b>Inspect weekly</b> — early detection saves the entire crop</div></div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ══ TAB: FEEDBACK ══ -->
<div class="tab-panel" id="tp-feedback">
  <div class="grid">
    <div class="col">
      <div class="card"><div class="chd"><div class="xico">⭐</div><div><div class="cttl" data-i="fb_title">Rate LeafScan</div><div class="csub" data-i="fb_sub">Your feedback helps us improve</div></div></div>
        <div class="cbd">
          <p style="font-size:.78rem;color:var(--tx2);margin-bottom:.9rem;text-align:center" data-i="fb_how">How was your experience?</p>
          <div class="fb-star-row" id="starRow">
            <span class="fbstar" data-v="1" onclick="setStar(1)">⭐</span>
            <span class="fbstar" data-v="2" onclick="setStar(2)">⭐</span>
            <span class="fbstar" data-v="3" onclick="setStar(3)">⭐</span>
            <span class="fbstar" data-v="4" onclick="setStar(4)">⭐</span>
            <span class="fbstar" data-v="5" onclick="setStar(5)">⭐</span>
          </div>
          <p style="font-size:.78rem;color:var(--tx2);margin-bottom:.6rem;text-align:center" data-i="fb_what">What did you like?</p>
          <div class="fbtag-row" id="fbTags">
            <span class="fbtag" onclick="toggleTag(this)" data-i="fbt1">Easy to use</span>
            <span class="fbtag" onclick="toggleTag(this)" data-i="fbt2">Accurate results</span>
            <span class="fbtag" onclick="toggleTag(this)" data-i="fbt3">Fast scanning</span>
            <span class="fbtag" onclick="toggleTag(this)" data-i="fbt4">Helpful suggestions</span>
            <span class="fbtag" onclick="toggleTag(this)" data-i="fbt5">Good UI</span>
            <span class="fbtag" onclick="toggleTag(this)" data-i="fbt6">Multi-language</span>
          </div>
          <textarea class="fbtxt" id="fbTxt" placeholder="Write your feedback here..." rows="3"></textarea>
          <button class="fbsend" onclick="sendFeedback()">📤 <span data-i="fb_send">Submit Feedback</span></button>
        </div>
      </div>
    </div>
    <div class="col">
      <div class="card"><div class="chd"><div class="xico">💬</div><div><div class="cttl" data-i="fb_prev">Previous Feedback</div><div class="csub" data-i="fb_session">This session</div></div></div>
        <div class="cbd">
          <div id="fbList"><div class="empty"><div class="empt-e">💬</div><span data-i="no_fb">No feedback yet</span></div></div>
        </div>
      </div>
      <div class="card">
        <div class="chd"><div class="xico">👨‍💻</div><div><div class="cttl">Meet the Developers</div><div class="csub">Built with ❤️ for farmers</div></div></div>
        <div class="cbd">
          <div class="dev-row">
            <div class="dev-card">
              <div class="dev-avatar">H</div>
              <div class="dev-info">
                <div class="dev-name">Hardik</div>
                <div class="dev-role">Lead Developer · AI & Backend</div>
                <a class="dev-mail" href="mailto:Hardikchaturbedi@gmail.com">Hardikchaturbedi@gmail.com</a>
              </div>
            </div>
            <div class="dev-card">
              <div class="dev-avatar" style="background:linear-gradient(135deg,#a855f7,#ec4899)">A</div>
              <div class="dev-info">
                <div class="dev-name">Aditi</div>
                <div class="dev-role">Co-Developer · UI & Design</div>
                <a class="dev-mail" href="mailto:vtanu8546@gmail.com">vtanu8546@gmail.com</a>
              </div>
            </div>
          </div>
          <div class="tip" style="margin-top:.8rem"><div class="tipn">🌐</div><div class="tipt"><b>Best For:</b>Affected Plant & Leaf</div></div>
          <div class="tip"><div class="tipn">📊</div><div class="tipt"><b>27 disease classes</b> — Apple, Tomato, Potato, Corn, Grape & more</div></div>
        </div>
      </div>
    </div>
  </div>
</div>

</div><!-- /page -->

<div id="toast"></div>

<footer>
  <div style="margin-bottom:.6rem;font-size:.8rem">
    <b style="color:var(--tx);font-size:.9rem">🌿 LeafScan</b>
  </div>
  <div style="margin-bottom:.4rem">
    Crafted with ❤️ by <b>Hardik</b> &amp; <b>Aditi</b>
  </div>
  <div style="margin-bottom:.5rem;display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap">
    <a href="mailto:chaturbedi@gmail.com" style="color:var(--g);text-decoration:none;transition:opacity .2s" onmouseover="this.style.opacity='.7'" onmouseout="this.style.opacity='1'">chaturbedi@gmail.com</a>
    <span style="color:var(--brd2)">·</span>
    <a href="mailto:vtanu8546@gmail.com" style="color:var(--g);text-decoration:none;transition:opacity .2s" onmouseover="this.style.opacity='.7'" onmouseout="this.style.opacity='1'">vtanu8546@gmail.com</a>
  </div>
  <div>PlantDoc Dataset · MobileNetV2 · Farmer's AI Companion</div>
</footer>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<script>
/* ══ FARMER BACKGROUNDS ══ */
// High quality Unsplash farm/agriculture images (royalty-free)
const FARM_IMGS=[
  "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1600&q=80", // wheat field sunset
  "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=1600&q=80", // green farmland
  "https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?w=1600&q=80", // tractor in field
  "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1600&q=80", // watering crops
  "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=1600&q=80", // rice paddy
  "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1600&q=80", // lush green farm
  "https://images.unsplash.com/photo-1530836369250-ef72a3f5cda8?w=1600&q=80", // tomato plant
  "https://images.unsplash.com/photo-1592878849122-facb97ed2bdc?w=1600&q=80", // harvesting
];
let bgIdx=0;
function initFarmerBg(){
  bgIdx=Math.floor(Math.random()*FARM_IMGS.length);
  loadFarmerBg();}
function loadFarmerBg(){
  const el=document.getElementById('farmerBg');
  el.classList.remove('visible');
  const img=new Image();
  img.onload=()=>{el.style.backgroundImage=`url(${FARM_IMGS[bgIdx]})`;el.classList.add('visible');};
  img.onerror=()=>{el.classList.add('visible');};// fallback gracefully
  img.src=FARM_IMGS[bgIdx];}
function nextFarmerBg(){bgIdx=(bgIdx+1)%FARM_IMGS.length;loadFarmerBg();}
// Rotate bg every 45 seconds
setInterval(nextFarmerBg,45000);

/* ══ MOTIVATIONAL QUOTES ══ */
const QUOTES={
en:[
  {q:"Your hard work will define your legacy.",a:"Farmer's Wisdom"},
  {q:"Every morning brings new hope, every field is a new beginning.",a:""},
  {q:"The farmer is the only man who grows money from the earth.",a:""},
  {q:"No rain, no grain — but with patience, the harvest comes.",a:""},
  {q:"A healthy crop is the result of a thousand small decisions.",a:""},
  {q:"Sow with faith. Reap with gratitude.",a:""},
  {q:"The best time to plant a tree was 20 years ago. The second best time is now.",a:"Chinese Proverb"},
  {q:"Feed the soil and the soil will feed you.",a:""},
  {q:"Farming looks easy when your plow is a pencil.",a:"Eisenhower"},
  {q:"To forget how to dig the earth and to tend the soil is to forget ourselves.",a:"Gandhi"},
  {q:"The discovery of agriculture was the first big step toward a civilized life.",a:""},
  {q:"Life on the farm is a school of patience — you can't hurry the harvest.",a:""},
  {q:"The farmer works the hardest of anyone and yet the land always gives back.",a:""},
  {q:"One good farmer is worth a thousand lawyers.",a:""},
  {q:"Blessed are the farmers — for they inherit the earth's bounty.",a:""},
],
hi:[
  {q:"आपकी मेहनत आपकी विरासत बनाएगी।",a:"किसान की बुद्धि"},
  {q:"हर सुबह नई उम्मीद लेकर आती है, हर खेत नई शुरुआत है।",a:""},
  {q:"किसान वह है जो धरती से सोना उगाता है।",a:""},
  {q:"बारिश न हो तो भी हिम्मत रखो — फसल धैर्य का फल है।",a:""},
  {q:"स्वस्थ फसल हजार छोटे फैसलों का नतीजा है।",a:""},
  {q:"विश्वास के साथ बोओ, कृतज्ञता के साथ काटो।",a:""},
  {q:"मिट्टी को खिलाओ, मिट्टी तुम्हें खिलाएगी।",a:""},
  {q:"किसान की मेहनत सबसे महान तपस्या है।",a:""},
  {q:"धरती माँ है — उसकी सेवा करो, वो कभी नहीं भूलती।",a:""},
  {q:"खेत में जो पसीना बहाते हैं, इतिहास उन्हें याद करता है।",a:""},
  {q:"अच्छा किसान एक हजार वकीलों से बेहतर है।",a:""},
  {q:"जमीन से जुड़े रहो — यही असली जड़ें हैं।",a:""},
  {q:"जब किसान खुश होगा, तो देश खुश होगा।",a:""},
  {q:"बीज बोने का साहस ही कल की फसल की नींव है।",a:""},
  {q:"मेहनत कभी बेकार नहीं जाती — जमीन सब याद रखती है।",a:""},
],
bn:[
  {q:"আপনার কঠোর পরিশ্রমই আপনার উত্তরাধিকার হবে।",a:"কৃষকের জ্ঞান"},
  {q:"প্রতিটি সকাল নতুন আশা নিয়ে আসে, প্রতিটি মাঠ নতুন শুরু।",a:""},
  {q:"কৃষক সেই যে মাটি থেকে সোনা ফলায়।",a:""},
  {q:"মাটিকে ভালোবাসো — মাটি তোমাকে ফিরিয়ে দেবে।",a:""},
  {q:"বিশ্বাসের সাথে বপন করো, কৃতজ্ঞতার সাথে ঘরে তোলো।",a:""},
  {q:"একজন ভালো কৃষক হাজার আইনজীবীর চেয়ে ভালো।",a:""},
  {q:"ধৈর্য ধরো — ফসল সময়মতো আসবেই।",a:""},
  {q:"জমির সেবাই জীবনের সবচেয়ে বড় সেবা।",a:""},
],
ta:[
  {q:"உங்கள் கடின உழைப்பே உங்கள் மரபு.",a:"விவசாயி ஞானம்"},
  {q:"ஒவ்வொரு காலையும் புதிய நம்பிக்கை, ஒவ்வொரு வயலும் புதிய தொடக்கம்.",a:""},
  {q:"விவசாயி மண்ணில் இருந்து தங்கம் விளைவிப்பவர்.",a:""},
  {q:"மண்ணை நேசி — மண் உன்னை திரும்ப வழங்கும்.",a:""},
  {q:"நம்பிக்கையுடன் விதை, நன்றியுடன் அறுவடை செய்.",a:""},
  {q:"பொறுமையே விவசாயியின் மிகப்பெரிய ஆயுதம்.",a:""},
],
te:[
  {q:"మీ కష్టమే మీ వారసత్వాన్ని నిర్ణయిస్తుంది.",a:"రైతు జ్ఞానం"},
  {q:"ప్రతి తెల్లవారూ కొత్త ఆశ, ప్రతి పొలం కొత్త మొదలు.",a:""},
  {q:"రైతు మట్టి నుండి బంగారం పండించే వాడు.",a:""},
  {q:"మట్టిని ప్రేమించు — మట్టి నిన్ను తిరిగి ఇస్తుంది.",a:""},
  {q:"విశ్వాసంతో విత్తు, కృతజ్ఞతతో పంట కోయి.",a:""},
],
mr:[
  {q:"तुमची मेहनत तुमची ओळख बनवेल.",a:"शेतकऱ्याची शहाणीव"},
  {q:"प्रत्येक सकाळ नवी आशा घेऊन येते, प्रत्येक शेत नवी सुरुवात.",a:""},
  {q:"शेतकरी म्हणजे मातीतून सोने पिकवणारा माणूस.",a:""},
  {q:"मातीवर प्रेम करा — माती तुम्हाला परत देईल.",a:""},
  {q:"श्रद्धेने पेरा, कृतज्ञतेने कापा.",a:""},
  {q:"चांगला शेतकरी हजार वकिलांपेक्षा श्रेष्ठ.",a:""},
],
gu:[
  {q:"તમારી મહેનત જ તમારો વારસો બનશે.",a:"ખેડૂતની સૂઝ"},
  {q:"દરરોજ સવારે નવી આશા, દરરેક ખેતર નવી શરૂઆત.",a:""},
  {q:"ખેડૂત એ છે જે માટીમાંથી સોનું ઉગાડે.",a:""},
  {q:"માટીને પ્રેમ કરો — માટી તમને પાછું આપશે.",a:""},
  {q:"વિશ્વાસ સાથે વાવો, કૃતજ્ઞતા સાથે લણો.",a:""},
],
pa:[
  {q:"ਤੁਹਾਡੀ ਮਿਹਨਤ ਹੀ ਤੁਹਾਡੀ ਵਿਰਾਸਤ ਬਣੇਗੀ।",a:"ਕਿਸਾਨ ਦੀ ਸਿਆਣਪ"},
  {q:"ਹਰ ਸਵੇਰ ਨਵੀਂ ਉਮੀਦ, ਹਰ ਖੇਤ ਨਵੀਂ ਸ਼ੁਰੂਆਤ।",a:""},
  {q:"ਕਿਸਾਨ ਉਹ ਹੈ ਜੋ ਮਿੱਟੀ ਤੋਂ ਸੋਨਾ ਉਗਾਉਂਦਾ ਹੈ।",a:""},
  {q:"ਮਿੱਟੀ ਨਾਲ ਪਿਆਰ ਕਰੋ — ਮਿੱਟੀ ਵਾਪਸ ਕਰੇਗੀ।",a:""},
  {q:"ਭਰੋਸੇ ਨਾਲ ਬੀਜੋ, ਸ਼ੁਕਰਗੁਜ਼ਾਰੀ ਨਾਲ ਵੱਢੋ।",a:""},
]};

let lastQIdx=-1;
function newQuote(){
  const pool=QUOTES[cLang]||QUOTES.en;
  let idx;do{idx=Math.floor(Math.random()*pool.length);}while(idx===lastQIdx&&pool.length>1);
  lastQIdx=idx;const q=pool[idx];
  const qEl=document.getElementById('qText');
  qEl.style.animation='none';requestAnimationFrame(()=>{qEl.style.animation='';});
  qEl.textContent=q.q;
  document.getElementById('qAuthor').textContent=q.a?'— '+q.a:'';}

/* ══ FACT CHIPS ══ */
const FACTS={
en:[
  {ico:"🌿",txt:"Plants signal distress by releasing chemicals into the air"},
  {ico:"🦠",txt:"Over 50% of crop losses worldwide are caused by fungi"},
  {ico:"💧",txt:"Overwatering is the #1 cause of root disease in home gardens"},
  {ico:"☀️",txt:"Sunlight for 6+ hours daily prevents most fungal diseases"},
  {ico:"🧪",txt:"Neem oil is effective against 200+ types of pests & diseases"},
  {ico:"🔬",txt:"Early blight appears as dark spots with yellow rings on leaves"},
  {ico:"🌾",txt:"India loses ₹90,000 crore annually to crop diseases"},
  {ico:"🐛",txt:"Healthy soil has 1 billion microbes per teaspoon"},
  {ico:"📅",txt:"Crop rotation reduces disease risk by up to 40%"},
  {ico:"🌡",txt:"Most fungal diseases thrive between 20-30°C with high humidity"},
],
hi:[
  {ico:"🌿",txt:"पौधे खतरे में होने पर हवा में रसायन छोड़ते हैं"},
  {ico:"🦠",txt:"दुनिया भर में 50% से अधिक फसल नुकसान कवक के कारण होता है"},
  {ico:"💧",txt:"अत्यधिक सिंचाई जड़ रोग का सबसे बड़ा कारण है"},
  {ico:"☀️",txt:"रोजाना 6+ घंटे धूप अधिकांश कवक रोगों को रोकती है"},
  {ico:"🧪",txt:"नीम तेल 200+ कीट और बीमारियों पर असरदार है"},
  {ico:"🌾",txt:"भारत में हर साल ₹90,000 करोड़ की फसल बर्बाद होती है"},
  {ico:"🐛",txt:"स्वस्थ मिट्टी में एक चम्मच में 1 अरब सूक्ष्मजीव होते हैं"},
  {ico:"📅",txt:"फसल चक्र से बीमारी का खतरा 40% तक कम होता है"},
]};
// Other langs fallback to en
['bn','ta','te','mr','gu','pa'].forEach(l=>FACTS[l]=FACTS[l]||FACTS.en);

function buildFactStrip(containerId){
  const pool=FACTS[cLang]||FACTS.en;
  const shuffled=[...pool].sort(()=>Math.random()-.5).slice(0,6);
  const el=document.getElementById(containerId);if(!el)return;
  el.innerHTML='';
  shuffled.forEach(f=>{const d=document.createElement('div');d.className='fact-chip';
    d.innerHTML=`<span>${f.ico}</span><span>${f.txt}</span>`;el.appendChild(d);});}

/* ══ EDUCATIONAL TOOLTIPS ══ */
const EDU_FACTS={
  "Early blight":[
    {ico:"🦠",title:"What is Early Blight?",text:"Caused by Alternaria fungus. Dark brown spots with yellow halos on lower leaves first. Spreads upward."},
    {ico:"🌡",title:"Ideal Conditions",text:"Thrives in warm (24-29°C), humid weather. Spreads fastest after rain followed by dry spells."},
    {ico:"💊",title:"Treatment",text:"Copper-based or Chlorothalonil fungicide. Apply every 7-10 days. Remove infected leaves."},
  ],
  "Late blight":[
    {ico:"⚠️",title:"Danger Level: HIGH",text:"Late blight caused the Irish Potato Famine (1845). It can destroy an entire field in 3-5 days."},
    {ico:"🌡",title:"Spreads Fast In",text:"Cool (10-20°C) and very wet weather. Wind carries spores to healthy plants within hours."},
    {ico:"🚨",title:"Act Fast",text:"Remove infected plants immediately. Apply Metalaxyl or Mancozeb fungicide. Stop overhead watering."},
  ],
  "Leaf Mold":[
    {ico:"🌬",title:"What Causes It?",text:"Passalora fulva fungus. Appears as yellow spots on top of leaves and olive-green mold below."},
    {ico:"💧",title:"Key Risk Factor",text:"High humidity (above 85%) triggers it. Common in greenhouses and densely planted fields."},
    {ico:"✂️",title:"Prevention",text:"Improve airflow between plants. Avoid wetting leaves. Use resistant varieties when possible."},
  ],
  "healthy":[
    {ico:"✅",title:"Your Plant is Healthy!",text:"Great news! A healthy leaf means proper nutrition, good watering, and no pest pressure."},
    {ico:"🔍",title:"Keep Watching",text:"Even healthy plants need weekly inspection. Diseases often start with very subtle signs."},
    {ico:"🌱",title:"Maintain Health",text:"Continue your current care routine. Balanced NPK fertilizer monthly keeps plants strong."},
  ],
  "default":[
    {ico:"🔬",title:"How AI Detection Works",text:"Our model analyzes leaf texture, color patterns, and spot shapes using deep learning to identify diseases."},
    {ico:"📊",title:"About Confidence Score",text:"A score above 70% is reliable. Below 50% means try again with a clearer, better-lit photo."},
    {ico:"🌿",title:"PlantDoc Dataset",text:"Trained on 2,500+ real field images across 27 disease classes — unlike lab images, these are real-world."},
  ]};

function getEduFacts(diseaseName,isHealthy){
  if(isHealthy)return EDU_FACTS.healthy;
  const name=(diseaseName||'').toLowerCase();
  for(const [k,v] of Object.entries(EDU_FACTS)){
    if(k!=='default'&&k!=='healthy'&&name.includes(k.toLowerCase()))return v;}
  return EDU_FACTS.default;}

function buildEduTooltips(diseaseName,isHealthy){
  const facts=getEduFacts(diseaseName,isHealthy);
  const el=document.getElementById('eduFacts');el.innerHTML='';
  facts.forEach(f=>{
    const d=document.createElement('div');
    d.className='fact-chip tip-host';
    d.style.cssText='flex-direction:column;align-items:flex-start;padding:8px 12px;min-width:160px;cursor:help';
    d.innerHTML=`<div style="display:flex;align-items:center;gap:5px;font-weight:800;color:var(--tx);font-size:.72rem">${f.ico} ${f.title}</div>
      <div style="font-size:.67rem;color:var(--tx2);margin-top:3px;line-height:1.45;white-space:normal;max-width:160px">${f.text}</div>`;
    el.appendChild(d);});
  document.getElementById('eduRow').style.display='block';}
/* ══ TRANSLATIONS ══ */
const TX={
en:{eyebrow:"Plant Disease Detection",h1:"Diagnose your <em>crops</em> instantly",hero_p:"Upload any leaf photo — AI identifies diseases & plant health in seconds.",
s1:"Disease Classes",s2:"Training Images",s3:"Val Accuracy",s4:"Optimized",
nav_live:"AI Online",tutorial:"Tutorial",upload_title:"Upload Leaf",upload_sub:"JPG · PNG · WEBP",
dzt:"Drop image here",dzs:"<b>Click to browse</b> or drag & drop",change:"Change ↺",
analyze_btn:"Analyze Leaf",scanning:"SCANNING",step0:"Loading",step1:"Preprocessing",step2:"Features",step3:"Classifying",step4:"Report",
result_title:"Analysis Result",plant_lbl:"Plant",disease_lbl:"Disease",conf_lbl:"Confidence",
copy:"Copy",save:"Save",share:"Share",print:"Print",
hist_title:"Scan History",hist_sub:"scans this session",no_scans:"No scans yet",
stats_title:"Session Stats",stats_sub:"Live counters",total:"Total",healthy_lbl:"Healthy",diseased_lbl:"Diseased",healthy_pct:"Healthy %",
tips_title:"Quick Tips",tips_sub:"Better accuracy",photo_tips:"Photo Tips",general_tips:"General Advice",
tip1:"Use <b>natural daylight</b> — avoid flash",tip2:"<b>Fill the frame</b> with the affected leaf",
tip3:"Keep image <b>sharp and focused</b>",tip4:"Scan <b>multiple leaves</b> to confirm",
tip5:"Best for: <b>Apple, Tomato, Potato, Corn, Grape</b>",
tip6:"Avoid <b>wet or dirty</b> leaves — wipe gently first",tip7:"Scan early morning for <b>best visibility</b>",
gtip1:"<b>Water properly</b> — avoid overwatering",gtip2:"<b>Good air circulation</b> — space plants well",
gtip3:"<b>Remove infected leaves</b> immediately",gtip4:"<b>Neem oil spray</b> — organic prevention",
gtip5:"<b>Rotate crops</b> every season",gtip6:"<b>Inspect weekly</b> — early detection saves crops",
report_title:"Personalized Report",
fb_title:"Rate LeafScan",fb_sub:"Your feedback helps us improve",fb_how:"How was your experience?",fb_what:"What did you like?",
fbt1:"Easy to use",fbt2:"Accurate results",fbt3:"Fast scanning",fbt4:"Helpful suggestions",fbt5:"Good UI",fbt6:"Multi-language",
fb_send:"Submit Feedback",fb_prev:"Previous Feedback",fb_session:"This session",no_fb:"No feedback yet",
help_title:"Need Help?",help_sub:"Contact & resources",
tab_scan:"🔍 Scan",tab_hist:"🕒 History",tab_stats:"📊 Stats",tab_tips:"💡 Tips",tab_fb:"⭐ Feedback",
top_diseases:"Top Diseases Found",this_session:"This session",
healthy_tag:"HEALTHY PLANT",disease_tag:"DISEASE DETECTED",
analyzed:"Analyzed in",secs:"s",
sev_low:"Low Severity",sev_med:"Medium Severity",sev_high:"High Severity",
t_copied:"📋 Copied!",t_saved:"⬇ Saved!",t_healthy:"✅ Plant is Healthy!",t_diseased:"⚠️ Disease Detected!",t_fb:"🙏 Thanks for feedback!",t_lang:"🌐 Language changed",not_leaf_msg:"Please upload a leaf image for accurate results",take_photo:"Take Photo",choose_file:"Choose File",camera_title:"Camera",cam_hint:"Position leaf inside frame"},
hi:{eyebrow:"पौधे की बीमारी पहचान",h1:"अपनी <em>फसल</em> को तुरंत जाँचें",hero_p:"कोई भी पत्ते की फोटो अपलोड करें — AI सेकंडों में बीमारी पहचानेगी।",
s1:"बीमारी वर्ग",s2:"ट्रेनिंग छवियाँ",s3:"सटीकता",s4:"अनुकूलित",
nav_live:"AI चालू",tutorial:"ट्यूटोरियल",upload_title:"पत्ता अपलोड करें",upload_sub:"JPG · PNG · WEBP",
dzt:"यहाँ छवि डालें",dzs:"<b>क्लिक करें</b> या खींचकर छोड़ें",change:"बदलें ↺",
analyze_btn:"पत्ता जाँचें",scanning:"स्कैनिंग",step0:"लोडिंग",step1:"प्रोसेसिंग",step2:"फीचर",step3:"वर्गीकरण",step4:"रिपोर्ट",
result_title:"जाँच परिणाम",plant_lbl:"पौधा",disease_lbl:"बीमारी",conf_lbl:"विश्वसनीयता",
copy:"कॉपी",save:"सेव",share:"शेयर",print:"प्रिंट",
hist_title:"स्कैन इतिहास",hist_sub:"इस सत्र में स्कैन",no_scans:"अभी कोई स्कैन नहीं",
stats_title:"सत्र आँकड़े",stats_sub:"लाइव काउंटर",total:"कुल",healthy_lbl:"स्वस्थ",diseased_lbl:"बीमार",healthy_pct:"स्वस्थ %",
tips_title:"त्वरित सुझाव",tips_sub:"बेहतर सटीकता",photo_tips:"फोटो सुझाव",general_tips:"सामान्य सलाह",
tip1:"<b>प्राकृतिक रोशनी</b> में फोटो लें",tip2:"पत्ते को <b>पूरे फ्रेम</b> में रखें",
tip3:"फोटो <b>साफ और फोकस</b> में हो",tip4:"पुष्टि के लिए <b>कई पत्ते</b> स्कैन करें",
tip5:"<b>सेब, टमाटर, आलू, मक्का, अंगूर</b> के लिए सर्वश्रेष्ठ",
tip6:"<b>गीले या गंदे</b> पत्ते से बचें",tip7:"सुबह के समय स्कैन करें",
gtip1:"<b>सही तरीके से पानी दें</b> — अत्यधिक सिंचाई न करें",gtip2:"<b>अच्छी हवा</b> के लिए पौधों में जगह रखें",
gtip3:"<b>संक्रमित पत्ते</b> तुरंत हटाएँ",gtip4:"<b>नीम तेल का छिड़काव</b> — जैविक बचाव",
gtip5:"हर मौसम में <b>फसल बदलें</b>",gtip6:"<b>हफ्ते में जाँच</b> — जल्दी पहचान से फसल बचती है",
report_title:"व्यक्तिगत रिपोर्ट",
fb_title:"LeafScan को रेट करें",fb_sub:"आपकी प्रतिक्रिया हमें बेहतर बनाती है",fb_how:"आपका अनुभव कैसा रहा?",fb_what:"आपको क्या पसंद आया?",
fbt1:"उपयोग में आसान",fbt2:"सटीक परिणाम",fbt3:"तेज़ स्कैनिंग",fbt4:"उपयोगी सुझाव",fbt5:"अच्छा डिज़ाइन",fbt6:"बहुभाषी",
fb_send:"प्रतिक्रिया भेजें",fb_prev:"पिछली प्रतिक्रिया",fb_session:"इस सत्र में",no_fb:"अभी कोई प्रतिक्रिया नहीं",
help_title:"सहायता चाहिए?",help_sub:"संपर्क और संसाधन",
tab_scan:"🔍 स्कैन",tab_hist:"🕒 इतिहास",tab_stats:"📊 आँकड़े",tab_tips:"💡 सुझाव",tab_fb:"⭐ प्रतिक्रिया",
top_diseases:"मिली प्रमुख बीमारियाँ",this_session:"इस सत्र में",
healthy_tag:"पौधा स्वस्थ है",disease_tag:"बीमारी मिली",
analyzed:"विश्लेषण हुआ",secs:"सेकंड में",
sev_low:"कम गंभीर",sev_med:"मध्यम गंभीर",sev_high:"अधिक गंभीर",
t_copied:"📋 कॉपी हो गया!",t_saved:"⬇ सेव हो गया!",t_healthy:"✅ पौधा स्वस्थ है!",t_diseased:"⚠️ बीमारी मिली!",t_fb:"🙏 धन्यवाद!",t_lang:"🌐 भाषा बदल गई",not_leaf_msg:"कृपया पत्ते की फोटो अपलोड करें",take_photo:"फोटो लें",choose_file:"फाइल चुनें",camera_title:"कैमरा",cam_hint:"पत्ते को फ्रेम में रखें"}
};
// Fill other langs from en (fallback)
['bn','ta','te','mr','gu','pa'].forEach(l=>TX[l]=TX[l]||{...TX.en});

const FLAGS={en:"🇺🇸",hi:"🇮🇳",bn:"🇮🇳",ta:"🇮🇳",te:"🇮🇳",mr:"🇮🇳",gu:"🇮🇳",pa:"🇮🇳"};
const LNAMES={en:"EN",hi:"HI",bn:"BN",ta:"TA",te:"TE",mr:"MR",gu:"GU",pa:"PA"};
let cLang="en",cTheme="dark";

function t(k){return (TX[cLang]&&TX[cLang][k])||TX.en[k]||k}
function applyLang(){
  document.querySelectorAll('[data-i]').forEach(el=>{
    const v=t(el.dataset.i);if(!v)return;
    if(v.includes('<'))el.innerHTML=v;else el.textContent=v;
  });
  document.getElementById('fbTxt').placeholder=cLang==='hi'?'यहाँ अपनी प्रतिक्रिया लिखें...':'Write your feedback here...';
  document.getElementById('hCnt').textContent=histArr.length+' '+t('hist_sub');
  // Update history badge + nav count
  const hb=document.getElementById('histBadge');
  if(hb){hb.style.display='';hb.textContent=histArr.length;hb.classList.add('bump');setTimeout(()=>hb.classList.remove('bump'),400);}
  const nc=document.getElementById('navCount');
  if(nc){nc.style.display='';nc.textContent=histArr.length+' scan'+(histArr.length!==1?'s':'');}
}
function setLang(l){cLang=l;document.getElementById('lFlag').textContent=FLAGS[l];document.getElementById('lNm').textContent=LNAMES[l];
  document.querySelectorAll('.lopt').forEach(o=>o.classList.toggle('sel',o.getAttribute('onclick').includes("'"+l+"'")));
  document.getElementById('lw').classList.remove('open');applyLang();toast(t('t_lang'));}
function toggleLD(){document.getElementById('lw').classList.toggle('open')}
document.addEventListener('click',e=>{if(!e.target.closest('.lw'))document.getElementById('lw').classList.remove('open')});

/* ══ THEME ══ */
function toggleTheme(){cTheme=cTheme==='dark'?'light':'dark';
  document.documentElement.setAttribute('data-theme',cTheme);
  document.getElementById('tIco').textContent=cTheme==='dark'?'🌙':'☀️';
  document.getElementById('tTxt').textContent=cTheme==='dark'?'Dark':'Light';
  refreshCharts();}

/* ══ CURSOR — PREMIUM ══ */
const cD=document.getElementById('cD'),cR=document.getElementById('cR'),cT=document.getElementById('cT');
let mx=0,my=0,rx=0,ry=0,tx=0,ty=0,isHover=false;
// Trail particles
const TRAIL=[];
for(let i=0;i<6;i++){const d=document.createElement('div');d.style.cssText=`position:fixed;border-radius:50%;pointer-events:none;z-index:9998;top:0;left:0;width:${4-i*.4}px;height:${4-i*.4}px;background:var(--g);opacity:0;transition:opacity .1s;will-change:transform`;document.body.appendChild(d);TRAIL.push({el:d,x:0,y:0,delay:i*1.6});}
// Mouse move
document.addEventListener('mousemove',e=>{
  mx=e.clientX;my=e.clientY;
  cD.style.transform=`translate(${mx}px,${my}px)`;
});
// Smooth ring follow + trail
(function lC(){
  rx+=(mx-rx)*.12;ry+=(my-ry)*.12;
  cR.style.transform=`translate(${rx}px,${ry}px)`;
  // trail
  TRAIL.forEach((t,i)=>{
    t.x+=(mx-t.x)*(0.09-i*.008);
    t.y+=(my-t.y)*(0.09-i*.008);
    t.el.style.transform=`translate(${t.x}px,${t.y}px)`;
    t.el.style.opacity=isHover?'0':`${0.35-i*.05}`;
    t.el.style.marginLeft=`-${(4-i*.4)/2}px`;
    t.el.style.marginTop=`-${(4-i*.4)/2}px`;
  });
  requestAnimationFrame(lC);
})();
// Hover states
document.querySelectorAll('button,a,.dz,.hi,.pr,.stat,.tip,.actb,.lopt,.cb,.fbtag,.fbstar,.cam-btn,.cam-snap').forEach(el=>{
  el.addEventListener('mouseenter',()=>{isHover=true;document.body.classList.add('cg')});
  el.addEventListener('mouseleave',()=>{isHover=false;document.body.classList.remove('cg')});
});
// Click burst
document.addEventListener('mousedown',e=>{
  document.body.classList.add('cc');
  // Spawn burst particles
  for(let i=0;i<8;i++){
    const p=document.createElement('div');const angle=(i/8)*Math.PI*2;const dist=28+Math.random()*18;
    p.style.cssText=`position:fixed;width:3px;height:3px;border-radius:50%;background:var(--g);pointer-events:none;z-index:9998;left:${e.clientX}px;top:${e.clientY}px;transition:transform .5s cubic-bezier(.2,1,.3,1),opacity .5s ease;box-shadow:0 0 4px var(--gg)`;
    document.body.appendChild(p);
    requestAnimationFrame(()=>{p.style.transform=`translate(${Math.cos(angle)*dist}px,${Math.sin(angle)*dist}px) scale(0)`;p.style.opacity='0';});
    setTimeout(()=>p.remove(),520);
  }
  setTimeout(()=>document.body.classList.remove('cc'),120);
});

/* ══ CANVAS ══ */
const cv=document.getElementById('bgC'),cx2=cv.getContext('2d');
let W,H,pts=[];
function initC(){cv.width=W=innerWidth;cv.height=H=innerHeight;
  pts=Array.from({length:45},()=>({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.22,vy:(Math.random()-.5)*.22,r:Math.random()*1.1+.35,o:Math.random()*.3+.07}));}
initC();addEventListener('resize',initC);
(function fr(){cx2.clearRect(0,0,W,H);const gc=cTheme==='dark'?'110,251,92':'22,122,6';
  pts.forEach(p=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;
    cx2.beginPath();cx2.arc(p.x,p.y,p.r,0,6.28);cx2.fillStyle=`rgba(${gc},${p.o})`;cx2.fill()});
  pts.forEach((a,i)=>pts.slice(i+1).forEach(b=>{const d=Math.hypot(a.x-b.x,a.y-b.y);if(d<100){
    cx2.beginPath();cx2.moveTo(a.x,a.y);cx2.lineTo(b.x,b.y);
    cx2.strokeStyle=`rgba(${gc},${.06*(1-d/100)})`;cx2.lineWidth=.45;cx2.stroke();}}));
  requestAnimationFrame(fr);})();

/* ══ RIPPLE ══ */
function ripple(el,e){const rc=el.getBoundingClientRect(),s=Math.max(rc.width,rc.height)*2.5;
  const r=document.createElement('div');r.className='rip';
  Object.assign(r.style,{width:s+'px',height:s+'px',left:(e.clientX-rc.left-s/2)+'px',top:(e.clientY-rc.top-s/2)+'px'});
  el.appendChild(r);setTimeout(()=>r.remove(),560);}
document.querySelectorAll('.rhost').forEach(el=>el.addEventListener('click',e=>ripple(el,e)));

/* ══ TABS ══ */
function showTab(id){
  // Tabs highlight
  document.querySelectorAll('.tab').forEach((t,i)=>t.classList.toggle('on',['scan','history','stats','tips','feedback'][i]===id));
  // Hide current, show new with animation
  document.querySelectorAll('.tab-panel').forEach(p=>{
    if(p.classList.contains('on')&&p.id!=='tp-'+id){
      p.style.opacity='0';p.style.transform='translateY(-8px)';
      p.style.transition='opacity .18s,transform .18s';
      setTimeout(()=>{p.classList.remove('on');p.style.cssText='';},180);
    }
  });
  setTimeout(()=>{
    const panel=document.getElementById('tp-'+id);
    if(panel){panel.classList.add('on');}
    if(id==='stats')buildPieChart();
    if(id==='history')buildHistoryFull();
    window.scrollTo({top:document.querySelector('.tabs').offsetTop-80,behavior:'smooth'});
  },id==='scan'?0:160);
}

/* ══ DRAG DROP ══ */
const dz=document.getElementById('dz');
dz.addEventListener('dragover',e=>{e.preventDefault();dz.classList.add('over')});
dz.addEventListener('dragleave',()=>dz.classList.remove('over'));
dz.addEventListener('drop',e=>{e.preventDefault();dz.classList.remove('over');const f=e.dataTransfer.files[0];if(f&&f.type.startsWith('image/'))setFile(f)});
document.getElementById('fI').addEventListener('change',function(){if(this.files[0])setFile(this.files[0])});

let selF=null,histArr=[],lastR=null,hChart=null,hChart2=null,pieChart=null;
let sT=0,sH=0,sD=0,diseaseCount={},fbStar=0,fbArr=[];

/* ══ LEAF VALIDATION ══ */
// Simple color-based heuristic: real leaves have dominant green channel
function validateLeaf(imgEl,cb){
  try{
    const cv=document.createElement('canvas');const sz=64;cv.width=cv.height=sz;
    const cx=cv.getContext('2d');cx.drawImage(imgEl,0,0,sz,sz);
    const d=cx.getImageData(0,0,sz,sz).data;
    let gScore=0,total=0,greenPx=0;
    for(let i=0;i<d.length;i+=4){
      const r=d[i],g=d[i+1],b=d[i+2],a=d[i+3];
      if(a<30)continue;total++;
      // Green dominance score
      if(g>r&&g>b&&g>60)greenPx++;
      gScore+=g-Math.max(r,b);
    }
    const ratio=total?greenPx/total:0;
    if(ratio>0.18)cb('leaf',Math.round(ratio*100));
    else if(ratio>0.07)cb('maybe',Math.round(ratio*100));
    else cb('notleaf',Math.round(ratio*100));
  }catch(e){cb('unknown',0);}
}

function showValBadge(type,pct){
  const el=document.getElementById('valBadge');
  const msgs={leaf:`✅ Leaf Detected (${pct}% green)`,maybe:`⚠️ Possibly a leaf — try better lighting`,notleaf:`❌ No leaf detected — upload a leaf image`,unknown:'📷 Image loaded'};
  const cls={leaf:'val-leaf',maybe:'val-warn',notleaf:'val-err',unknown:'val-leaf'};
  el.innerHTML=`<span class="val-badge ${cls[type]}">${msgs[type]}</span>`;
  el.style.display='block';
  // If not leaf, disable analyze and shake button
  const btn=document.getElementById('aBtn');
  if(type==='notleaf'){
    btn.disabled=true;
    btn.style.animation='shake .4s ease';
    setTimeout(()=>btn.style.animation='',450);
    toast('❌ '+t('not_leaf_msg'));
  }else{btn.disabled=false;}
}

function setFile(f,fromCamera){
  selF=f;
  const rd=new FileReader();
  rd.onload=e=>{
    const s=e.target.result;
    document.getElementById('pImg').src=s;
    document.getElementById('sImg').src=s;
    document.getElementById('pW').style.display='block';
    dz.style.display='none';
    const name=fromCamera?'📸 Camera':'📁 '+f.name;
    document.getElementById('fnC').textContent=name.length>22?name.slice(0,20)+'…':name;
    // Validate after image loads
    const img=document.getElementById('pImg');
    if(img.complete){validateLeaf(img,showValBadge);}
    else{img.onload=()=>validateLeaf(img,showValBadge);}
  };
  rd.readAsDataURL(f);
  document.getElementById('valBadge').style.display='none';
  document.getElementById('rCard').style.display='none';
  document.getElementById('ldr').style.display='none';
}

/* ══ SHAKE ANIMATION ══ */
const shakeStyle=document.createElement('style');
shakeStyle.textContent='@keyframes shake{0%,100%{transform:translateX(0)}20%{transform:translateX(-6px)}40%{transform:translateX(6px)}60%{transform:translateX(-4px)}80%{transform:translateX(4px)}}';
document.head.appendChild(shakeStyle);

/* ══ CAMERA ══ */
let camStream=null,facingMode='environment';
async function openCamera(){
  document.getElementById('camModal').style.display='block';
  await startCam();}
async function startCam(){
  if(camStream){camStream.getTracks().forEach(t=>t.stop());}
  try{
    camStream=await navigator.mediaDevices.getUserMedia({video:{facingMode,width:{ideal:1280},height:{ideal:960}}});
    document.getElementById('camVideo').srcObject=camStream;
  }catch(e){
    toast('❌ Camera access denied. Check browser permissions.');
    closeCamera();
  }
}
function closeCamera(){
  if(camStream){camStream.getTracks().forEach(t=>t.stop());camStream=null;}
  document.getElementById('camModal').style.display='none';
}
function flipCamera(){
  facingMode=facingMode==='environment'?'user':'environment';
  startCam();
}
function snapPhoto(){
  const video=document.getElementById('camVideo');
  const canvas=document.getElementById('camCanvas');
  canvas.width=video.videoWidth;canvas.height=video.videoHeight;
  canvas.getContext('2d').drawImage(video,0,0);
  canvas.toBlob(blob=>{
    const file=new File([blob],'camera_leaf.jpg',{type:'image/jpeg'});
    closeCamera();
    setFile(file,true);
    // Flash effect
    const flash=document.createElement('div');
    flash.style.cssText='position:fixed;inset:0;background:#fff;z-index:700;opacity:.85;transition:opacity .3s;pointer-events:none';
    document.body.appendChild(flash);
    requestAnimationFrame(()=>requestAnimationFrame(()=>{flash.style.opacity='0';setTimeout(()=>flash.remove(),320);}));
  },'image/jpeg',.92);
}
// Close camera on backdrop click
document.getElementById('camModal').addEventListener('click',e=>{if(e.target===document.getElementById('camModal'))closeCamera();});

/* ══ STEPS ══ */
function runSteps(done){
  const ids=['s0','s1','s2','s3','s4'];let pct=0;
  const pi=setInterval(()=>{pct=Math.min(pct+2,94);document.getElementById('sPct').textContent=pct+'%'},62);
  ids.forEach((id,i)=>setTimeout(()=>{
    if(i>0){const p=document.getElementById(ids[i-1]);p.classList.remove('on');p.classList.add('ok');p.innerHTML='✓ '+p.textContent.replace('✓ ','')}
    document.getElementById(id).classList.add('on');},i*600));
  setTimeout(()=>{clearInterval(pi);document.getElementById('sPct').textContent='100%';done();},3200);}

/* ══ ANALYZE ══ */
async function analyze(){
  if(!selF)return;
  document.getElementById('aBtn').disabled=true;
  document.getElementById('rCard').style.display='none';
  document.getElementById('ldr').style.display='block';
  document.querySelectorAll('.step').forEach(s=>{s.classList.remove('on','ok');s.innerHTML=s.textContent.replace('✓ ','')});
  document.getElementById('ldr').scrollIntoView({behavior:'smooth',block:'nearest'});
  const fd=new FormData();fd.append('image',selF);const t0=Date.now();
  runSteps(async()=>{
    try{const res=await fetch('/predict',{method:'POST',body:fd});const d=await res.json();
      if(d.error){alert('Error: '+d.error);return;}
      const el=((Date.now()-t0)/1000).toFixed(1);
      document.getElementById('ldr').style.display='none';
      showResult(d,el);addHistory(d,document.getElementById('pImg').src);updateStats(d);
    }catch(e){alert('Server se connect nahi hua.');}
    finally{document.getElementById('aBtn').disabled=false;document.getElementById('ldr').style.display='none';}});}

/* ══ DISEASE SUGGESTIONS DB ══ */
const DISEASE_DB={
  "Early blight":{sev:"med",suggestions:["🌿 Remove and destroy infected leaves immediately","💊 Apply copper-based fungicide every 7-10 days","💧 Water at soil level — avoid wetting leaves","☀️ Ensure plants get 6+ hours of sunlight","🧹 Clean fallen debris around plants"]},
  "Late blight":{sev:"high",suggestions:["🚨 Act immediately — this spreads very fast","🧪 Apply Mancozeb or Metalaxyl fungicide urgently","✂️ Remove all infected parts and burn them","💧 Stop overhead irrigation completely","📞 Consult a local agricultural expert soon"]},
  "Leaf Mold":{sev:"med",suggestions:["🌬 Improve ventilation around plants","💊 Spray chlorothalonil fungicide","🌡 Reduce humidity — space plants further apart","💧 Morning watering only so leaves dry by evening","🔍 Check undersides of leaves weekly"]},
  "healthy":{sev:"low",suggestions:["✅ Your plant looks great! Keep it up","💧 Continue regular watering schedule","🌱 Apply balanced fertilizer monthly","🔍 Keep checking weekly for early signs","🌞 Ensure adequate sunlight and spacing"]},
  "default":{sev:"med",suggestions:["🔬 Confirm with a local agricultural expert","💊 Apply broad-spectrum fungicide as precaution","✂️ Remove visibly infected leaves","💧 Avoid overhead watering","📱 Scan more leaves for better confidence"]}};

function getSuggestions(diseaseName,isHealthy){
  if(isHealthy)return DISEASE_DB.healthy;
  const name=(diseaseName||'').toLowerCase();
  for(const [k,v] of Object.entries(DISEASE_DB)){
    if(k!=='default'&&k!=='healthy'&&name.includes(k.toLowerCase()))return v;}
  return DISEASE_DB.default;}

/* ══ SHOW RESULT ══ */
function showResult(d,el){
  lastR=d;const h=d.binary_status==='Healthy';
  document.getElementById('rHero').className='rhero '+(h?'H':'D');
  document.getElementById('rOrb').textContent=h?'✅':'⚠️';
  document.getElementById('rTag').textContent=h?t('healthy_tag'):t('disease_tag');
  document.getElementById('rNm').textContent=d.disease_name||d.binary_status;
  document.getElementById('rPlant').textContent=d.plant_name||'—';
  document.getElementById('rDis').textContent=d.disease_name||'—';
  document.getElementById('cVal').textContent=d.confidence+'%';
  document.getElementById('cFill').style.width=d.confidence+'%';
  document.getElementById('rMeta').textContent=`${t('analyzed')} ${el}${t('secs')}`;

  // Donut chart
  const arc=document.getElementById('donutArc'),dtxt=document.getElementById('donutTxt');
  const gc=getComputedStyle(document.documentElement).getPropertyValue('--g').trim();
  arc.style.stroke=h?'var(--g)':'var(--r)';
  setTimeout(()=>{arc.setAttribute('stroke-dasharray',`${d.confidence} ${100-d.confidence}`);dtxt.textContent=d.confidence+'%';},100);
  document.getElementById('donutLeg').innerHTML=`
    <div class="dl-item"><div class="dl-dot" style="background:${h?'var(--g)':'var(--r)'}"></div>${h?t('healthy_tag'):t('disease_tag')}</div>
    <div class="dl-item"><div class="dl-dot" style="background:var(--bg4)"></div>Other</div>`;

  // Predictions
  const pl=document.getElementById('predList');pl.innerHTML='';
  d.top_predictions.forEach((p,i)=>{const ph=p.status==='Healthy';
    const div=document.createElement('div');div.className='pr';
    div.innerHTML=`<div class="prk">${i+1}</div><div class="prn">${p.class}</div>
    <div class="mbar"><div class="mfill" style="width:${p.confidence}%"></div></div>
    <div class="ppct">${p.confidence}%</div>
    <span class="ppill ${ph?'ppH':'ppD'}">${p.status}</span>`;
    pl.appendChild(div);});

  // Personalized Report
  const sg=getSuggestions(d.disease_name,h);
  const sevEl=document.getElementById('sevBadge');
  sevEl.textContent=t('sev_'+sg.sev);
  sevEl.className='sev-badge sev-'+sg.sev;
  const sl=document.getElementById('suggList');sl.innerHTML='';
  sg.suggestions.forEach(s=>{const li=document.createElement('li');li.className='sugg-item';
    const [ico,...rest]=s.split(' ');
    li.innerHTML=`<span class="sugg-ico">${ico}</span><span>${rest.join(' ')}</span>`;sl.appendChild(li);});
  document.getElementById('reportBox').style.display='block';

  const rc=document.getElementById('rCard');rc.style.display='block';rc.classList.remove('show-anim');void rc.offsetWidth;rc.classList.add('show-anim');
  document.getElementById('rCard').scrollIntoView({behavior:'smooth',block:'nearest'});
  toast(h?t('t_healthy'):t('t_diseased'));}

/* ══ STATS UPDATE ══ */
function updateStats(d){sT++;if(d.binary_status==='Healthy')sH++;else sD++;
  const dn=d.disease_name||d.binary_status;diseaseCount[dn]=(diseaseCount[dn]||0)+1;
  document.getElementById('sT').textContent=sT;document.getElementById('sH').textContent=sH;document.getElementById('sD').textContent=sD;
  const pct=sT?Math.round(sH/sT*100):0;document.getElementById('hBF').style.width=pct+'%';document.getElementById('hPct').textContent=pct+'%';
  buildDiseaseRank();}

function buildDiseaseRank(){const dr=document.getElementById('diseaseRank');
  const sorted=Object.entries(diseaseCount).sort((a,b)=>b[1]-a[1]).slice(0,5);
  if(!sorted.length)return;dr.innerHTML='';
  sorted.forEach(([nm,cnt],i)=>{const div=document.createElement('div');div.className='pr';
    div.innerHTML=`<div class="prk">${i+1}</div><div class="prn">${nm}</div><div class="ppct">${cnt}x</div>`;
    dr.appendChild(div);});}

/* ══ HISTORY ══ */
function addHistory(d,thumb){histArr.unshift({d,thumb,t:new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})});
  document.getElementById('hCnt').textContent=histArr.length+' '+t('hist_sub');
  // Update history badge + nav count
  const hb=document.getElementById('histBadge');
  if(hb){hb.style.display='';hb.textContent=histArr.length;hb.classList.add('bump');setTimeout(()=>hb.classList.remove('bump'),400);}
  const nc=document.getElementById('navCount');
  if(nc){nc.style.display='';nc.textContent=histArr.length+' scan'+(histArr.length!==1?'s':'');}
  const hl=document.getElementById('hList');hl.innerHTML='';
  histArr.slice(0,8).forEach((item,i)=>{const h2=item.d.binary_status==='Healthy';
    const div=document.createElement('div');div.className='hi';div.style.animationDelay=(i*.04)+'s';
    div.innerHTML=`<img class="hth" src="${item.thumb}"><div class="hi-info"><div class="hin">${item.d.disease_name||item.d.binary_status}</div><div class="him">${item.d.plant_name||'—'} · ${item.t}</div></div><div class="hdot ${h2?'dG':'dR'}"></div>`;
    hl.appendChild(div);});
  buildLineChart();}

function buildHistoryFull(){const hl=document.getElementById('hListFull');hl.innerHTML='';
  if(!histArr.length){hl.innerHTML='<div class="empty"><div class="empt-e">🌱</div>No scans yet</div>';return;}
  histArr.forEach((item,i)=>{const h2=item.d.binary_status==='Healthy';
    const div=document.createElement('div');div.className='hi';div.style.animationDelay=(i*.03)+'s';
    div.innerHTML=`<img class="hth" src="${item.thumb}"><div class="hi-info"><div class="hin">${item.d.disease_name||item.d.binary_status}</div><div class="him">${item.d.plant_name||'—'} · ${item.t} · ${item.d.confidence}%</div></div><div class="hdot ${h2?'dG':'dR'}"></div>`;
    hl.appendChild(div);});}

/* ══ CHARTS ══ */
function gColor(){return cTheme==='dark'?'rgba(110,251,92,':'rgba(22,122,6,'}
function buildLineChart(){
  if(histArr.length<2){document.getElementById('cwrap').style.display='none';return;}
  document.getElementById('cwrap').style.display='block';
  const labs=histArr.slice().reverse().map((_,i)=>'#'+(i+1));
  const vals=histArr.slice().reverse().map(x=>x.d.confidence);
  const gc=cTheme==='dark'?'#6efb5c':'#167a06';
  if(hChart)hChart.destroy();
  hChart=new Chart(document.getElementById('hChart'),{type:'line',data:{labels:labs,datasets:[{data:vals,borderColor:gc,backgroundColor:gc.replace('#6efb5c','rgba(110,251,92,0.08)').replace('#167a06','rgba(22,122,6,0.08)'),borderWidth:1.5,pointRadius:3,pointBackgroundColor:gc,tension:.4,fill:true}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{display:false},y:{min:0,max:100,display:false}},animation:{duration:500}}});}

function buildPieChart(){
  if(!sT)return;
  const gc=cTheme==='dark'?'#6efb5c':'#167a06';
  if(pieChart)pieChart.destroy();
  pieChart=new Chart(document.getElementById('pieChart'),{type:'doughnut',data:{labels:[t('healthy_lbl'),t('diseased_lbl')],datasets:[{data:[sH,sD],backgroundColor:[gc,'rgba(255,95,95,.8)'],borderWidth:0,hoverOffset:6}]},
    options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{color:cTheme==='dark'?'#88a888':'#3d6a3d',font:{size:11,family:'Plus Jakarta Sans'},padding:12}}},cutout:'68%'}});}

function refreshCharts(){if(histArr.length>=2)buildLineChart();if(sT)buildPieChart();}

/* ══ TUTORIAL ══ */
let tutStep=0;const TMAX=4;
function openTut(){tutStep=0;updateTut();document.getElementById('tut').style.display='block';}
function closeTut(){document.getElementById('tut').style.display='none';}
function nextTut(){if(tutStep>=TMAX){closeTut();return;}tutStep++;updateTut();}
function updateTut(){
  for(let i=0;i<=TMAX;i++){document.getElementById('ts'+i).classList.toggle('on',i===tutStep);document.getElementById('td'+i).classList.toggle('on',i===tutStep);}
  document.getElementById('tutNext').textContent=tutStep===TMAX?'Get Started! 🌱':'Next →';}

/* ══ HERO FLOATING PARTICLES ══ */
function initHeroParticles(){
  const container=document.getElementById('heroParts');
  if(!container)return;
  for(let i=0;i<18;i++){
    const p=document.createElement('div');p.className='hp';
    const sz=Math.random()*4+1.5;
    p.style.cssText=`width:${sz}px;height:${sz}px;left:${Math.random()*100}%;animation-duration:${6+Math.random()*10}s;animation-delay:${Math.random()*8}s;opacity:0`;
    container.appendChild(p);
  }
}

window.addEventListener('load',()=>{initHeroParticles();initFarmerBg();newQuote();buildFactStrip('factStrip');if(!localStorage.getItem('ls_tutDone')){openTut();localStorage.setItem('ls_tutDone','1');}});

/* ══ TOAST ══ */
function toast(msg){const el=document.getElementById('toast');el.textContent=msg;el.classList.add('show');setTimeout(()=>el.classList.remove('show'),2700);}

/* ══ ACTIONS ══ */
function copyRes(){if(!lastR)return;navigator.clipboard.writeText(`LeafScan Result\nPlant: ${lastR.plant_name}\nStatus: ${lastR.binary_status}\nDisease: ${lastR.disease_name}\nConfidence: ${lastR.confidence}%`).then(()=>toast(t('t_copied')));}
function dlRes(){if(!lastR)return;const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(lastR,null,2)],{type:'application/json'}));a.download='leafscan_result.json';a.click();toast(t('t_saved'));}
function shareRes(){if(!lastR)return;const txt=`🌿 LeafScan: ${lastR.binary_status} — ${lastR.disease_name} (${lastR.confidence}%)`;if(navigator.share)navigator.share({title:'LeafScan',text:txt});else navigator.clipboard.writeText(txt).then(()=>toast('↗ '+t('t_copied')));}
function printReport(){if(!lastR)return;window.print();}

/* ══ FEEDBACK ══ */
function setStar(v){fbStar=v;document.querySelectorAll('.fbstar').forEach((s,i)=>s.classList.toggle('on',i<v));}
function toggleTag(el){el.classList.toggle('on');}
function sendFeedback(){
  const txt=document.getElementById('fbTxt').value.trim();
  const tags=[...document.querySelectorAll('.fbtag.on')].map(t2=>t2.textContent);
  if(!fbStar&&!txt&&!tags.length){toast('⚠️ Please add a rating or comment');return;}
  fbArr.unshift({star:fbStar,tags,txt,time:new Date().toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})});
  const fl=document.getElementById('fbList');fl.innerHTML='';
  fbArr.forEach(fb=>{const div=document.createElement('div');div.className='hi';
    div.innerHTML=`<div style="font-size:1rem;flex-shrink:0">${'⭐'.repeat(fb.star)||'💬'}</div>
    <div class="hi-info"><div class="hin">${fb.txt||fb.tags.join(', ')||'Feedback'}</div><div class="him">${fb.time}</div></div>`;
    fl.appendChild(div);});
  document.getElementById('fbTxt').value='';fbStar=0;
  document.querySelectorAll('.fbstar').forEach(s=>s.classList.remove('on'));
  document.querySelectorAll('.fbtag').forEach(t2=>t2.classList.remove('on'));
  toast(t('t_fb'));}
</script>
</body>
</html>"""

@app.route("/")
def index():
    return HTML

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Image nahi mili"}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "File select nahi ki"}), 400
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    try:
        result = predict_image(filepath, top_k=5)
        return jsonify(result)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

if __name__ == "__main__":
    print("\n🌿 LeafScan v4 — Farmer's Complete AI Companion")
    # print("   http://localhost:5000\n")
    # app.run(debug=True, port=5000)

    import os
    app.run(
      host="0.0.0.0",
      port=int(os.environ.get("PORT", 5000))
)