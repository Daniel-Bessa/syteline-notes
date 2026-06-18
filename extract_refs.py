#!/usr/bin/env python3
import sys, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'c:\Users\iceco\Desktop\Syteline\_extracted_02.txt', encoding='utf-8') as f:
    raw = f.read()

# Split into "paragraphs" (blocks separated by 2+ newlines)
paras = [p.strip() for p in re.split(r'\n{2,}', raw) if len(p.strip()) > 60]

def find_best(terms, min_score=2):
    """Return the paragraph that matches the most of the given terms."""
    best, best_score = '', 0
    for p in paras:
        pl = p.lower()
        score = sum(1 for t in terms if t.lower() in pl)
        if score > best_score:
            best_score, best = score, p
    if best_score >= min_score:
        # clean up special chars and whitespace
        best = re.sub(r'[•●]', '•', best)
        best = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', best)
        best = re.sub(r'\s+', ' ', best).strip()
        # trim to ~300 chars, at a sentence boundary
        if len(best) > 320:
            cut = best[:320]
            last = max(cut.rfind('.'), cut.rfind('!'), cut.rfind('?'))
            if last > 100: best = cut[:last+1]
        return best
    return ''

QUERIES = [
    # Q1
    ['Explorer', 'hierarchical view', 'forms', 'folders'],
    # Q2
    ['Master Explorer', 'Modules', 'Roles', 'All Forms'],
    # Q3
    ['Select Form', 'dialog', 'Ctrl', 'Open', 'toolbar'],
    # Q4
    ['AutoRun', 'PreLoad', 'do not rename', 'subfolders'],
    # Q5
    ['AutoRun', 'automatically', 'log in', 'opens'],
    # Q6
    ['presentation layer', 'middleware', 'database', 'three layers'],
    # Q7
    ['filter-in-place', 'temporary', 'save', 'criteria'],
    # Q8
    ['filter-in-place', 'operators', 'NULL', 'wildcard'],
    # Q9
    ['data cap', '200', 'Get More Rows'],
    # Q10
    ['query clause', 'field name', 'operator', 'value'],
    # Q11
    ['save', 'query', 'saved filter', 'reuse'],
    # Q12
    ['LIKE', 'query form', 'operators', 'filter'],
    # Q13
    ['grid', 'column', 'resize', 'hide', 'Edit Grid'],
    # Q14
    ['Sort dialog', 'Collection', 'By Property', 'Descending'],
    # Q15 — Q14 in file index
    ['red asterisk', 'required', 'new record'],
    # Q16
    ['green asterisk', 'system', 'generate', 'auto'],
    # Q17
    ['gray field', 'no border', 'read-only'],
    # Q18
    ['drop-down', 'Find', 'Add', 'filter'],
    # Q19
    ['business data', 'option list', 'Find', 'Add'],
    # Q20
    ['Actions > Copy', 'copy', 'existing record'],
    # Q21
    ['undo', 'Ctrl+F5', 'F5', 'refresh', 'cancel changes'],
    # Q22
    ['Object Notes', 'Attach', 'reusable', 'System/User Notes'],
    # Q23
    ['Background Task', 'Task Succeeded', 'Task Failed', 'Return Status'],
    # Q24
    ['Export Collection', 'comma', 'tab', 'separated'],
    # Q25
    ['Smart Client', 'copy', 'paste', 'Excel', 'rows', 'columns'],
    # Q26 — Course Review starts
    ['form', 'window', 'interact', 'database', 'record', 'field', 'collection'],
    # Q27
    ['collection', 'group', 'related records'],
    # Q28
    ['Grid view', 'Detail view', 'Dual view', 'rows', 'columns'],
    # Q29
    ['linking button', 'related form', 'right-click', 'Details'],
    # Q30
    ['Filter In Place', 'filter mode', 'search criteria', 'toolbar'],
    # Q31
    ['My Folders', 'customize', 'subfolder', 'shortcut'],
    # Q32
    ['query form', 'Ctrl+Q', 'By Query', 'Actions > Filter'],
    # Q33
    ['new record', 'Ctrl+N', 'Actions > New', 'Refresh mode'],
    # Q34
    ['save', 'Ctrl+S', 'Save Current', 'collection'],
    # Q35
    ['validation', 'error', 'navigate away', 'save', 'Validate'],
    # Q36
    ['red X', 'marked', 'deletion', 'not saved'],
    # Q37
    ['Object Notes', 'current record', 'once', 'Class Notes'],
    # Q38
    ['report', 'parameters', 'range filters', 'Preview', 'Print'],
    # Q39
    ['Preview', 'Commit', 'process', 'trial', 'update database'],
    # Q40
    ['Actions > To Excel', 'export', 'collection', 'spreadsheet', 'automatically'],
]

for i, terms in enumerate(QUERIES, 1):
    ref = find_best(terms)
    # escape for JS string
    ref_js = ref.replace('\\','\\\\').replace("'","\\'").replace('\n',' ')
    print(f"  // Q{i}: {terms[0]}")
    print(f"  ref: '{ref_js}',")
    print()
