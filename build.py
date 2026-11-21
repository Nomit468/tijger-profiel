"""Bouwt de vier rolprofielen (Tijger, Panter, Wolf, Beer) als losse HTML-pagina's.

Draaien: python3 build.py  -> schrijft index.html, panter.html, wolf.html, beer.html
Bron: korfballadvisor.blogspot.com (profielen uit 2009-2011).
"""
import pathlib

OUT = pathlib.Path(__file__).parent

ORDER = [("tijger", "index.html", "Tijger"), ("panter", "panter.html", "Panter"),
         ("wolf", "wolf.html", "Wolf"), ("beer", "beer.html", "Beer")]
LINK = {k: f for k, f, _ in ORDER}

CHECK_SVG = ('<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.5l3.2 3L13 4.5" fill="none" '
             'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def nl(v):
    return f"{v:.2f}".replace(".", ",")


def rng(lo, hi):
    return nl(lo) if lo == hi else f"{nl(lo)}–{nl(hi)}"


# ---------- onderdelen ----------

def tokens(light, dark):
    def decl(d):
        return "; ".join(f"--{k}: {v}" for k, v in d.items())
    return (f":root {{ {decl(light)} }}\n"
            f"@media (prefers-color-scheme: dark) {{ :root:not([data-theme=\"light\"]) {{ {decl(dark)} }} }}\n"
            f":root[data-theme=\"dark\"] {{ {decl(dark)} }}")


def ruler(marks, aria):
    """marks: (label, lo, hi, side) met side c/l/r. Schaal 0-3,50 m (korfhoogte)."""
    y = lambda h: 280 - h * (260 / 3.5)
    parts = [
        '<line class="ln" x1="40" y1="280" x2="40" y2="22" stroke-width="3"/>',
        '<line class="ln" x1="20" y1="280" x2="290" y2="280" stroke-width="1.5"/>',
        '<ellipse class="korf" cx="40" cy="20" rx="20" ry="5" stroke-width="3"/>',
        '<line class="tick" x1="62" y1="20" x2="82" y2="20"/>',
        '<text x="88" y="24">korf · 3,50 m</text>',
    ]
    prev = 24
    xs = {"c": (34, 12), "l": (27, 9), "r": (44, 9)}
    for label, lo, hi, side in sorted(marks, key=lambda m: -m[2]):
        top, bot = y(hi), y(lo)
        h = max(bot - top, 5)
        if bot - top < 5:
            top = (top + bot) / 2 - 2.5
        yc = top + h / 2
        ly = max(yc + 4, prev + 15)
        prev = ly
        x, w = xs[side]
        parts.append(f'<rect class="band" x="{x}" y="{top:.1f}" width="{w}" height="{h:.1f}" rx="1.5"/>')
        parts.append(f'<line class="tick" x1="{x + w + 2}" y1="{yc:.1f}" x2="82" y2="{ly - 4:.1f}"/>')
        parts.append(f'<text x="88" y="{ly:.1f}">{label} · {rng(lo, hi)} m</text>')
    parts.append('<text class="mut" x="88" y="276">vloer · 0 m</text>')
    return (f'<svg class="ruler" viewBox="0 0 300 300" role="img" aria-label="{aria}">'
            + "".join(parts) + "</svg>")


def range_chart(title, unit, vmax, step, rows, me):
    n = vmax // step
    out = [f'<div class="rc"><h4>{title}</h4>']
    for name, lo, hi in rows:
        left, width = lo / vmax * 100, (hi - lo) / vmax * 100
        cls = "rc-row me" if name == me else "rc-row"
        out.append(f'<div class="{cls}"><span>{name}</span><div class="rc-track" style="--step: {100 / n:.4f}%">'
                   f'<div class="rc-bar" style="left: {left:.2f}%; width: {width:.2f}%"></div></div>'
                   f'<span class="rc-val">{lo}–{hi}{unit}</span></div>')
    ticks = "".join(f'<span style="left: {i * step / vmax * 100:.2f}%">{i * step}</span>' for i in range(n + 1))
    out.append(f'<div class="rc-axis" aria-hidden="true"><span></span><div>{ticks}</div><span></span></div></div>')
    return "".join(out)


def items(lst):
    out = []
    for it in lst:
        tag = f'<span class="tag">{it[0]}</span>' if it[0] else ""
        out.append(f'<div class="item">{tag}<h3>{it[1]}</h3><p>{it[2]}</p></div>')
    return "".join(out)


def section(eyebrow, h2, body, intro=None, extra_cls=""):
    intro_html = f"<p>{intro}</p>" if intro else ""
    return (f'<section><div class="wrap{extra_cls}"><div class="sec-head"><span class="eyebrow">{eyebrow}</span>'
            f'<h2>{h2}</h2>{intro_html}</div>{body}</div></section>')


def page(key, r):
    cur = ' aria-current="page"'
    nav = "".join(
        f'<a href="{f}"{cur if k == key else ""}>{name}</a>' for k, f, name in ORDER)
    stats = "".join(
        f'<div class="stat"><b>{b}</b><span>{s}</span>{f"<small>{sm}</small>" if sm else ""}</div>'
        for b, s, sm in r["stats"])
    facts = "".join(f'<div class="fact"><dt>{a}</dt><dd>{b}</dd></div>' for a, b in r["facts"])
    checks = "".join(
        f'<li><label for="c{i}"><input type="checkbox" id="c{i}"><span class="box">{CHECK_SVG}</span>'
        f'<span>{t}</span></label></li>' for i, t in enumerate(r["check"], 1))
    watch = ""
    if r.get("watch"):
        lis = "".join(f'<li><h3>{h}</h3><p>{p}</p><p class="tip"><b>Tip:</b> {t}</p></li>' for h, p, t in r["watch"])
        watch = section("Eerlijk is eerlijk", f"Waar een {key} op moet letten", f'<ul class="watch">{lis}</ul>',
                        "Elk type heeft valkuilen. Deze komen uit het profiel zelf. De tips zijn een aanvulling.")
    sources = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{t}</a> ({d})</li>' for t, u, d in r["sources"])
    others = " · ".join(f'<a href="{f}">{n}</a>' for k, f, n in ORDER if k != key)
    low, mid, high = r["verdicts"]
    n = len(r["check"])

    return f"""<!doctype html>
<html lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Profiel van de {r['name']}</title>
<meta name="description" content="{r['meta']}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;600;800&display=swap">
<link rel="stylesheet" href="style.css">
<style>
{tokens(*r['tokens'])}
</style>
</head>
<body>
<header class="hero">
  <svg class="deco" viewBox="0 0 400 400" preserveAspectRatio="xMaxYMid slice" aria-hidden="true">{r['deco']}</svg>
  <div class="wrap">
    <nav class="roles" aria-label="Rollen in de aanval">{nav}</nav>
    <span class="eyebrow">Korfbal · rollen in de aanval</span>
    <h1>De {r['name']}</h1>
    <p class="lead">{r['lead']}</p>
    <p class="note">Dit profiel is gebaseerd op hoe de topspelers van het Nederlands team deze rol speelden.</p>
  </div>
</header>
<main>
{section("In cijfers", r['stats_h2'], f'<div class="stats">{stats}</div><div class="feature">{r["feature"]}</div>')}
{section("Op het veld", f"Wat een {key} doet", f'<div class="grid">{items(r["skills"])}</div>')}
{section("In je hoofd", f"Hoe een {key} denkt", f'<div class="grid">{items(r["mind"])}</div>', r['mind_intro'])}
{section("Het lijf", f"Hoe hoog een top-{key} reikt",
         f'<div class="body-wrap">{ruler(*r["ruler"])}<div><dl class="facts">{facts}</dl><p class="callout">{r["callout"]}</p></div></div>')}
{watch}
<section><div class="wrap duo">{r['duo']}</div></section>
{section("Even checken", f"Zit er een {key} in jou?", f'''<ul class="check" id="check">{checks}</ul>
<div class="result" aria-live="polite"><b id="score">0 van {n}</b><span id="verdict">Vink hierboven aan wat bij je past.</span></div>''',
         "Vink aan wat bij je past. Geen test, gewoon om over na te denken.")}
</main>
<footer>
  <div class="wrap">
    <p>Bron: de blog Korfball Advisor. De profielen zijn gebaseerd op topspelers van het Nederlands team van toen en herschreven voor spelers van 14 tot 19 jaar. Tips en de check zijn toegevoegd.</p>
    <ul>{sources}</ul>
    <p>Andere rollen: {others}</p>
  </div>
</footer>
<script>
(function () {{
  var boxes = document.querySelectorAll('#check input');
  var score = document.getElementById('score');
  var verdict = document.getElementById('verdict');
  function update() {{
    var n = 0;
    boxes.forEach(function (b) {{ if (b.checked) n++; }});
    score.textContent = n + ' van {n}';
    if (n === 0) verdict.textContent = 'Vink hierboven aan wat bij je past.';
    else if (n <= 2) verdict.textContent = {low!r};
    else if (n <= 5) verdict.textContent = {mid!r};
    else verdict.textContent = {high!r};
  }}
  boxes.forEach(function (b) {{ b.addEventListener('change', update); }});
  update();
}})();
</script>
</body>
</html>
"""


# ---------- inhoud ----------

GROW = "Dit zijn maten van volwassen topspelers. Jij groeit nog. Kijk dus vooral naar wat je zelf kunt trainen"

ROLES = {}

ROLES["tijger"] = dict(
    name="Tijger",
    meta="Het korfbalprofiel van de Tijger, herschreven voor spelers van 14 tot 19 jaar.",
    tokens=(dict(band="#E2620B", **{"on-band": "#14201A"}, deco="#14201A", acc="#B84D06", fill="#E2620B",
                 **{"on-fill": "#14201A"}, soft="#FBE3D2"),
            dict(band="#FF8A2B", **{"on-band": "#14201A"}, deco="#14201A", acc="#FF9A45", fill="#FF8A2B",
                 **{"on-fill": "#14201A"}, soft="#3A2414")),
    deco=('<polygon class="d" points="400,10 150,46 400,70"/><polygon class="d" points="400,105 210,128 400,150"/>'
          '<polygon class="d" points="400,185 120,224 400,252"/><polygon class="d" points="400,286 230,306 400,326"/>'
          '<polygon class="d" points="400,352 170,384 400,400"/><polygon class="d" points="290,0 250,0 330,40"/>'),
    lead="De schutter van het team. Als het spannend wordt, wil de tijger de bal. In de opstelling is dit de hoofdrol.",
    stats_h2="Een tijger in één wedstrijd",
    stats=[("20–30", "schoten per wedstrijd", None), ("20–30%", "daarvan gaat erin", None),
           ("4–6", "doelpunten uit het spel", "7–8 met vrije ballen en strafworpen erbij"),
           ("3–6 m", "van de paal", "Sta je hier vrij, dan schiet je. Altijd.")],
    feature=('<div class="miss"><div><h3>Missen hoort erbij</h3><p>Een top-tijger mist ongeveer drie van de vier schoten. '
             'Toch blijft een tijger schieten. Wie niet schiet, scoort ook niet. Een misser is voor een tijger geen reden '
             'om het de volgende keer niet te proberen.</p></div><div><div class="dots" role="img" aria-label="25 schoten, waarvan 6 raak">'
             + "".join(f'<span class="dot{" hit" if i in (2, 7, 11, 16, 19, 23) else ""}"></span>' for i in range(25))
             + '</div><div class="legend"><span><i class="h"></i>raak</span><span><i class="m"></i>mis</span><span>25 schoten</span></div></div></div>'),
    skills=[
        ("Wapen nr. 1", "Het afstandschot", "Uit een vrije positie gaat meer dan 30% erin. Omdat je verdediger daar bang voor is, krijg je ruimte voor de doorloopbal en de uitwijkbal."),
        ("Techniek", "Schieten vanaf hoofdhoogte", "Je zet het schot in op hoofdhoogte. Daardoor kan je verdediger het lastig blokken of de bal van richting laten veranderen."),
        ("Duel", "Winnen van je Guard", "Je wisselt steeds van tempo en richting. Ben je vrij, dan neem je alles even terug, kom je in balans en schiet je raak."),
        ("Altijd", "Elk moment een schot", "Je kunt op ieder moment van de wedstrijd tot een schot komen, juist ook als de spanning het hoogst is."),
        ("Basis", "Balvaardig", "Tijgers zijn van jongs af met een bal bezig. Je kunt ermee jongleren. Hoe beter je balgevoel, hoe meer opties je hebt."),
        ("Stilstaande bal", "Vrije ballen en strafworpen", "Ongeveer 30% van de doelpunten van een tijger komt uit vrije ballen en strafworpen. Die punten liggen voor het oprapen."),
    ],
    mind_intro="Dit deel maakt het grootste verschil. Lengte heb je niet in de hand, je mindset wel.",
    mind=[
        (None, "Honger naar de goal", "Scoren staat centraal, in de wedstrijd en op de training. Je wilt er elke week beter in worden."),
        (None, "Lef", "Je durft risico te nemen. Ook als een misser betekent dat jullie de bal kwijt zijn, schiet je als je vrij staat."),
        (None, "Rust als het spannend is", "In de laatste minuten wil jij de bal. Je neemt de verantwoordelijkheid en blijft stabiel, wat er ook gebeurt."),
        (None, "Snel weer door", "Gemist? Volgende. Je herstelt snel van tegenslag en laat je niet uit het veld slaan."),
        (None, "Nooit wegduiken", "Je loopt geen duel uit de weg en verstopt je niet achter je teamgenoten."),
        (None, "Je tegenstander lezen", "Je ziet snel waar je Guard zwak is, en daar speel je op in."),
    ],
    ruler=([("sprong", 3.20, 3.30, "c"), ("staand", 2.60, 2.60, "c"), ("lengte", 1.90, 2.00, "c")],
           "Schaal van 0 tot 3,50 meter: lengte 1,90 tot 2,00 m, reikhoogte staand 2,60 m, in sprong 3,20 tot 3,30 m, korf op 3,50 m"),
    facts=[("Lengte", "1,90–2,00 m"), ("Reikhoogte staand", "2,60 m"), ("Reikhoogte sprong", "3,20–3,30 m"),
           ("Beweging", "Snel, wendbaar, explosief"), ("Ogen en handen", "Uitstekende oog-handcoördinatie, kan goed diepte zien")],
    callout=GROW + ": snelheid, explosiviteit, je schot en je balgevoel.",
    watch=[
        ("Tunnelvisie", "Tijgers kijken vooral naar voren, naar de korf. Wat er naast ze gebeurt, zien ze minder.",
         "kijk voor je schot één keer opzij. Staat een teamgenoot vrijer?"),
        ("Weinig oog voor de rest", "Veel tijgers letten weinig op de kansen van de Panter, de Wolf of de Beer. Een tijger gaat ook niet snel dubbelen om een ander vrij te spelen.",
         "een assist telt ook. Een tijger die af en toe aangeeft, is moeilijker te verdedigen."),
        ("Hoge eisen aan je team", "Een tijger verwacht veel van teamgenoten en wil dat ze hem of haar begrijpen.",
         "praat met je aangevers over wanneer jij de bal wilt. Dat werkt beter dan boos kijken na een slechte pass."),
    ],
    duo=('<div><span class="eyebrow">Je beste maatje</span><h2>De Wolf</h2><p>De Wolf is de beste helper van de tijger. '
         'Een Wolf voelt aan waar je staat en op welk moment je de bal moet krijgen. Daardoor werken jullie snel en slim samen. '
         '<a href="wolf.html">Lees het profiel van de Wolf</a>.</p></div>'
         '<div><span class="eyebrow">Geen jongensrol</span><span class="big">74</span><p>doelpunten in 14 wedstrijden, gemaakt door '
         'de enige vrouwelijke tijger in de Nederlandse competitie die 20–30% scoorde. Tijgers waren toen nog vooral mannen. '
         'De schrijver van het profiel vond dat jammer: er waren te weinig vrouwelijke tijgers. Meiden, deze rol is ook voor jullie.</p></div>'),
    check=["Als het spannend wordt, wil ik de bal.", "Na een misser denk ik meteen: volgende.",
           "Ik schiet liever één keer te veel dan één keer te weinig.", "Een duel ga ik niet uit de weg.",
           "Schieten is het leukste deel van de training.", "Ik zie snel waar mijn verdediger zwak is.",
           "Sta ik vrij, dan twijfel ik niet.", "Ik kan snel wisselen van tempo en richting."],
    verdicts=("Je kracht zit waarschijnlijk ergens anders. Kijk ook eens bij de Panter, de Wolf of de Beer.",
              "Er zit een tijger in je. Werk aan je schot en je lef, en kijk wat er gebeurt.",
              "Tijger-alarm. Vraag je trainer eens of deze rol bij je past."),
    sources=[("Profiel van Tijger en de uitwerking van de rol van Tijger", "https://korfballadvisor.blogspot.com/2011/06/profiel-van-tijger-en-de-uitwerking-van.html", "2011")],
)

ROLES["panter"] = dict(
    name="Panter",
    meta="Het korfbalprofiel van de Panter, herschreven voor spelers van 14 tot 19 jaar.",
    tokens=(dict(band="#2A2342", **{"on-band": "#F2EEFF"}, deco="#D7F05A", acc="#6247C9", fill="#6B4FD0",
                 **{"on-fill": "#FFFFFF"}, soft="#E8E3F7"),
            dict(band="#271F40", **{"on-band": "#F2EEFF"}, deco="#D7F05A", acc="#B7A5FF", fill="#A891FF",
                 **{"on-fill": "#14201A"}, soft="#2A2442")),
    deco=('<g transform="rotate(-8 300 190)"><ellipse class="d" cx="250" cy="190" rx="46" ry="19"/>'
          '<ellipse class="b" cx="250" cy="190" rx="5" ry="17"/><ellipse class="d" cx="360" cy="190" rx="46" ry="19"/>'
          '<ellipse class="b" cx="360" cy="190" rx="5" ry="17"/></g>'),
    lead="De schaduwspits. De Panter speelt vlak naast of achter de Tijger en slaat toe zodra de verdediging even naar de Tijger kijkt.",
    stats_h2="Een panter in één wedstrijd",
    stats=[("10–18", "schoten per wedstrijd", "Minder dan de Tijger"), ("20–30%", "daarvan gaat erin", "Net zo raak als de Tijger"),
           ("2e", "tempo in de aanval", "De Tijger neemt het initiatief, jij volgt direct"),
           ("6–8 m", "van de paal", "Daar begin je meestal je actie")],
    feature=('<div><h3>Zo komt een panter vrij</h3><p>Een panter krijgt minder kansen dan een tijger. Het geheim is geduld: '
             'je wacht tot je moment komt, en dan sta je meteen klaar.</p></div>'
             '<ol class="seq"><li><b>De Tijger gaat het duel aan</b><span>De verdediging let op de Tijger.</span></li>'
             '<li><b>Jij beweegt in de schaduw</b><span>Naast de Tijger of op de lijn Tijger–paal, zo dat jouw Guard de bal niet goed ziet.</span></li>'
             '<li><b>Je kans komt</b><span>Je staat in balans, met je hoofd en je lijf, en maakt hem af.</span></li></ol>'),
    skills=[
        ("Timing", "Spelen in het tweede tempo", "De Tijger neemt het initiatief en trekt de aandacht. Jij bent altijd klaar om het over te nemen."),
        ("Positie", "Naast of achter de Tijger", "Je beweegt direct naast de Tijger (dubbelpass, korte lijn) of op de lijn tussen Tijger en paal (dubbelpass, lange lijn)."),
        ("Kijken", "Split vision", "Je houdt oogcontact met de Tijger en houdt tegelijk je eigen verdediger in de gaten."),
        ("Bewegen", "Altijd in beweging", "Je zoekt plekken waar je Guard de bal niet of maar half kan zien."),
        ("Passen", "Een goede passer", "Met een lange pass verander je de richting van de aanval en geef je de assist aan Tijger, Wolf of Beer. Je helpt de Wolf ook de bal rond te spelen."),
        ("Rouleren", "Wisselen van rol", "Een panter kan de rol van Tijger en van Wolf overnemen. Daardoor weet de verdediging niet waar het gevaar vandaan komt."),
    ],
    mind_intro="Geduld is je superkracht. Je krijgt minder kansen dan de Tijger, dus elke kans telt.",
    mind=[
        (None, "Scoringsdrift", "Je wilt scoren en blijft werken aan je schot."),
        (None, "Passie", "Je houdt van wedstrijden spelen en van trainen. Je bent een harde werker."),
        (None, "Strijdlust", "Je bent strijdlustig en veerkrachtig. Een tegenslag houdt je niet tegen."),
        (None, "Weten wie je bent", "Je kent je rol, je sterke punten en ook wat je nog niet goed kunt."),
        (None, "Geduld", "Je kunt omgaan met druk en je kunt wachten op het juiste moment."),
        (None, "Teamspeler", "Je speelt voor de doelen van het team en je let goed op de Tijger en de Wolf."),
    ],
    ruler=([("sprong spelers", 3.00, 3.30, "l"), ("sprong speelsters", 2.70, 2.85, "r"),
            ("staand spelers", 2.45, 2.55, "l"), ("staand speelsters", 2.25, 2.40, "r"),
            ("lengte spelers", 1.80, 2.00, "l"), ("lengte speelsters", 1.72, 1.85, "r")],
           "Schaal van 0 tot 3,50 meter met lengte en reikhoogte van spelers en speelsters in de rol van Panter, korf op 3,50 m"),
    facts=[("Lengte", "spelers 1,80–2,00 m<br>speelsters 1,72–1,85 m"),
           ("Reikhoogte staand", "spelers 2,45–2,55 m<br>speelsters 2,25–2,40 m"),
           ("Reikhoogte sprong", "spelers 3,00–3,30 m<br>speelsters 2,70–2,85 m"),
           ("Beweging", "Explosief in korte bewegingen met richtingsveranderingen, snel en wendbaar"),
           ("Ogen en handen", "Uitstekende oog-handcoördinatie")],
    callout=GROW + ": korte explosieve acties, snel van richting veranderen, je pass en je schot. In de meetlat staan spelers links van de paal en speelsters rechts.",
    duo=('<div><span class="eyebrow">Waarom een panter?</span><h2>Geen vak vol tijgers</h2><p>Met alleen tijgers in de aanval worden '
         'spelers rivalen in plaats van maatjes. Een panter is minder sterk in het duel met de Guard dan een tijger, maar profiteert '
         'juist van de druk die de tijger zet. <a href="index.html">Lees het profiel van de Tijger</a>.</p></div>'
         '<div><span class="eyebrow">Voor iedereen</span><h2>Spelers én speelsters</h2><p>Jorrit Bergsma en Marijke van den Berg werden '
         'in 2009 genoemd als hele goede panters. Het profiel geeft ook aparte maten voor speelsters. De Panter is dus een rol voor jongens en meiden.</p></div>'),
    check=["Ik kan geduldig wachten op mijn kans.", "Als ik een kans krijg, sta ik meteen klaar.",
           "Ik geef net zo graag een goede pass als dat ik scoor.", "Ik zie tegelijk de bal en mijn verdediger.",
           "Ik vind het niet erg dat een ander vaker schiet dan ik.", "Ik blijf bewegen, ook zonder bal.",
           "Ik kan snel stoppen en van richting veranderen.", "Ik vind het leuk om van rol te wisselen."],
    verdicts=("Je kracht zit waarschijnlijk ergens anders. Kijk ook eens bij de Tijger, de Wolf of de Beer.",
              "Er zit een panter in je. Train je timing en je pass, en kijk wat er gebeurt.",
              "Panter-alarm. Vraag je trainer eens of deze rol bij je past."),
    sources=[("Profiel van de topspeler in de rol van Panter", "https://korfballadvisor.blogspot.com/2009/10/zij-vormen-samen-de-zogenaamde-action.html", "2009"),
             ("The Panther in the Line-up", "https://korfballadvisor.blogspot.com/2009/03/panther-in-line-up.html", "2009")],
)

ROLES["wolf"] = dict(
    name="Wolf",
    meta="Het korfbalprofiel van de Wolf, herschreven voor spelers van 14 tot 19 jaar.",
    tokens=(dict(band="#9DBEDF", **{"on-band": "#14201A"}, deco="#F5F7F1", acc="#2F6496", fill="#3D74A8",
                 **{"on-fill": "#FFFFFF"}, soft="#DDE8F3"),
            dict(band="#6F94BA", **{"on-band": "#0F1612"}, deco="#E9EEF4", acc="#9CC3EA", fill="#7FAEDB",
                 **{"on-fill": "#14201A"}, soft="#1C2A38")),
    deco=('<circle class="d" cx="300" cy="175" r="110"/><circle class="b" cx="262" cy="140" r="18" opacity=".25"/>'
          '<circle class="b" cx="335" cy="215" r="26" opacity=".2"/><circle class="b" cx="320" cy="120" r="9" opacity=".25"/>'),
    lead="De aangever. De Wolf heeft de meest sociale rol in de aanval: jij zorgt dat de Tijger en de Panter kunnen scoren.",
    stats_h2="Een wolf in één wedstrijd",
    stats=[("5–10", "schoten per wedstrijd", None), ("15–30%", "daarvan gaat erin", None),
           ("4–6 m", "rond de korf", "Daar sta je na de opbouw"),
           ("10+ m", "strakke pass", "Zo ver geeft een goede wolf een bal strak aan")],
    feature=('<div><h3>Een aanval door de ogen van de wolf</h3><p>In korfbal heb je 25 seconden om te schieten. '
             'In die tijd heeft de wolf twee taken.</p></div>'
             '<div><div class="clock-bar" role="img" aria-label="Schotklok van 25 seconden: eerste 9 seconden transporteur, daarna aangever"><i></i><i></i></div>'
             '<div class="clock-scale" aria-hidden="true"><span>25 s</span><span><span>±16 s</span><span>0 s</span></span></div>'
             '<div class="clock-text"><div><b>Transporteur</b><span>Je laat de bal door het hele vak gaan, terwijl de opstelling van 4-0 naar 3-1 en 2-2 gaat.</span></div>'
             '<div><b>Aangever</b><span>Rond 16 seconden op de klok ga je naar de aangeefpositie, net voor de korfzone. Vandaar voed je de Tijger, daarna de Panter.</span></div></div></div>'),
    skills=[
        ("Kerntaak", "Aangeven", "Je belangrijkste taak is de Tijger en de Panter voeden. Je leest waar en hoe de Tijger vrijkomt, en daarna de Panter."),
        ("Opbouw", "Transporteur", "In de opbouw laat je de bal door het hele vak gaan, van voor naar achter en van links naar rechts. Zo komen je vakgenoten op hun plek."),
        ("Route", "Naar de aangeefpositie", "Je komt vanaf de achterlijn over de lijn paal–Tijger, snijdend langs het blok, tot net voor de korfzone."),
        ("Techniek", "Van hoog naar hoog", "Richting en tempo van de bal zijn belangrijk. Je pass gaat van hoog naar hoog, zodat de schutter meteen kan schieten."),
        ("Lezen", "Twee dingen tegelijk", "Je leest Tijger en Panter tegelijk en coacht ze: waar en wanneer komt de bal."),
        ("Trucje", "De valse wolf", "Komt jouw Guard voorverdedigen om de bal te zien? Dan word je zelf schutter, of speel je de Beer vrij."),
    ],
    mind_intro="Belangrijk: je helpt de Tijger en de Panter het best als je zelf ook kunt scoren.",
    mind=[
        (None, "Strijdlust", "Je houdt van het duel en bent strijdlustig."),
        (None, "Winnaarsmentaliteit", "Door je houding geef je je vakgenoten vertrouwen."),
        (None, "Onvermoeibaar", "Je stopt nooit en geeft niet op."),
        (None, "Rust", "Tijger en Panter moeten onder druk scoren. Jij blijft rustig en beheerst, en dat helpt hen."),
        (None, "Dienstbaar", "Je speelt voor het vak en het team, en je inspireert anderen door steeds weer te helpen."),
        (None, "Slim en flexibel", "Je leest wat de voorverdediger van plan is en profiteert daarvan rond de korf."),
    ],
    ruler=([("sprong", 2.66, 2.80, "c"), ("staand", 2.25, 2.35, "c"), ("lengte", 1.72, 1.80, "c")],
           "Schaal van 0 tot 3,50 meter: lengte 1,72 tot 1,80 m, reikhoogte staand 2,25 tot 2,35 m, in sprong 2,66 tot 2,80 m, korf op 3,50 m"),
    facts=[("Lengte", "1,72–1,80 m"), ("Reikhoogte staand", "2,25–2,35 m"), ("Reikhoogte sprong", "2,66–2,80 m"),
           ("Beweging", "Goede loper met een grote actieradius, snel van richting"),
           ("Handen", "Scoort met twee handen, en eenhandig met links én rechts")],
    callout="Een wolf hoeft niet lang te zijn. Topwolven varieerden van 1,70 m (Jet Brandsma) tot 1,82 m (Kim Cocu). Train vooral je pass, je overzicht en je schot dicht bij de korf.",
    duo=('<div><span class="eyebrow">Je maatjes</span><h2>Tijger, Panter en Beer</h2><p>Jij voelt het beste moment van de Tijger en de Panter aan. '
         'Rond de korf werk je samen met de Beer om de beste aangeefpositie te krijgen. '
         '<a href="index.html">Tijger</a> · <a href="panter.html">Panter</a> · <a href="beer.html">Beer</a></p></div>'
         '<div><span class="eyebrow">Wie speelt wolf?</span><h2>Meestal een speelster</h2><p>In het Nederlands team was de wolf meestal een vrouw. '
         'Een goede wolf kan ook rouleren met de Panter. Een enkeling met veel lengte kan zelfs als Beer spelen.</p></div>'),
    check=["Ik geef liever een goede assist dan dat ik zelf schiet.", "Ik zie snel wie er vrij gaat komen.",
           "Ik blijf rustig als anderen gestrest zijn.", "Ik praat en coach veel in het veld.",
           "Ik loop de hele wedstrijd door.", "Ik geef strakke, harde passes.",
           "Ik kan zelf ook scoren dicht bij de korf.", "Ik voel goed aan wat mijn teamgenoten nodig hebben."],
    verdicts=("Je kracht zit waarschijnlijk ergens anders. Kijk ook eens bij de Tijger, de Panter of de Beer.",
              "Er zit een wolf in je. Train je pass en je overzicht, en kijk wat er gebeurt.",
              "Wolf-alarm. Vraag je trainer eens of deze rol bij je past."),
    sources=[("Profiel van de topspeler in de rol van Wolf", "https://korfballadvisor.blogspot.com/2009/10/profiel-van-de-topspeler-in-de-rol-van_22.html", "2009"),
             ("Rol: De Wolf", "https://korfballadvisor.blogspot.com/2009/09/rol-de-wolf.html", "2009")],
)

ROLES["beer"] = dict(
    name="Beer",
    meta="Het korfbalprofiel van de Beer, herschreven voor spelers van 14 tot 19 jaar.",
    tokens=(dict(band="#7A4E26", **{"on-band": "#FFF4E8"}, deco="#4E3015", acc="#8A5A2B", fill="#8A5A2B",
                 **{"on-fill": "#FFFFFF"}, soft="#F1E4D6"),
            dict(band="#6B4421", **{"on-band": "#FFF4E8"}, deco="#3E2610", acc="#D9A46B", fill="#D9A46B",
                 **{"on-fill": "#14201A"}, soft="#33251A")),
    deco=('<polygon class="d" points="200,30 226,26 290,372 276,376"/><polygon class="d" points="262,22 288,18 352,364 338,368"/>'
          '<polygon class="d" points="324,30 350,26 414,372 400,376"/>'),
    lead="De rebounder. De Beer staat onder de korf, vangt de missers en geeft het vak een nieuwe kans.",
    stats_h2="Een beer in één wedstrijd",
    stats=[("4–12", "schoten per wedstrijd", None), ("30–50%", "daarvan gaat erin", "De hoogste trefkans van alle rollen"),
           ("70–80%", "van de aanvalsrebounds", "wint een top-beer"),
           ("Zone", "rond de paal", "Je werkt in de korfzone of net daarbuiten")],
    feature=('<div><h3>Minder schoten, meer raak</h3><p>Van de vier rollen schiet de beer het minst, maar wel het vaakst raak. '
             'Je schiet van dichtbij, in de korfzone.</p></div><div class="charts">'
             + range_chart("Schoten per wedstrijd", "", 30, 10,
                           [("Tijger", 20, 30), ("Panter", 10, 18), ("Wolf", 5, 10), ("Beer", 4, 12)], "Beer")
             + range_chart("Trefkans", "%", 60, 10,
                           [("Tijger", 20, 30), ("Panter", 20, 30), ("Wolf", 15, 30), ("Beer", 30, 50)], "Beer")
             + '</div>'),
    skills=[
        ("Plek", "De korfzone", "Je werkt in de zone rond de paal of net daarbuiten."),
        ("Kerntaak", "Rebounds winnen", "Je vangt schoten af die niet raak zijn. Zo blijft de aanval doorgaan en krijgt je vak een nieuwe kans."),
        ("Twee dingen tegelijk", "Lezen en uitblokken", "Je leest waar de bal gaat vallen en blokt tegelijk je verdediger uit."),
        ("Positie", "Je plek houden", "Je leest het spel. Zo houd je je positie vast of verbeter je die tijdens de aanval."),
        ("Scoren", "Handig rond de korf", "Je scoort dichtbij met allerlei technieken, met één en met twee handen."),
        ("Samenwerken", "Met de Wolf", "Rond de korf speel je met de Wolf. Komt de Guard van de Wolf voorverdedigen, dan kan de Wolf jou vrijspelen."),
    ],
    mind_intro="Een beer geeft het vak houvast. Je staat er, wat er ook gebeurt.",
    mind=[
        (None, "Strijdlust", "Je houdt van het duel en bent strijdlustig."),
        (None, "Winnaarsmentaliteit", "Door je houding en je plek in het vak geef je je vakgenoten vertrouwen."),
        (None, "Onverzettelijk", "Je bent taai, geeft niet op en laat je niet wegduwen."),
        (None, "Standvastig", "Onder druk blijf je staan. Daarmee inspireer je de rest van je vak."),
        (None, "Dienstbaar", "Je speelt voor het vak en het team."),
        (None, "Slim", "Je leest wat de voorverdediger wil doen, profiteert daarvan en coacht je vakgenoten."),
    ],
    ruler=([("sprong", 3.10, 3.20, "c"), ("staand", 2.50, 2.60, "c"), ("lengte", 1.88, 2.00, "c")],
           "Schaal van 0 tot 3,50 meter: lengte 1,88 tot 2,00 m, reikhoogte staand 2,50 tot 2,60 m, in sprong 3,10 tot 3,20 m, korf op 3,50 m"),
    facts=[("Lengte", "1,88–2,00 m"), ("Reikhoogte staand", "2,50–2,60 m"), ("Reikhoogte sprong", "3,10–3,20 m"),
           ("Bouw", "Stevig, zodat je de tegenstander uit de afvangzone kunt blokken"),
           ("Ogen en handen", "Zeer goede oog-handcoördinatie, handig met één en twee handen")],
    callout=GROW + ": positie kiezen, uitblokken, de timing van je sprong en scoren met beide handen.",
    duo=('<div><span class="eyebrow">Waarom het telt</span><h2>Elke rebound is een nieuwe kans</h2><p>Een gemist schot is pas verloren als '
         'de verdediging de bal pakt. Elke rebound die jij wint, is een nieuwe aanval voor je vak.</p></div>'
         '<div><span class="eyebrow">Je maatje</span><h2>De Wolf</h2><p>Rond de korf spelen de wolf en de beer met elkaar. '
         'Samen zoeken jullie de beste aangeefpositie, en soms speelt de wolf jou vrij. '
         '<a href="wolf.html">Lees het profiel van de Wolf</a>.</p></div>'),
    check=["Ik sta graag onder de korf, ook als het druk is.", "Ik zie vroeg waar een schot gaat vallen.",
           "Ik laat me niet makkelijk wegduwen.", "Ik scoor graag van dichtbij.",
           "Een rebound winnen voelt voor mij als een doelpunt.", "Ik kan mijn verdediger uitblokken en tegelijk de bal volgen.",
           "Ik coach mijn vakgenoten.", "Ik geef nooit op, ook niet bij een achterstand."],
    verdicts=("Je kracht zit waarschijnlijk ergens anders. Kijk ook eens bij de Tijger, de Panter of de Wolf.",
              "Er zit een beer in je. Train je uitblokken en je timing, en kijk wat er gebeurt.",
              "Beer-alarm. Vraag je trainer eens of deze rol bij je past."),
    sources=[("Profiel van de topspeler in de rol van Beer", "https://korfballadvisor.blogspot.com/2009/10/profiel-van-de-topspeler-in-de-rol-van.html", "2009"),
             ("Profile of the Top Player: Bear", "https://korfballadvisor.blogspot.com/2009/10/profile-of-top-player-bear.html", "2009")],
)

if __name__ == "__main__":
    for key, fname, _ in ORDER:
        (OUT / fname).write_text(page(key, ROLES[key]), encoding="utf-8")
        print("geschreven:", fname)
