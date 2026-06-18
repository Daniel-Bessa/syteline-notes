#!/usr/bin/env python3
"""
Extract exercises from workbook text files and generate HTML exercise trackers.
Run after running: python -m pdfminer.high_level extract ... (already done via earlier script)
"""
import re, json, os, textwrap

# ── Helper: parse a block of text into parts+steps ───────────────────────────
STEP_RE  = re.compile(r'^\s{0,6}(\d{1,2})\.\s{1,6}(.+)')
PART_RE  = re.compile(r'^\s{0,4}Part\s+(\d+|[A-Z])[\s:\–\-]+(.+)', re.IGNORECASE)
NOTE_RE  = re.compile(r'^\s{0,4}Note[s]?:\s*(.+)', re.IGNORECASE)
COPYRIGHT_RE = re.compile(r'© 20\d\d Infor|v10 (Navigating|Creating|Extending|Using|CloudSuite)')
PAGE_RE  = re.compile(r'^\s*\d+\s*$')

def clean(s):
    s = s.replace('–', '-').replace('—', '-').replace('’', "'")
    s = s.replace('“', '"').replace('”', '"').replace(' ', ' ')
    return ' '.join(s.split())

def parse_exercise_block(lines):
    """Given lines of an exercise, return list of {title, steps} parts."""
    parts = []
    cur_part = {'title': 'Steps', 'steps': []}
    cur_step = None
    step_continuation = False

    for raw in lines:
        line = raw.rstrip()
        if not line.strip():
            step_continuation = False
            continue
        if COPYRIGHT_RE.search(line) or PAGE_RE.match(line):
            continue

        pm = PART_RE.match(line)
        sm = STEP_RE.match(line)
        nm = NOTE_RE.match(line)

        if pm:
            if cur_step:
                cur_part['steps'].append(cur_step)
                cur_step = None
            if cur_part['steps']:
                parts.append(cur_part)
            cur_part = {'title': f"Part {pm.group(1)} – {clean(pm.group(2))}", 'steps': []}
            step_continuation = False
        elif sm:
            if cur_step:
                cur_part['steps'].append(cur_step)
            cur_step = {'text': clean(sm.group(2)), 'note': ''}
            step_continuation = True
        elif nm and cur_step:
            cur_step['note'] = clean(nm.group(1))
            step_continuation = False
        elif cur_step and step_continuation:
            stripped = line.strip()
            if stripped and not stripped.startswith('©') and not PAGE_RE.match(stripped):
                cur_step['text'] += ' ' + clean(stripped)
        else:
            step_continuation = False

    if cur_step:
        cur_part['steps'].append(cur_step)
    if cur_part['steps']:
        parts.append(cur_part)

    return parts

EX_HEAD_RE = re.compile(r'^\s{0,4}Exercise\s+(\d+\.\d+[a-z]?)[\s:\–]+(.+)', re.IGNORECASE)
GOAL_STOP  = re.compile(r'Exercise steps|Part\s+\d|^\s{0,4}\d+\.\s{1,6}', re.IGNORECASE)

def extract_exercises(txt_path):
    with open(txt_path, encoding='utf-8') as f:
        lines = f.readlines()

    exercises = []
    i = 0
    while i < len(lines):
        m = EX_HEAD_RE.match(lines[i])
        if m:
            ex_id    = m.group(1).strip()
            ex_title = clean(m.group(2))
            # collect goal lines (until "Exercise steps", "Part N", first numbered step, or next Exercise)
            goal_lines = []
            j = i + 1
            while j < len(lines):
                line = lines[j].rstrip()
                if EX_HEAD_RE.match(line):
                    break
                if GOAL_STOP.search(line):
                    break
                stripped = line.strip()
                if stripped and not stripped.startswith('Notes') and \
                   not stripped.startswith('If you') and \
                   not COPYRIGHT_RE.search(stripped) and not PAGE_RE.match(stripped):
                    goal_lines.append(clean(stripped))
                j += 1
            goal = ' '.join(goal_lines[:3])   # at most 3 sentences

            # collect step lines until next Exercise heading (or end of file)
            step_lines = []
            k = j
            while k < len(lines):
                if EX_HEAD_RE.match(lines[k]):
                    break
                step_lines.append(lines[k])
                k += 1

            parts = parse_exercise_block(step_lines)
            if parts:
                exercises.append({'id': ex_id, 'title': ex_title, 'goal': goal, 'parts': parts})
            i = k
        else:
            i += 1

    return exercises

# ── HTML template ─────────────────────────────────────────────────────────────
def js_escape(s):
    return s.replace('\\','\\\\').replace('`','\\`').replace('$','\\$')

def build_html(title, subtitle, lessons_data, filename):
    """
    lessons_data: list of {id, label, title, exercises: [{id,title,goal,parts:[{title,steps:[{text,note}]}]}]}
    """
    key = filename.replace('.html','')
    lessons_js = json.dumps(lessons_data, ensure_ascii=False, indent=2)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Exercises — {title}</title>
  <style>
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
         background:#1a1a1a;color:#e2e8f0;min-height:100vh}}
    .hdr{{background:#0f172a;padding:18px 28px;display:flex;align-items:center;gap:14px;
          border-bottom:1px solid #1e293b;position:sticky;top:0;z-index:10}}
    .hdr-icon{{font-size:28px}}
    .hdr-title{{font-size:18px;font-weight:700;color:#f1f5f9}}
    .hdr-sub{{font-size:12px;color:#64748b;margin-top:2px}}
    .hdr-right{{margin-left:auto;text-align:right}}
    .hdr-home{{color:#60a5fa;text-decoration:none;font-size:13px}}
    .hdr-home:hover{{text-decoration:underline}}
    .prog-wrap{{background:#0f172a;padding:10px 28px;border-bottom:1px solid #1e293b}}
    .prog-label{{font-size:12px;color:#94a3b8;margin-bottom:6px;display:flex;justify-content:space-between}}
    .prog-bar{{height:6px;background:#1e293b;border-radius:3px;overflow:hidden}}
    .prog-fill{{height:100%;background:linear-gradient(90deg,#3b82f6,#60a5fa);border-radius:3px;
               transition:width .4s ease}}
    .page{{max-width:860px;margin:0 auto;padding:28px 20px 60px}}
    .lesson{{margin-bottom:8px}}
    .lesson-btn{{width:100%;text-align:left;background:#2d2d2d;border:none;border-radius:10px;
                padding:14px 18px;cursor:pointer;display:flex;align-items:center;gap:12px;
                color:#e2e8f0;font-size:15px;font-weight:600;transition:background .15s}}
    .lesson-btn:hover{{background:#374151}}
    .lesson-btn .l-badge{{background:#1e3a5f;color:#60a5fa;font-size:11px;font-weight:700;
                          padding:2px 8px;border-radius:10px}}
    .lesson-btn .l-check{{margin-left:auto;font-size:12px;color:#64748b}}
    .lesson-btn .l-caret{{color:#64748b;font-size:12px;transition:transform .2s}}
    .lesson-btn.open .l-caret{{transform:rotate(90deg)}}
    .lesson-body{{display:none;padding:6px 0 10px}}
    .lesson-body.open{{display:block}}
    .ex-card{{background:#242424;border-radius:10px;margin-bottom:10px;
              border:1px solid #2d2d2d;overflow:hidden}}
    .ex-head{{padding:14px 18px;cursor:pointer;display:flex;align-items:flex-start;gap:12px}}
    .ex-head:hover{{background:#2d2d2d}}
    .ex-num{{background:#1e3a5f;color:#60a5fa;font-size:11px;font-weight:700;
             padding:3px 9px;border-radius:8px;white-space:nowrap;flex-shrink:0;margin-top:2px}}
    .ex-title{{font-size:14px;font-weight:600;color:#f1f5f9;flex:1}}
    .ex-meta{{font-size:12px;color:#64748b;margin-top:3px}}
    .ex-progress{{margin-left:auto;flex-shrink:0;text-align:right}}
    .ex-pct{{font-size:12px;font-weight:700;color:#60a5fa}}
    .ex-done-badge{{font-size:11px;color:#86efac;display:none}}
    .ex-head.done .ex-pct{{display:none}}
    .ex-head.done .ex-done-badge{{display:block}}
    .ex-body{{display:none;padding:0 18px 18px;border-top:1px solid #2d2d2d}}
    .ex-body.open{{display:block}}
    .ex-goal{{background:#1e293b;border-left:3px solid #0284c7;color:#7dd3fc;
              padding:10px 14px;border-radius:0 6px 6px 0;font-size:13px;line-height:1.6;
              margin:14px 0 16px}}
    .part-title{{font-size:12px;font-weight:700;color:#94a3b8;text-transform:uppercase;
                letter-spacing:.06em;margin:16px 0 8px}}
    .step-list{{list-style:none;display:flex;flex-direction:column;gap:6px}}
    .step-item{{display:flex;align-items:flex-start;gap:10px;cursor:pointer;
               padding:8px 10px;border-radius:7px;transition:background .12s}}
    .step-item:hover{{background:#2d2d2d}}
    .step-cb{{width:18px;height:18px;border:2px solid #374151;border-radius:4px;
              flex-shrink:0;margin-top:1px;display:flex;align-items:center;justify-content:center;
              transition:all .15s;cursor:pointer}}
    .step-item.checked .step-cb{{background:#16a34a;border-color:#16a34a}}
    .step-item.checked .step-cb::after{{content:'✓';color:#fff;font-size:11px;font-weight:700}}
    .step-text{{font-size:13px;color:#cbd5e1;line-height:1.55;flex:1}}
    .step-item.checked .step-text{{color:#4b5563;text-decoration:line-through}}
    .step-note{{font-size:11.5px;color:#475569;font-style:italic;margin-top:3px;display:block}}
    .ex-controls{{display:flex;gap:8px;margin-top:16px;padding-top:14px;border-top:1px solid #2d2d2d}}
    .btn{{padding:7px 14px;border-radius:7px;border:none;cursor:pointer;font-size:12px;
          font-weight:600;transition:background .15s}}
    .btn-reset{{background:#374151;color:#94a3b8}}
    .btn-reset:hover{{background:#4b5563}}
    .btn-all{{background:#1e3a5f;color:#60a5fa}}
    .btn-all:hover{{background:#1d4ed8;color:#fff}}
  </style>
</head>
<body>
<div class="hdr">
  <span class="hdr-icon">🛠️</span>
  <div>
    <div class="hdr-title">{title}</div>
    <div class="hdr-sub">{subtitle}</div>
  </div>
  <div class="hdr-right"><a href="../index.html" class="hdr-home">← Back to hub</a></div>
</div>
<div class="prog-wrap">
  <div class="prog-label">
    <span>Overall progress</span>
    <span id="prog-text">0 / 0 steps complete</span>
  </div>
  <div class="prog-bar"><div class="prog-fill" id="prog-fill" style="width:0%"></div></div>
</div>
<div class="page" id="page"></div>
<script>
const KEY = '{key}';
const LESSONS = {lessons_js};

function loadState(){{try{{return JSON.parse(localStorage.getItem(KEY)||'{{}}')}}catch(e){{return{{}}}}}}
function saveState(s){{localStorage.setItem(KEY,JSON.stringify(s))}}
let state = loadState();

function allStepIds(){{
  const ids=[];
  LESSONS.forEach(l=>l.exercises.forEach(ex=>{{
    ex.parts.forEach((pt,pi)=>pt.steps.forEach((_,si)=>ids.push(`${{ex.id}}-p${{pi}}-s${{si}}`)));
  }}));
  return ids;
}}
function updateProgress(){{
  const ids=allStepIds();
  const done=ids.filter(id=>state[id]).length;
  const pct=ids.length?Math.round((done/ids.length)*100):0;
  document.getElementById('prog-fill').style.width=pct+'%';
  document.getElementById('prog-text').textContent=`${{done}} / ${{ids.length}} steps complete`;
}}
function countEx(ex){{
  let t=0,d=0;
  ex.parts.forEach((pt,pi)=>pt.steps.forEach((_,si)=>{{t++;if(state[`${{ex.id}}-p${{pi}}-s${{si}}`])d++;}}));
  return{{t,d}};
}}
function updateExHead(exId){{
  const head=document.querySelector(`.ex-head[data-ex="${{exId}}"]`);
  if(!head)return;
  const ex=LESSONS.flatMap(l=>l.exercises).find(e=>e.id===exId);
  const{{t,d}}=countEx(ex);
  const pct=t?Math.round((d/t)*100):0;
  head.querySelector('.ex-pct').textContent=pct+'%';
  if(d===t&&t>0)head.classList.add('done');else head.classList.remove('done');
}}
function updateLessonHead(lid){{
  const lesson=LESSONS.find(l=>l.id===lid);
  const btn=document.querySelector(`.lesson-btn[data-lesson="${{lid}}"]`);
  if(!btn||!lesson)return;
  let t=0,d=0;
  lesson.exercises.forEach(ex=>{{const c=countEx(ex);t+=c.t;d+=c.d;}});
  btn.querySelector('.l-check').textContent=`${{d}}/${{t}}`;
}}
function render(){{
  const page=document.getElementById('page');
  page.innerHTML='';
  LESSONS.forEach(lesson=>{{
    const lDiv=document.createElement('div');
    lDiv.className='lesson';
    const btn=document.createElement('button');
    btn.className='lesson-btn open';
    btn.dataset.lesson=lesson.id;
    btn.innerHTML=`<span class="l-badge">${{lesson.label}}</span><span>${{lesson.title}}</span><span class="l-check"></span><span class="l-caret">▶</span>`;
    const body=document.createElement('div');
    body.className='lesson-body open';
    btn.addEventListener('click',()=>{{btn.classList.toggle('open');body.classList.toggle('open');}});
    lesson.exercises.forEach(ex=>{{
      const card=document.createElement('div');card.className='ex-card';
      const head=document.createElement('div');head.className='ex-head';head.dataset.ex=ex.id;
      const stepCount=ex.parts.reduce((a,p)=>a+p.steps.length,0);
      head.innerHTML=`<span class="ex-num">Ex ${{ex.id}}</span><div><div class="ex-title">${{ex.title}}</div><div class="ex-meta">${{stepCount}} steps</div></div><div class="ex-progress"><div class="ex-pct">0%</div><div class="ex-done-badge">✓ Done</div></div>`;
      const exBody=document.createElement('div');exBody.className='ex-body open';
      if(ex.goal){{const g=document.createElement('div');g.className='ex-goal';g.textContent=ex.goal;exBody.appendChild(g);}}
      ex.parts.forEach((part,pi)=>{{
        if(part.title!=='Steps'){{const pt=document.createElement('div');pt.className='part-title';pt.textContent=part.title;exBody.appendChild(pt);}}
        const ul=document.createElement('ul');ul.className='step-list';
        part.steps.forEach((step,si)=>{{
          const id=`${{ex.id}}-p${{pi}}-s${{si}}`;
          const li=document.createElement('li');li.className='step-item'+(state[id]?' checked':'');
          const cb=document.createElement('div');cb.className='step-cb';
          const txt=document.createElement('div');txt.className='step-text';
          txt.innerHTML=step.text;
          if(step.note)txt.innerHTML+=`<span class="step-note">${{step.note}}</span>`;
          li.appendChild(cb);li.appendChild(txt);
          li.addEventListener('click',()=>{{
            state[id]=!state[id];saveState(state);
            li.classList.toggle('checked',state[id]);
            updateExHead(ex.id);updateLessonHead(lesson.id);updateProgress();
          }});
          ul.appendChild(li);
        }});
        exBody.appendChild(ul);
      }});
      const ctrl=document.createElement('div');ctrl.className='ex-controls';
      const rb=document.createElement('button');rb.className='btn btn-reset';rb.textContent='Reset';
      rb.addEventListener('click',e=>{{e.stopPropagation();
        ex.parts.forEach((pt,pi)=>pt.steps.forEach((_,si)=>{{delete state[`${{ex.id}}-p${{pi}}-s${{si}}`];}}));
        saveState(state);
        exBody.querySelectorAll('.step-item').forEach(li=>li.classList.remove('checked'));
        updateExHead(ex.id);updateLessonHead(lesson.id);updateProgress();
      }});
      const ab=document.createElement('button');ab.className='btn btn-all';ab.textContent='Mark all done';
      ab.addEventListener('click',e=>{{e.stopPropagation();
        ex.parts.forEach((pt,pi)=>pt.steps.forEach((_,si)=>{{state[`${{ex.id}}-p${{pi}}-s${{si}}`]=true;}}));
        saveState(state);
        exBody.querySelectorAll('.step-item').forEach(li=>li.classList.add('checked'));
        updateExHead(ex.id);updateLessonHead(lesson.id);updateProgress();
      }});
      ctrl.appendChild(rb);ctrl.appendChild(ab);exBody.appendChild(ctrl);
      head.addEventListener('click',()=>exBody.classList.toggle('open'));
      card.appendChild(head);card.appendChild(exBody);body.appendChild(card);
    }});
    lDiv.appendChild(btn);lDiv.appendChild(body);page.appendChild(lDiv);
    lesson.exercises.forEach(ex=>updateExHead(ex.id));
    updateLessonHead(lesson.id);
  }});
  updateProgress();
}}
render();
</script>
</body>
</html>"""
    return html

# ── Workbook configs ───────────────────────────────────────────────────────────
WORKBOOKS = [
    {
        'txt':      r'c:\Users\iceco\Desktop\Syteline\_extracted_03.txt',
        'out':      r'c:\Users\iceco\Desktop\Syteline\exercises\ex-03-form-personalizations.html',
        'title':    '03 — Form Personalizations Exercises',
        'subtitle': 'CSI v10 · Creating Form Personalizations · Hands-on lab exercises',
        'key':      'ex-03-form',
        'lessons': [
            {'id':'L2','label':'Lesson 2','title':'Setting Up for Development',   'ex_ids':['2.1']},
            {'id':'L3','label':'Lesson 3','title':'Setting the Form Appearance',  'ex_ids':['3.1','3.2','3.3']},
            {'id':'L4','label':'Lesson 4','title':'Adding Components to a Form',  'ex_ids':['4.1']},
            {'id':'L5','label':'Lesson 5','title':'Working with Inherited Attributes','ex_ids':['5.1']},
            {'id':'L6','label':'Lesson 6','title':'Creating List Sources',        'ex_ids':['6.1']},
            {'id':'L7','label':'Lesson 7','title':'Creating Validators',          'ex_ids':['7.1']},
            {'id':'L8','label':'Lesson 8','title':'Creating Strings',             'ex_ids':['8.1']},
            {'id':'L9','label':'Lesson 9','title':'Working with UET Fields',      'ex_ids':['9.1','9.2']},
            {'id':'L10','label':'Lesson 10','title':'Adding Event Handlers',      'ex_ids':['10.1']},
            {'id':'L11','label':'Lesson 11','title':'Using FormSync',             'ex_ids':['11.1']},
        ]
    },
    {
        'txt':      r'c:\Users\iceco\Desktop\Syteline\_extracted_04.txt',
        'out':      r'c:\Users\iceco\Desktop\Syteline\exercises\ex-04-extending-mongoose.html',
        'title':    '04 — Extending the Application Exercises',
        'subtitle': 'CSI v10 · Extending with Mongoose · Hands-on lab exercises',
        'key':      'ex-04-mongoose',
        'lessons': [
            {'id':'L2','label':'Lesson 2','title':'Setting Up the Development Environment','ex_ids':['2.1','2.2','2.3']},
            {'id':'L3','label':'Lesson 3','title':'Exploring the Mongoose Architecture',   'ex_ids':['3.1']},
            {'id':'L4','label':'Lesson 4','title':'Creating New Data Maintenance',         'ex_ids':['4.1','4.2','4.3','4.4','4.5','4.6','4.7']},
            {'id':'L5','label':'Lesson 5','title':'Extending Existing Forms and IDOs',     'ex_ids':['5.1','5.2']},
            {'id':'L6','label':'Lesson 6','title':'Building the Expense Reports Form',     'ex_ids':['6.1','6.2','6.3']},
            {'id':'L7','label':'Lesson 7','title':'Building the Portal Form',              'ex_ids':['7.1','7.2','7.3','7.4','7.5','7.6']},
            {'id':'L8','label':'Lesson 8','title':'Security and Check-In',                 'ex_ids':['8.1','8.2']},
        ]
    },
    {
        'txt':      r'c:\Users\iceco\Desktop\Syteline\_extracted_05.txt',
        'out':      r'c:\Users\iceco\Desktop\Syteline\exercises\ex-05-creating-reports.html',
        'title':    '05 — Creating Reports Exercises',
        'subtitle': 'CSI v10 · Creating Reports Using Mongoose · Hands-on lab exercises',
        'key':      'ex-05-reports',
        'lessons': [
            {'id':'L1','label':'Lesson 1','title':'DataView Reports',           'ex_ids':['1.1']},
            {'id':'L2','label':'Lesson 2','title':'Simple Report Type Forms',   'ex_ids':['2.1']},
            {'id':'L3','label':'Lesson 3','title':'FlexLayout Components',      'ex_ids':['3.1']},
            {'id':'L4','label':'Lesson 4','title':'Adding Report Components',   'ex_ids':['4.1']},
            {'id':'L5','label':'Lesson 5','title':'Stored Procedure Reports',   'ex_ids':['5.1']},
            {'id':'L6','label':'Lesson 6','title':'Sub-Reports',                'ex_ids':['6.1']},
            {'id':'L7','label':'Lesson 7','title':'Report Criteria Forms',      'ex_ids':['7.1','7.2']},
            {'id':'L8','label':'Lesson 8','title':'Advanced Report Criteria',   'ex_ids':['8.1','8.2']},
        ]
    },
    {
        'txt':      r'c:\Users\iceco\Desktop\Syteline\_extracted_aes.txt',
        'out':      r'c:\Users\iceco\Desktop\Syteline\exercises\ex-aes.html',
        'title':    'AES — Application Event System Exercises',
        'subtitle': 'CSI v10 · Using the Application Event System · Hands-on lab exercises',
        'key':      'ex-aes',
        'lessons': [
            {'id':'L3','label':'Lesson 3','title':'Creating Notification Events',      'ex_ids':['3.1','3.2','3.3','3.4']},
            {'id':'L4','label':'Lesson 4','title':'Using the New Workflow Wizard',     'ex_ids':['4.1','4.2','4.3']},
            {'id':'L7','label':'Lesson 7','title':'Approval Workflows',                'ex_ids':['7.1']},
            {'id':'L8','label':'Lesson 8','title':'Prompting for Information',         'ex_ids':['8.1']},
            {'id':'L9','label':'Lesson 9','title':'Multi-Level Approvals',             'ex_ids':['9.1']},
            {'id':'L10','label':'Lesson 10','title':'Calling Events from Forms',       'ex_ids':['10.1']},
        ]
    },
]

# ── Main ──────────────────────────────────────────────────────────────────────
for wb in WORKBOOKS:
    print(f"\nProcessing {wb['out']} ...")
    exercises_by_id = {ex['id']: ex for ex in extract_exercises(wb['txt'])}
    print(f"  Found exercise IDs: {sorted(exercises_by_id.keys())}")

    lessons_data = []
    for lesson_cfg in wb['lessons']:
        exs = []
        for eid in lesson_cfg['ex_ids']:
            if eid in exercises_by_id:
                exs.append(exercises_by_id[eid])
            else:
                print(f"  WARNING: Exercise {eid} not found")
        if exs:
            lessons_data.append({
                'id':        lesson_cfg['id'],
                'label':     lesson_cfg['label'],
                'title':     lesson_cfg['title'],
                'exercises': exs,
            })

    html = build_html(wb['title'], wb['subtitle'], lessons_data, os.path.basename(wb['out']))
    os.makedirs(os.path.dirname(wb['out']), exist_ok=True)
    with open(wb['out'], 'w', encoding='utf-8') as f:
        f.write(html)
    total_steps = sum(
        sum(len(pt['steps']) for pt in ex['parts'])
        for ld in lessons_data for ex in ld['exercises']
    )
    total_ex = sum(len(ld['exercises']) for ld in lessons_data)
    print(f"  Written: {total_ex} exercises, {total_steps} steps")

print("\nAll done.")
