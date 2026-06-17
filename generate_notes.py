#!/usr/bin/env python3
"""Generate CSI/SyteLine study-notes PDFs for folders 04, 05, AES, and a Master index."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib import colors

DARK   = HexColor('#222222')
MID    = HexColor('#555555')
LGRAY  = HexColor('#f6f6f6')
BORDER = HexColor('#d8d8d8')
GREEN  = HexColor('#006600')
WHITE  = HexColor('#ffffff')
W = 6.5 * inch

_ss = getSampleStyleSheet()
S = {
    'T' : ParagraphStyle('T',  parent=_ss['Normal'], fontSize=24, fontName='Helvetica-Bold',  textColor=DARK, spaceAfter=4),
    'ST': ParagraphStyle('ST', parent=_ss['Normal'], fontSize=11, fontName='Helvetica',        textColor=MID,  spaceAfter=10),
    'H1': ParagraphStyle('H1', parent=_ss['Normal'], fontSize=16, fontName='Helvetica-Bold',   textColor=DARK, spaceBefore=16, spaceAfter=6),
    'H2': ParagraphStyle('H2', parent=_ss['Normal'], fontSize=12, fontName='Helvetica-Bold',   textColor=MID,  spaceBefore=10, spaceAfter=4),
    'B' : ParagraphStyle('B',  parent=_ss['Normal'], fontSize=10, fontName='Helvetica',        textColor=DARK, spaceAfter=7, leading=15),
    'BL': ParagraphStyle('BL', parent=_ss['Normal'], fontSize=10, fontName='Helvetica',        textColor=DARK, spaceAfter=4, leading=14, leftIndent=18, firstLineIndent=-10),
    'C' : ParagraphStyle('C',  parent=_ss['Normal'], fontSize=9,  fontName='Courier',          textColor=GREEN,spaceAfter=3, leading=13, leftIndent=20),
    'TH': ParagraphStyle('TH', parent=_ss['Normal'], fontSize=9.5,fontName='Helvetica-Bold',   textColor=DARK),
    'TB': ParagraphStyle('TB', parent=_ss['Normal'], fontSize=9,  fontName='Helvetica',        textColor=DARK, leading=13),
}

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=10, spaceBefore=4)
def sp(n=8):  return Spacer(1, n)
def p(t, s='B'): return Paragraph(t, S[s])
def h1(t):   return Paragraph(t, S['H1'])
def h2(t):   return Paragraph(t, S['H2'])
def bl(t):   return Paragraph('– ' + t, S['BL'])

def tbl(headers, rows, widths=None):
    if widths is None:
        widths = [2.0*inch, W-2.0*inch]
    data = [[Paragraph(h, S['TH']) for h in headers]]
    for row in rows:
        data.append([Paragraph(str(c), S['TB']) for c in row])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,0), LGRAY),
        ('GRID',       (0,0),(-1,-1), 0.4, BORDER),
        ('TOPPADDING', (0,0),(-1,-1), 5),
        ('BOTTOMPADDING',(0,0),(-1,-1), 5),
        ('LEFTPADDING', (0,0),(-1,-1), 7),
        ('RIGHTPADDING',(0,0),(-1,-1), 7),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,LGRAY]),
        ('VALIGN',     (0,0),(-1,-1),'TOP'),
    ]))
    return t

def build(path, elements):
    doc = SimpleDocTemplate(path, pagesize=letter,
                            rightMargin=0.75*inch, leftMargin=0.75*inch,
                            topMargin=0.75*inch, bottomMargin=0.75*inch)
    doc.build(elements)
    print(f"Created: {path}")


# ───────────────────────────────────────────────────────────────
# PDF 1 — Extending the Application with Mongoose (Folder 04)
# ───────────────────────────────────────────────────────────────
def pdf_extending():
    e = []
    e += [p("CSI v10 — Extending the Application with Mongoose", 'T'),
          p("Study notes from the Infor official training workbook (214 pages)", 'ST'), hr()]

    e += [h1("Why this guide matters"),
          p("This is the primary <b>developer course</b> — the step beyond personalizing forms. "
            "It teaches how to extend CSI at the data layer: creating new database tables, IDOs, "
            "and forms from scratch; extending existing IDOs and forms; building portal-facing "
            "screens; and working safely in a multi-developer environment. "
            "If you need to add a field that doesn't exist anywhere in the application, or build "
            "a brand-new business process, this is the knowledge you need."),
          p("Prerequisites: UI Navigation and Creating Form Personalizations. "
            "Those courses cover the client tier. This course works primarily at the IDO (middle) tier."),
          hr()]

    e += [h1("1. The Mongoose Three-Tier Architecture"),
          p("All CSI development happens inside the Mongoose framework's three tiers. Knowing "
            "which tier owns which concern is essential before writing a line of customization code."),
          tbl(["Tier", "What lives here / what happens"],
              [["1 — Client (WinStudio Smart Client or Web Client)",
                "Forms, components, form-level event handlers. WinStudio metadata (form definitions) "
                "is stored in a Forms database and loaded at runtime. Smart Client and Web Client "
                "render the same metadata differently."],
               ["2 — Middle Tier (IDO Runtime Service)",
                "IDO business objects, property classes, IDO methods, custom C# extension "
                "class DLLs. The IDORuntimeHost.exe process runs here. Every client request "
                "(load, save, invoke) is handled by this tier before touching the database."],
               ["3 — Database (SQL Server)",
                "Application data tables, stored procedures, views. Also stores: IDO metadata, "
                "form metadata, Application Event System tables, report definitions. "
                "Custom stored procedures and triggers live here."]],
              [2.2*inch, W-2.2*inch]),
          sp(),
          p("<b>Important mental model:</b> A form Save calls UpdateCollection on the IDO Runtime "
            "(tier 2), which executes SQL on tier 3. Custom C# extension class logic runs on "
            "tier 2 — between the client request and the SQL execution."),
          hr()]

    e += [h1("2. Development Permission Levels — All Five"),
          p("Editing permission is set per-user on the Users form. "
            "Check yours: <b>Help &gt; About &lt;servername&gt;</b>."),
          tbl(["Level", "What they can do"],
              [["Vendor Developer (value 4, set manually — hidden from dropdown)",
                "Bypasses all customizations; sees pure vendor defaults. Use this to diagnose "
                "whether a bug is in the base product or a customization. Never make real "
                "development changes here."],
               ["Site Developer",
                "Full development power: create/delete forms and IDOs at any scope "
                "(Vendor/Site/Group/User), impersonate any user/group to view their version, "
                "manage all global objects. This is your day-to-day developer level."],
               ["Full User",
                "Can fully customize forms at their own User scope only. "
                "Cannot create or delete forms, and cannot affect other users."],
               ["Basic User",
                "Simple user-scope changes only: hide fields, set read-only, change colors "
                "and fonts, rearrange components. Cannot create or delete forms."],
               ["None",
                "Cannot enter Design Mode at all. The design mode icon is disabled. "
                "Default for standard end users."]],
              [2.0*inch, W-2.0*inch]),
          sp(),
          p("<b>Entering Design Mode:</b> Clear the filter-in-place first, then press "
            "<b>Ctrl+E</b> or click the Design Mode icon. A Site Developer will see a scope "
            "dialog — always verify you have the correct scope (Vendor / Site Default / Group / "
            "User) before saving anything."),
          hr()]

    e += [h1("3. IDOs (Intelligent Data Objects) — The Core Building Block"),
          p("An IDO is a named business object on the middle tier that encapsulates a set of "
            "database columns, exposes them as named properties to the client, and defines the "
            "methods (business logic) for interacting with those columns. Every WinStudio form "
            "collection is bound to exactly one IDO."),
          h2("IDO anatomy"),
          tbl(["Element", "What it is"],
              [["Table References",
                "One or more SQL tables or views the IDO reads and writes. The IDO maps "
                "columns to named properties."],
               ["Property Definitions",
                "Named columns/calculated values exposed to the client. Key attributes per "
                "property: Name, Data type, Length, Required/Optional, Key flag (marks "
                "primary key columns), Read-only, Calc (derived/not stored)."],
               ["Property Classes",
                "Reusable attribute templates. If 15 IDOs all have a 'Status' field with the "
                "same type and behavior, they all inherit from one Property Class — change "
                "the class and all IDOs update automatically."],
               ["IDO Methods",
                "Custom stored procedures or C# methods attached to the IDO. "
                "Types: Fetch (returns rows), Non-fetch (writes without returning rows), "
                "GetProperty, SetProperty. Invoked via the Invoke() built-in method."],
               ["IDO Extension Class",
                "Optional C# DLL that overrides LoadCollection, UpdateCollection, or Invoke "
                "at the middle tier. Required for complex cross-IDO validation, external "
                "integrations, or logic that cannot live in a stored procedure."]],
              [1.9*inch, W-1.9*inch]),
          sp(),
          h2("Standard built-in methods — every IDO has these four"),
          bl("<b>LoadCollection</b> — retrieves rows matching a filter; returns them to the client."),
          bl("<b>UpdateCollection</b> — handles insert, update, and delete for a batch of rows."),
          bl("<b>GetPropertyInfo</b> — returns property metadata (types, lengths, required) to the form."),
          bl("<b>Invoke</b> — calls a named custom method, passing and returning parameters."),
          sp(6),
          h2("Inheritance chain for property attributes (broadest → most specific)"),
          p("<b>IDO Property Class → IDO Property → Property Class Extension → "
            "Component Class → Component (instance on form)</b>"),
          p("The most specific level always wins. A component-level override beats everything above it."),
          hr()]

    e += [h1("4. Creating New Functionality — The New Data Maintenance Wizard"),
          p("When you need a brand-new entity (new SQL table + IDO + form), "
            "the New Data Maintenance Wizard creates all three in a guided sequence."),
          tbl(["What the wizard creates", "Details"],
              [["SQL Table",
                "A new table with your defined columns plus the standard system columns "
                "(RowPointer, CreateDate, CreateUser, ModifyDate, ModifyUser, InWorkflow)."],
               ["IDO Definition",
                "An IDO bound to the new table, with properties corresponding to each column."],
               ["Multiview Form",
                "A two-pane WinStudio form (grid list on top, detail below) bound to the new "
                "IDO. Immediately usable for CRUD operations."]],
              [2.0*inch, W-2.0*inch]),
          sp(),
          p("<b>Post-wizard refinement:</b> Set the primary key; mark required fields; "
            "add dropdown list sources (list sources); add validation logic in the IDO or "
            "extension class; refine form layout and tab order; add to the Explorer navigation."),
          p("<b>Access path:</b> In Design Mode → System &gt; Form &gt; Definition &gt; New "
            "(choose 'Build New Data Maintenance Form')."),
          hr()]

    e += [h1("5. Extending Existing IDOs — Adding Custom Data"),
          p("The most frequent developer task: adding custom columns to existing application "
            "tables that Infor owns. Two supported approaches:"),
          h2("Approach A — User Extended Tables (UETs)  [preferred, upgrade-safe]"),
          p("UETs add physical columns to existing application tables without modifying "
            "Infor's base IDO definition. Infor upgrades do not remove UET columns."),
          tbl(["Step", "Form to use / action"],
              [["1. Define a UET Class", "UET Classes form — give the set of new fields a name."],
               ["2. Define UET Fields", "UET User Fields form — each field: name, data type (e.g. nvarchar(50)), length."],
               ["3. Link fields to class", "UET Class/Field Relationships form."],
               ["4. Link class to table", "UET Table/Class Relationships form — specify the real table (e.g. co_mst)."],
               ["5. Apply schema", "UET Impact Schema form → click Process. Physically adds columns to SQL Server."],
               ["6. Refresh metadata", "Ctrl+U (with 'Unload IDO Metadata With Forms' on) or restart IDO Runtime Service."],
               ["7. If using replication", "Replication Management form → Regenerate Replication Triggers."]],
              [1.7*inch, W-1.7*inch]),
          sp(),
          h2("Approach B — IDO Property Extension at Site scope"),
          p("Add properties directly to an existing vendor IDO at site scope. The vendor base "
            "IDO is untouched; your extension properties are merged at runtime. "
            "Use when UETs are insufficient (e.g., adding a calculated/joined property)."),
          hr()]

    e += [h1("6. Extending Existing Forms"),
          p("A Site Developer can add components, event handlers, and tab pages to any vendor "
            "form at Site scope — without touching the base vendor definition."),
          tbl(["Task", "How to do it"],
              [["Add a new field/component",
                "Drag from Toolbox → draw on form. Bind to an IDO property: "
                "Component sheet &gt; Data Source &gt; Binding. "
                "The IDO property must exist first (add it to the IDO if needed)."],
               ["Add an event handler",
                "Edit &gt; Event Handlers → New. Set Event Name, Sequence, Response Type "
                "(e.g. Method Call, Set Values, Generate Application Event, Goto Form)."],
               ["Add a NoteBook tab",
                "Add a NoteBook component; add NotebookTab children inside; "
                "assign captions; set tab order (select notebook before tabs inside)."],
               ["Override a base event handler",
                "Set 'From Base Form' = False on the inherited handler. "
                "Warning: this re-associates ALL handlers for that event — review the "
                "full list. Only override what you need to change."],
               ["Extended vs. copied form",
                "Extension: inherits future base-form upgrades (preferred). "
                "Copy: fully independent — you own all maintenance. "
                "Prefer extension unless you need full independence."]],
              [1.9*inch, W-1.9*inch]),
          hr()]

    e += [h1("7. Portal Forms — External User Access"),
          p("The Customer Portal and Vendor Portal let external users interact with the "
            "application via a browser, without WinStudio. "
            "The course uses an <b>Expense Report submission form</b> as the worked example."),
          tbl(["Concept", "Detail"],
              [["Enable a form for portal", "Set form property 'Display In Portal' = True."],
               ["Control visible fields", "Mark fields Hidden = True in the portal version to restrict what external users see."],
               ["Enforce data security", "Use IDO-level permanent filter expressions so each portal user only sees their own data. "
                                         "UI hiding alone is never sufficient security."],
               ["Workflow integration", "Typical pattern: external user submits via portal → Application Event System fires → "
                                        "internal manager approves in WinStudio → record commits to database."]],
              [1.8*inch, W-1.8*inch]),
          hr()]

    e += [h1("8. Team Development — Check-In / Check-Out and FormSync"),
          p("In a team, multiple Site Developers may need to work on the same form set. "
            "The check-out mechanism prevents simultaneous overwrites."),
          tbl(["Action", "What it does"],
              [["Check Out", "Locks the form definition for your exclusive edit. Others see 'Checked Out By [you]' and cannot save."],
               ["Check In", "Releases the lock and publishes your changes to all users."],
               ["Discard Checkout", "Abandons your in-progress changes and releases the lock without saving."],
               ["Force Check In (Vendor Dev only)", "Releases another user's lock in an emergency."]],
              [2.2*inch, W-2.2*inch]),
          sp(),
          h2("FormSync — moving customizations between environments"),
          p("FormSync exports/imports form definitions and global objects (component classes, "
            "validators, strings, form-level event handlers) as XML files. "
            "<b>FormSync does NOT cover:</b> IDO metadata, SQL tables/stored procedures, "
            "Application Event System event/handler metadata, report definitions — "
            "those require separate deployment procedures."),
          p("FormSync path: Master Explorer &gt; Modules &gt; System &gt; Utilities &gt; FormSync."),
          hr()]

    e += [h1("Quick Reference: Essential Design-Mode Paths"),
          tbl(["Task", "Path / shortcut"],
              [["Enter / exit Design Mode", "Ctrl+E (after clearing filter-in-place), or toolbar button"],
               ["New form + IDO + table wizard", "System > Form > Definition > New"],
               ["Copy a form", "System > Form > Definition > Copy"],
               ["Check out / check in", "System > Form > Definition > Check Out / Check In"],
               ["UET setup (all steps)", "Master Explorer > Modules > System > User Extended Tables"],
               ["UET Impact Schema", "Master Explorer > Modules > System > UET Impact Schema"],
               ["Discard IDO metadata cache", "Ctrl+U (requires 'Unload IDO Metadata With Forms' in User Preferences > Runtime Behaviors)"],
               ["Restart IDO Runtime Service", "Windows Services console on utility server > Infor Framework IDO Runtime Services"],
               ["FormSync", "Master Explorer > Modules > System > Utilities > FormSync"],
               ["Check current permission level", "Help > About <servername>"]],
              [2.3*inch, W-2.3*inch])]

    build(r"c:\Users\iceco\Desktop\Syteline\04 Extending the Application with Mongoose\csi_extending_mongoose_notes.pdf", e)


# ───────────────────────────────────────────────────────────────
# PDF 2 — Creating Reports Using Mongoose (Folder 05)
# ───────────────────────────────────────────────────────────────
def pdf_reports():
    e = []
    e += [p("CSI v10 — Creating Reports Using Mongoose", 'T'),
          p("Study notes from the Infor official training workbook (166 pages)", 'ST'), hr()]

    e += [h1("Why this guide matters"),
          p("Standard CSI reports are built inside the Mongoose framework using "
            "<b>Report Type forms</b>, <b>FlexLayout</b> components, and <b>DataViews</b> "
            "(IDO methods that supply data to a report). This is a distinctly different "
            "approach from SQL Server Reporting Services (SSRS) — Mongoose reports live "
            "in WinStudio and deploy with the application metadata."),
          p("This guide is essential if you need to: build a new operational report, "
            "modify an existing Mongoose report, understand why a report runs slowly, "
            "or add parameters/criteria to an existing report."),
          hr()]

    e += [h1("1. Mongoose Reporting Architecture"),
          p("Mongoose reports are WinStudio forms of a special type — <b>Report Type forms</b>. "
            "They display and format data but do not allow editing. The data pipeline is:"),
          tbl(["Stage", "What happens"],
              [["1. Report Criteria form", "User enters parameters (date ranges, item filters, etc.)."],
               ["2. DataView / IDO Method called", "The Report Type form calls one or more IDO methods (DataViews) that query the database and return result sets."],
               ["3. Report Type form renders", "The FlexLayout component organizes the result set into a formatted, printable layout."],
               ["4. Output", "User previews, prints, or exports (PDF, Excel, CSV)."]],
              [1.5*inch, W-1.5*inch]),
          hr()]

    e += [h1("2. IDO Methods and DataViews"),
          p("A <b>DataView</b> in Mongoose reporting is simply an IDO method (usually of type "
            "Fetch) whose result set drives a report. The method accepts parameters "
            "(criteria) and returns a structured set of rows and columns."),
          h2("Creating a DataView IDO method"),
          bl("On the IDO, add a new method of type Fetch."),
          bl("The method body is a stored procedure that accepts @parameters and returns a result set."),
          bl("Define the method's parameters: name, direction (input/output), data type."),
          bl("The result set's column names become the property names available for binding in the report."),
          sp(6),
          h2("Key rules for DataView stored procedures"),
          bl("Always use a SELECT ... FROM ... WHERE pattern that returns a consistent column set."),
          bl("Add NOLOCK hints on read-heavy reports to avoid blocking production transactions."),
          bl("Use parameters for all filter criteria — never hard-code values in the procedure."),
          bl("Test the stored procedure directly in SQL Server Management Studio before wiring it to a report."),
          hr()]

    e += [h1("3. Report Type Forms"),
          p("A Report Type form is a WinStudio form with its Form Type property set to "
            "<b>Report</b>. This activates the report-specific toolset in Design Mode."),
          tbl(["Property / Feature", "What it controls"],
              [["Form Type = Report", "Activates the FlexLayout toolbox and report-specific behaviors."],
               ["Collection binding", "The form's collection is bound to a DataView IDO method (not a standard IDO)."],
               ["Report Criteria link", "A separate 'criteria' form is linked via the Report's Criteria Form Name property. The criteria form collects parameters that are passed to the DataView."],
               ["Page setup", "Paper size, orientation, margins — set via Form sheet > Page Setup properties."],
               ["Preview / Print / Export", "Standard toolbar buttons. Output formats: PDF, Excel, CSV, directly to a printer."]],
              [2.0*inch, W-2.0*inch]),
          sp(),
          p("<b>Finding existing reports:</b> In the Explorer, reports appear under their "
            "module (e.g., Modules &gt; Customer &gt; Reports). You can also use "
            "Ctrl+O and search by form name."),
          hr()]

    e += [h1("4. FlexLayout — The Report Layout Component"),
          p("FlexLayout is the specialized layout component used inside Report Type forms. "
            "It provides bands (sections) for organizing report content."),
          tbl(["FlexLayout Band", "Purpose"],
              [["Report Header", "Printed once at the very top of the report (title, logo, run date, parameters used)."],
               ["Page Header", "Printed at the top of every page (column headings, page number)."],
               ["Group Header", "Printed once at the start of each group (e.g., 'Customer: Acme Corp')."],
               ["Detail Band", "Printed once per data row — the main body of the report."],
               ["Group Footer", "Printed at the end of each group (subtotals, group summaries)."],
               ["Page Footer", "Printed at the bottom of every page (page X of Y, footer text)."],
               ["Report Footer", "Printed once at the very end (grand totals, summary statistics)."]],
              [1.8*inch, W-1.8*inch]),
          sp(),
          h2("Adding components to FlexLayout bands"),
          bl("Drag standard WinStudio components (Static, Edit, Grid, etc.) into a band."),
          bl("Bind components to DataView properties using the standard Binding property."),
          bl("Use Static components with calculated expressions for running totals, "
             "formatted dates, page numbers."),
          bl("<b>SUM / COUNT / AVG functions</b> are available in calculated field expressions "
             "for group and report footers."),
          hr()]

    e += [h1("5. Secondary Collections"),
          p("A Secondary Collection adds a child data set to a report — for example, "
            "order lines under each order header. It is a second IDO method (DataView) "
            "that is linked to the primary collection via a join key."),
          tbl(["Concept", "Detail"],
              [["Primary collection", "The main DataView that drives the report (e.g., Customer Orders)."],
               ["Secondary collection", "A child DataView (e.g., Order Lines) linked to the primary via a common key (e.g., CoNum)."],
               ["Link property", "Set on the secondary collection: which property in the child matches which property in the parent."],
               ["Rendering", "The Detail Band can contain a nested FlexLayout bound to the secondary collection, printing child rows under each parent row."]],
              [1.8*inch, W-1.8*inch]),
          sp(),
          p("<b>Performance note:</b> Each parent row causes a separate query for child rows "
            "unless you pre-join in the DataView stored procedure. For large data sets, "
            "consider returning everything in one query and using GROUP BY in the report."),
          hr()]

    e += [h1("6. Sub-Reports"),
          p("A Sub-Report embeds one complete Report Type form inside another. "
            "Use sub-reports when two datasets are too different to join in SQL "
            "but need to appear together on the printed page."),
          tbl(["Concept", "Detail"],
              [["Parent report", "The outer report. Contains a Sub-Report component in one of its bands."],
               ["Child report", "A fully independent Report Type form, designed separately."],
               ["Linking", "Pass parameters from the parent to the child via the Sub-Report component's parameter bindings (parent property → child parameter)."],
               ["Rendering", "The child report renders inline at the position of the Sub-Report component."],
               ["When to use vs. Secondary Collection",
                "Use Secondary Collection for simple parent-child row nesting. "
                "Use Sub-Report when the child data has a completely different layout, "
                "grouping, or criteria logic."]],
              [1.8*inch, W-1.8*inch]),
          hr()]

    e += [h1("7. Report Criteria Forms"),
          p("A Report Criteria form is a standard WinStudio form that collects user "
            "input (date ranges, filters, checkboxes) before the report runs. "
            "It is linked to the Report Type form via the Report's "
            "<b>Criteria Form Name</b> property."),
          tbl(["Element", "How it works"],
              [["Parameter fields", "Standard Edit/DateCombo/Combo components on the criteria form, not bound to any IDO — just collecting input."],
               ["Run button", "A button that reads the criteria field values and passes them as parameters to the Report Type form's DataView IDO method."],
               ["Default values", "Set via form event handlers: on FormLoad, set default date ranges, default filter values, etc."],
               ["Validation", "Validate criteria before calling the report (e.g., ensure From Date ≤ To Date)."]],
              [1.8*inch, W-1.8*inch]),
          sp(),
          p("<b>Access pattern:</b> The user opens the Criteria form, fills in parameters, "
            "clicks Run (or Preview). The Criteria form calls the Report Type form with "
            "parameters. The Report Type form calls its DataView. Data is returned and "
            "rendered. The user then uses Preview → Print or Export."),
          hr()]

    e += [h1("8. IDO Collections on Reports — Using Standard IDO Data"),
          p("In addition to DataView methods, a Report Type form can bind to a "
            "standard IDO's LoadCollection — effectively treating any existing IDO "
            "as a report data source without writing a custom DataView method."),
          bl("Bind the report's collection directly to an existing IDO (e.g., SLCustomers)."),
          bl("Set a Permanent Filter Expression on the report's collection to restrict data."),
          bl("Use this approach for simple reports where the IDO already returns the right data "
             "and no complex SQL joins are needed."),
          bl("For complex multi-table joins or aggregations, a custom DataView IDO method "
             "(stored procedure) will always give better performance and flexibility."),
          hr()]

    e += [h1("Quick Reference: Report Development Checklist"),
          tbl(["Step", "Action"],
              [["1. Design the data", "Write and test the stored procedure in SQL Server Management Studio first."],
               ["2. Create the IDO method (DataView)", "Add a Fetch method to an appropriate IDO; reference the stored procedure; define parameters."],
               ["3. Create the Criteria form", "Standard WinStudio form — collect user parameters; wire Run button."],
               ["4. Create the Report Type form", "New form, Form Type = Report; bind to DataView; set Criteria Form Name."],
               ["5. Build FlexLayout", "Add bands; bind components to DataView properties; add group headers/footers if needed."],
               ["6. Add Secondary Collections", "If child rows needed: define child DataView; link to parent; add nested FlexLayout."],
               ["7. Add Sub-Reports", "If independent child layouts needed: build child report separately; add Sub-Report component in parent."],
               ["8. Test end-to-end", "Open Criteria form → enter parameters → run → verify data accuracy → test edge cases (empty result, large result)."],
               ["9. Register in Explorer", "Add the Criteria form to the appropriate module folder in the Explorer navigation."]],
              [1.3*inch, W-1.3*inch])]

    build(r"c:\Users\iceco\Desktop\Syteline\05 Creating Reports Using Mongoose\csi_reports_mongoose_notes.pdf", e)


# ───────────────────────────────────────────────────────────────
# PDF 3 — Using the Application Event System (AES)
# ───────────────────────────────────────────────────────────────
def pdf_aes():
    e = []
    e += [p("CSI v10 — Using the Application Event System (AES)", 'T'),
          p("Study notes from the Infor official training workbook (302 pages)", 'ST'), hr()]

    e += [h1("Why this guide matters"),
          p("The Application Event System (AES) is the automation engine inside CloudSuite "
            "Industrial. Without it, automating approvals, sending notifications, or gating "
            "a record change pending a manager's response requires writing procedural code. "
            "With it, you define metadata rules — no compilation needed — and the system "
            "handles the rest, upgrade-safely."),
          p("Use cases: auto-notify on new records, approval workflows with suspend/commit, "
            "multi-level management approvals with voting, adding information to a record "
            "via a prompted response, triggering events on a schedule or when a threshold "
            "is crossed."),
          p("Prerequisites: UI Navigation (4-unit course). Basic SQL knowledge is recommended "
            "but not required for simple notification workflows."),
          hr()]

    e += [h1("1. The Three Basic Components"),
          p("Every AES scenario is built from the same three components, chained together:"),
          tbl(["Component", "What it is"],
              [["Event",
                "A uniquely named occurrence that can be triggered by user actions, database "
                "conditions, time passing, or another event's handler. The event itself is "
                "just a name — it does nothing until a handler is attached."],
               ["Event Handler",
                "Associated with one event. Defines: which conditions must be true, "
                "whether to run synchronously or asynchronously, whether to suspend "
                "the record pending a response, and which actions to take. "
                "One event can have multiple handlers; each handler belongs to only one event."],
               ["Event Action",
                "The individual unit of work inside a handler. Types include: Notify, Prompt, "
                "Fail, Finish, Branch, Set Values, Load IDO Row, Update Collection, "
                "Generate Event, Call IDO Method, Call Database Method, and more. "
                "A handler must have at least one action."]],
              [1.7*inch, W-1.7*inch]),
          sp(),
          p("<b>Mental model:</b> Event fires → Handler evaluates → Actions execute in sequence. "
            "If any synchronous action fails (and Ignore Failure is off), the chain stops "
            "and the handler exits with Failure status."),
          hr()]

    e += [h1("2. Event Types"),
          tbl(["Type", "Who creates them / what triggers them"],
              [["Framework Events (Access As = 'core')",
                "Created by Infor; fire automatically when the system does something "
                "(insert a row, update a row, delete a row, load a collection, invoke a method, "
                "login/logout). You cannot create framework events, but you can attach your "
                "own handlers to them. Examples: IdoOnItemInsert, IdoOnItemUpdate, "
                "IdoPostItemInsert, IdoPostItemDelete, IdoOnLoadCollection, SessionOnLogin."],
               ["Application-Specific Events",
                "Created by Infor or business partners for specific business processes. "
                "Tagged with the owner's Access As identifier."],
               ["Customer-Defined Events",
                "Created by your organization (Access As = blank). "
                "Can be triggered via: Event Trigger form (condition/time-based), "
                "Generate Event action type (from another handler), "
                "form event handler with 'Generate Application Event' response type, "
                "WinStudio API or .NET code."]],
              [1.8*inch, W-1.8*inch]),
          sp(),
          p("<b>Key insight:</b> Framework events fire constantly in the background — every "
            "time any user saves a record, IdoOnItemInsert or IdoOnItemUpdate fires. "
            "Nothing happens unless you add a handler. The event fires, and if no handler "
            "matches, it is silently discarded."),
          hr()]

    e += [h1("3. The Access As Identifier"),
          p("Every event, handler, and global constant is tagged with an <b>Access As</b> "
            "identifier that establishes ownership. You can only modify or delete objects "
            "whose Access As matches your current setting."),
          tbl(["Access As value", "Meaning"],
              [["core", "Owned by Infor's framework team. Read-only for everyone else."],
               ["Any specific name", "Owned by an Infor application team or authorized business partner. "
                                     "You can attach your handlers to their events, but cannot edit their objects."],
               ["Blank (empty)", "Owned by your end-customer organization. "
                                  "This is the Access As value for all the work you do in this course."]],
              [1.5*inch, W-1.5*inch]),
          sp(),
          p("To check your current Access As: "
            "Master Explorer &gt; Modules &gt; System &gt; Access As form (display-only)."),
          hr()]

    e += [h1("4. Synchronicity — Synchronous vs. Asynchronous"),
          p("Every event and every event handler is either synchronous or asynchronous. "
            "This is the most important behavioral distinction in the AES."),
          tbl(["Mode", "How it runs"],
              [["Synchronous",
                "Runs in the same thread as the action that triggered it. "
                "Blocks the user/process until all synchronous handlers complete. "
                "A failure stops the chain and can roll back the originating transaction. "
                "Framework events are always synchronous."],
               ["Asynchronous",
                "Queued to the Infor Framework Event Service (utility server). "
                "The originating thread continues immediately after successful queuing. "
                "Runs independently — failure does not affect the originating thread. "
                "Use for notifications that should not block the user."]],
              [1.7*inch, W-1.7*inch]),
          sp(),
          h2("How to make an event sync or async"),
          tbl(["How the event is generated", "Sync or Async?"],
              [["Framework (core) event", "Always synchronous"],
               ["Form event handler: Generate Application Event, Synchronous checkbox ON", "Synchronous"],
               ["Form event handler: Generate Application Event, Synchronous checkbox OFF", "Asynchronous"],
               ["Stored procedure: EXEC FireEventSp", "Synchronous"],
               ["Stored procedure: EXEC PostEventSp", "Asynchronous"],
               [".NET: FireApplicationEvent(Synchronous=True)", "Synchronous"],
               [".NET: FireApplicationEvent(Synchronous=False)", "Asynchronous"],
               ["Event action: Generate Event, SYNCHRONOUS(TRUE)", "Synchronous"],
               ["Event action: Generate Event, SYNCHRONOUS(FALSE)", "Asynchronous"]],
              [3.5*inch, W-3.5*inch]),
          sp(),
          p("<b>Handler-level setting:</b> Individual handlers also have a Synchronous "
            "checkbox. Clearing it queues the handler asynchronously even when the event "
            "itself is synchronous — useful for notifications attached to framework events."),
          hr()]

    e += [h1("5. Suspension — Gating a Record Change on Approval"),
          p("Suspension is the mechanism that holds a database change in limbo until "
            "a condition is met (typically a manager's approval). Only three framework "
            "events support suspension:"),
          bl("<b>IdoOnItemInsert</b>"),
          bl("<b>IdoOnItemUpdate</b>"),
          bl("<b>IdoOnItemDelete</b>"),
          sp(4),
          p("When a handler for one of these events has <b>Suspend = True</b>, the system "
            "follows a two-phase process:"),
          tbl(["Phase", "What happens"],
              [["Suspend-Validating Mode",
                "The system begins a transaction, performs the insert/update/delete to validate "
                "SQL constraints, runs synchronous non-suspended handlers, then rolls back "
                "the transaction. The record is locked (InWorkflow = 1) so no one else can "
                "change it. A task is queued for the commit phase."],
               ["Suspend-Committing Mode",
                "The Event Service picks up the queued task. It runs all handlers (including "
                "those marked Suspend). If all succeed, the change is committed to the database "
                "and InWorkflow is cleared. If any handler fails, the change is abandoned "
                "and InWorkflow is cleared."]],
              [2.0*inch, W-2.0*inch]),
          sp(),
          p("<b>Practical use:</b> Approval workflows. A new purchase order is created → "
            "IdoOnItemInsert fires with Suspend = True → a Prompt action sends the manager "
            "an approval request → the PO record is locked → when the manager approves, "
            "the commit phase runs and the PO is saved. If the manager rejects, a Fail "
            "action prevents the commit."),
          hr()]

    e += [h1("6. Key Forms of the Application Event System"),
          p("Navigate to most AES forms via: "
            "Master Explorer &gt; Modules &gt; System &gt; Event System."),
          tbl(["Form", "What you do here"],
              [["Access As", "View-only. Shows your current ownership identifier."],
               ["Events", "Name events. An event defined here but not on Event Triggers or Event Handlers is inert."],
               ["Event Triggers", "Define time/condition-based triggers that fire a custom event. "
                                   "Cannot trigger framework events here."],
               ["Event Handlers", "The primary work form. Create handlers: set Event Name, Applies To Objects, "
                                   "Synchronous checkbox, Suspend checkbox, Keep With / Chronology (ordering)."],
               ["Event Actions", "Linked from Event Handlers. Define the sequence of actions for a handler. "
                                  "Opened via the 'Event Actions' button on the handlers form."],
               ["Event Variable Groups", "Define initial state values (variable name + starting value) "
                                          "to pass to a handler when it starts executing."],
               ["Event Global Constants", "Named static values referenced in event expressions (GC(ConstantName)). "
                                           "Change the constant once and all handlers that reference it update."],
               ["Event Handler Diagram", "Visual flowchart of a handler's action sequence. "
                                          "Drag-and-drop to add/remove actions; double-click to edit."],
               ["New Workflow Wizard", "Guided wizard for simple 'Notify Me When' or 'Notify You When' "
                                        "notification workflows — no manual handler/action creation needed."],
               ["Workflow Event Handler Activation", "50+ predefined handlers (alert on late shipment, "
                                                       "approve credit limit change, etc.). "
                                                       "Fill in recipients and activate."],
               ["Event Status", "Track running and completed events. "
                                 "View handlers, parameters, voting status, output parameters."],
               ["Event Handler Status", "Drill into a specific handler's run: "
                                         "Actions tab (which actions ran), Variables tab (current values), "
                                         "Voting tab (approval status)."],
               ["Event Queue", "View asynchronous events waiting to be processed (FIFO order)."],
               ["Event Revisions / Handler Revisions", "Read-only history of metadata snapshots. "
                                                         "Running events execute against the revision in effect "
                                                         "when they started, not the current metadata."],
               ["Suspended Updates", "List of records locked in InWorkflow = 1, waiting for handler completion."],
               ["Inbox", "Where system messages and approval prompts appear for the recipient. "
                          "Response tab shows voting buttons; Variables tab shows payload data."],
               ["Session Access As", "Enable/disable handlers by Access As identifier for troubleshooting. "
                                       "Useful for isolating whether a custom handler is causing a bug."]],
              [2.1*inch, W-2.1*inch]),
          hr()]

    e += [h1("7. Creating a Custom Event and Handler — Step by Step"),
          tbl(["Step", "Action"],
              [["1. Name the event", "Events form — add a row with a unique event name (optional; you can also name it on the handler form directly)."],
               ["2. Define the handler", "Event Handlers form → New. Set: Event Name, Handler Description, "
                                          "Applies to Objects (filter to a specific IDO, e.g. SLCustomers), "
                                          "Synchronous checkbox (clear for async notifications), "
                                          "Suspend checkbox (check if you need approval gating)."],
               ["3. Add event actions", "Click 'Event Actions' on the handler. For each action: "
                                         "set Action Sequence number (10, 20, 30...) and Action Type."],
               ["4. Set action parameters", "Click 'Edit Parameters' to open the type-specific parameter form. "
                                              "Build expressions using the Expression Editor. "
                                              "Click 'Check Syntax' before saving."],
               ["5. Create global constants", "Event Global Constants form — define reusable values "
                                               "(e.g., CreditMgr = 'jsmith'). "
                                               "Reference with GC(ConstantName) in expressions."],
               ["6. Discard metadata cache", "Ctrl+U (with 'Unload IDO Metadata With Forms' on) — "
                                              "ensures the running system sees your new handler."],
               ["7. Test", "Trigger the event (perform the action on the relevant form). "
                            "Check Event Status form or Inbox to verify."]],
              [1.5*inch, W-1.5*inch]),
          hr()]

    e += [h1("8. Event Action Parameters — Key Functions"),
          p("Action parameters are written in an expression language using FUNCTION(value) syntax. "
            "Key function categories:"),
          h2("Value retrieval functions"),
          tbl(["Function", "Returns"],
              [["V(varName)", "Value of an event variable."],
               ["GC(constantName)", "Value of an event global constant."],
               ["E(paramName)", "Value of an event parameter."],
               ["P(propertyName) or PROPERTY(propertyName)", "Value of a framework event property (the data being inserted/updated/deleted)."],
               ["FP(propertyName) or FILTERPROPERTY(propertyName)", "Value as a quoted string (for use in filter expressions)."],
               ["SV(varName)", "Value of a WinStudio session variable."],
               ["ORIGINATOR()", "User ID of the person whose action triggered the event."],
               ["CURDATETIME()", "Current date and time (site-adjusted)."],
               ["PROPERTYMODIFIED(propertyName)", "TRUE if the property was changed in this update (IdoOnItemUpdate only)."]],
              [2.5*inch, W-2.5*inch]),
          sp(),
          h2("Text construction functions"),
          tbl(["Function", "Use"],
              [["SUBSTITUTE('text with {0} and {1}', expr0, expr1, ...)",
                "Builds a string by replacing {0}, {1} etc. with evaluated expressions. "
                "Most common way to build notification message bodies."],
               ["CLIENTSUBSTITUTE(...)",
                "Same as SUBSTITUTE but the result is stored with localization markers "
                "so each Inbox user sees the string in their configured language."]],
              [2.5*inch, W-2.5*inch]),
          sp(),
          h2("Voting / prompt result functions"),
          tbl(["Function", "Returns"],
              [["VOTINGRESULT(actionSequenceNum)", "Winning choice value from the specified Prompt action."],
               ["VOTINGTIE(actionSequenceNum)", "TRUE if the vote resulted in a tie."],
               ["VOTINGDISPARITY(actionSequenceNum)", "TRUE if any two recipients selected different choices."],
               ["RESPONDERS(actionNum [, choice])", "Count of recipients who responded (optionally for a specific choice)."],
               ["RECIPIENTS(actionNum)", "Total number of recipients who received the message."]],
              [2.5*inch, W-2.5*inch]),
          hr()]

    e += [h1("9. Requesting Approvals — Basic Pattern"),
          p("The most common AES workflow: send an approval request and suspend the "
            "record until the response is received."),
          h2("Required action sequence for a basic approval"),
          tbl(["Action #", "Type", "Purpose"],
              [["10", "Prompt", "Sends the approval request to the manager. "
                                "Key parameters: TO(recipient), SUBJECT(...), BODY(...), "
                                "QUESTION('Do you approve?'), CHOICES('1,sYes,0,sNo'), "
                                "VOTINGRULE(Plurality)."],
               ["20", "Fail (conditional)", "If the manager voted No: CONDITION(VOTINGRESULT(10) = '0'), "
                                              "RESULT('Rejected by manager.'). "
                                              "This prevents the record from committing."]],
              [0.8*inch, 1.0*inch, W-1.8*inch]),
          sp(),
          p("<b>Handler-level setting:</b> Check the <b>Suspend</b> checkbox on the handler "
            "so the record is held in InWorkflow=1 until the handler completes."),
          p("<b>Responding to a prompt (manager's perspective):</b> Open Inbox → open message "
            "→ click Response tab → click Approve or Reject button."),
          hr()]

    e += [h1("10. Voting Rules for Multi-Person Approvals"),
          p("When a Prompt is sent to multiple recipients, set the VOTINGRULE() parameter "
            "to define how the system tallies responses."),
          tbl(["Rule", "Behavior"],
              [["Majority", "First choice to receive > 50% of votes wins. Recommend using VOTINGTIE() for tie handling."],
               ["Plurality", "Choice with the most votes wins, even if < 50%."],
               ["ConditionalPlurality", "Plurality, but only if the winner reaches a specified MINIMUM() percentage."],
               ["MinimumCount", "First choice to reach a specified MINIMUM() vote count wins immediately."],
               ["MinimumPercentage", "First choice to reach a specified MINIMUM() percentage of all recipients wins immediately."],
               ["EarliestResponse", "First response received wins, regardless of choice. Voting closes immediately."],
               ["PreferredChoice", "If anyone votes for the designated PREFCHOICE(), that choice wins immediately. "
                                    "Otherwise falls back to Plurality."]],
              [2.0*inch, W-2.0*inch]),
          sp(),
          p("<b>Quorum:</b> The system automatically calculates the minimum number of votes "
            "needed to determine a winner. Once the quorum is reached, unvoted messages "
            "are expired and voting closes. Override with QUORUM(n) if needed."),
          hr()]

    e += [h1("11. Tracking Event System Status"),
          tbl(["Form", "Use it when..."],
              [["Event Status", "An event fired but you're not sure what happened. Look for failures, "
                                 "check parameters passed, see all handlers that ran."],
               ["Event Handler Status", "A specific handler didn't do what you expected. "
                                         "Actions tab shows which actions started. "
                                         "Variables tab shows variable values at failure."],
               ["Event Queue", "Checking whether asynchronous events are piling up or stalled."],
               ["Event Revisions / Handler Revisions", "Understanding why an old version of a handler ran "
                                                        "(handlers run against the revision in effect when they started)."],
               ["Suspended Updates", "Finding a record that is stuck in InWorkflow=1 "
                                      "(approval pending with no response received)."]],
              [2.0*inch, W-2.0*inch]),
          sp(),
          p("<b>Troubleshooting the event service not running:</b>"),
          bl("Verify the Infor Framework Event Service is Running (Windows Services on the utility server)."),
          bl("Verify your configuration is listed on the Event Service tab of the Service Configuration Manager."),
          bl("Check the Infor Framework Log Monitor for error messages."),
          hr()]

    e += [h1("12. The Infor Framework Event Service"),
          p("Asynchronous events and suspended events are processed by the "
            "<b>Infor Framework Event Service</b> — an independent Windows service on the utility server."),
          bl("Processes queued events in FIFO (first-in, first-out) order."),
          bl("After each queued item, checks for adjourned handlers whose retest/timeout time has arrived."),
          bl("Must be configured with your CloudSuite configuration (site name) in the Service Configuration Manager."),
          bl("If this service is not running, all asynchronous events and all suspended-commit processing will stall."),
          bl("The service can run on multiple servers for load-balancing; uses database locking to prevent double-processing."),
          sp(6),
          h2("Setting up the service"),
          bl("On the utility server: Start &gt; Infor CSI &gt; Service Configuration Manager (run as administrator)."),
          bl("Click the Event Service tab &gt; Add &gt; select your configuration &gt; Save."),
          bl("If you added a new configuration, restart the Infor Framework Event Service for it to take effect."),
          hr()]

    e += [h1("13. Setting Up External Email"),
          p("The AES can send messages to recipients' external email (Outlook, etc.) "
            "in addition to their WinStudio Inbox."),
          tbl(["Step", "Where"],
              [["1. Get SMTP settings", "From the email administrator."],
               ["2. Configure SMTP", "Intranets form (System administrator) → Reporting tab → SMTP section."],
               ["3. Add user email address", "Users form → Email Address tab → Primary email, set as Primary Email."],
               ["4. Enable send for user", "Users form → Email Address tab: check 'Send External Notifications' "
                                            "and/or 'Send External Prompts'."]],
              [1.5*inch, W-1.5*inch]),
          sp(),
          tbl(["Action type", "Sends to Inbox?", "Sends to external email?"],
              [["Notify", "Yes", "Yes (if user has external notifications enabled)"],
               ["Prompt", "Yes", "Yes (if user has external prompts enabled) — but free-form responses not supported via email"],
               ["Send Email", "No", "Yes — only sends to external email"]],
              [1.8*inch, 1.4*inch, W-3.2*inch]),
          sp(),
          p("<b>External prompt responses:</b> Recipients click a hyperlink in the email "
            "that opens a browser page and records their vote. If they respond via email "
            "first, the Inbox message is marked expired so they cannot vote twice."),
          hr()]

    e += [h1("Quick Reference: Common Expression Patterns"),
          tbl(["Pattern", "Expression"],
              [["Notify a global constant (role)", "TO(GC(CreditMgr))"],
               ["Notify the person who made the change", "TO(ORIGINATOR())"],
               ["Message body with substitution", "BODY(SUBSTITUTE('Credit limit changed to ${0} for {1}', FP('CreditLimit'), P('Name')))"],
               ["Check if a property was modified", "CONDITION(PROPERTYMODIFIED('CreditLimit'))"],
               ["Check if a property was NOT modified", "CONDITION(NOT PROPERTYMODIFIED('CreditLimit'))"],
               ["Filter to a specific form", "FILTERFORM('Customers') FILTER(SUBSTITUTE('CustNum={0}', FP('CustNum')))"],
               ["Yes/No voting choices", "CHOICES('1,sYes,0,sNo') QUESTION('Do you approve?')"],
               ["Fail if manager voted No", "CONDITION(VOTINGRESULT(10) = '0') RESULT('Rejected.')"],
               ["Expand a global constant textually (pre-parser)", "TGC(GlobalConstantName) — expands value before parsing"],
               ["Load old value before update (sync handler)", "Load IDO Row action with IDO(SLItems) PROPERTIES('LotSize') FILTER(SUBSTITUTE('Item={0}',FP('Item'))) SET(RV(OldValue)='LotSize')"]],
              [2.5*inch, W-2.5*inch])]

    build(r"c:\Users\iceco\Desktop\Syteline\Using The Application Event (workflows)\csi_aes_notes.pdf", e)


# ───────────────────────────────────────────────────────────────
# PDF 4 — Master Reference / Navigation Index
# ───────────────────────────────────────────────────────────────
def pdf_master():
    e = []
    e += [p("CSI / SyteLine v10 — Master Training Reference Guide", 'T'),
          p("Topic-to-document navigation index — use this to find which workbook covers what", 'ST'),
          hr()]

    e += [p("How to use this guide: When you have a question during implementation or "
            "development work, find the topic below and look up which source document "
            "covers it. Then open the corresponding summary PDF (in the same folder as "
            "the workbook) for the condensed notes, or open the original workbook for "
            "the full step-by-step exercises.", 'B'),
          sp(4)]

    # Document registry
    e += [h1("Document Registry — Source Workbooks"),
          tbl(["Label", "Full title", "Folder / file"],
              [["UI-NAV", "UI Navigation (Parts 1–4)",
                r"02 User Interface Navigation\CSI_v10_...Workbook.pdf  •  Notes: csi_ui_navigation_notes.md.pdf"],
               ["CFP", "Creating Form Personalizations",
                r"03 Creating From Personalizations\CSI_v10_...Workbook.pdf  •  Notes: csi_form_personalizations_notes.md.pdf"],
               ["EXT", "Extending the Application with Mongoose",
                r"04 Extending the Application with Mongoose\CSI_v10_...Workbook.pdf  •  Notes: csi_extending_mongoose_notes.pdf"],
               ["RPT", "Creating Reports Using Mongoose",
                r"05 Creating Reports Using Mongoose\CSI_v10_...Workbook.pdf  •  Notes: csi_reports_mongoose_notes.pdf"],
               ["AES", "Using the Application Event System",
                r"Using The Application Event (workflows)\CSI_Using...Workbook.pdf  •  Notes: csi_aes_notes.pdf"]],
              [0.7*inch, 2.3*inch, W-3.0*inch]),
          hr()]

    # Topic index — organized by subject area
    e += [h1("Topic Index — Organized by Subject Area")]

    e += [h2("Application Structure & Navigation"),
          tbl(["Topic", "Document(s)"],
              [["Opening and navigating forms", "UI-NAV"],
               ["Form types (Multiview, Query, Grid-only, Report, Utilities)", "UI-NAV"],
               ["Filter-in-place vs. Query forms (Ctrl+Q)", "UI-NAV"],
               ["Form modes: Filter / Refresh / New", "UI-NAV"],
               ["Grid vs. Detail view; splitter bar; Ctrl+1 / Ctrl+2", "UI-NAV"],
               ["Explorer: My Folders, Master Explorer, Public Folders, User Folders", "UI-NAV"],
               ["Keyboard shortcuts (Ctrl+O, F4, F5, F7/F8, Ctrl+S...)", "UI-NAV"],
               ["Smart Client vs. Web Client differences", "UI-NAV"],
               ["Notes (object notes, class notes, system/user notes, internal/external)", "UI-NAV"],
               ["Printing, output formats, export to Excel", "UI-NAV"],
               ["Workspaces (form groups)", "UI-NAV"],
               ["Activities and Utilities — batch processing, preview/commit vs. process-only", "UI-NAV"]],
              [3.0*inch, W-3.0*inch]),
          sp(4)]

    e += [h2("Form Customization (Design Mode)"),
          tbl(["Topic", "Document(s)"],
              [["Entering Design Mode; permission levels (5 levels)", "CFP, EXT"],
               ["Scope levels: Vendor / Site / Group / User; resolution order", "CFP, EXT"],
               ["Fonts and themes (Infor vs. Classic)", "CFP"],
               ["Background colors (solid, gradient) and background images", "CFP"],
               ["Component toolbox: Button, CheckBox, Edit, Combo, Grid, NoteBook...", "CFP"],
               ["Adding, aligning, and sizing components; alignment toolbar", "CFP"],
               ["Tab order — setting, rules, color coding", "CFP"],
               ["Read Only, Hidden, Visible When, Enabled When, Required When properties", "CFP"],
               ["Reverting a form to previous scope; System > Help > About This Form", "CFP"],
               ["Copying a form (System > Form > Definition > Copy)", "CFP, EXT"],
               ["Check-in / check-out of form definitions", "EXT"],
               ["FormSync — exporting/importing customizations between environments", "CFP, EXT"],
               ["Extended form vs. copied form — tradeoffs", "EXT"]],
              [3.0*inch, W-3.0*inch]),
          sp(4)]

    e += [h2("IDOs, Properties, and Data Architecture"),
          tbl(["Topic", "Document(s)"],
              [["Three-tier architecture (Client / IDO Runtime / Database)", "CFP, EXT"],
               ["What an IDO is; anatomy (table refs, properties, methods, extension class)", "CFP, EXT"],
               ["Property Classes — creating and using; the inheritance chain", "CFP, EXT"],
               ["Property Class Extensions — UI-level overrides of IDO property behavior", "CFP"],
               ["Component Classes — reusable component attribute bundles", "CFP"],
               ["IDO Property binding on a component", "CFP, EXT"],
               ["Read-Only For Existing Records vs. Read-Only For New Records", "CFP"],
               ["Creating a brand-new IDO + table + form (New Data Maintenance Wizard)", "EXT"],
               ["Extending an existing IDO at Site scope", "EXT"],
               ["User Extended Tables (UETs) — adding columns to existing tables", "CFP, EXT"],
               ["UET workflow: Classes → Fields → Class/Field → Table/Class → Impact Schema", "EXT"],
               ["IDO Methods: Fetch, Non-fetch, GetProperty, SetProperty", "EXT"],
               ["Standard built-in IDO methods: LoadCollection, UpdateCollection, GetPropertyInfo, Invoke", "EXT"]],
              [3.0*inch, W-3.0*inch]),
          sp(4)]

    e += [h2("List Sources, Validators, Strings"),
          tbl(["Topic", "Document(s)"],
              [["List sources: IDO Collection, IDO Method, Inline, Script", "CFP"],
               ["User-defined types (reusable named lists of values)", "CFP"],
               ["Validators: types (Alphanumeric, DateTime, Inline list, In Collection)", "CFP"],
               ["Validate Immediately vs. on-save; message display options", "CFP"],
               ["Strings (reusable translated text); naming prefixes s/f/m/t", "CFP"]],
              [3.0*inch, W-3.0*inch]),
          sp(4)]

    e += [h2("Event Handlers (Form-Level)"),
          tbl(["Topic", "Document(s)"],
              [["Form event handlers vs. Application Event System handlers", "CFP, AES"],
               ["Response types: Collection processing, Method call, Set values, Generate event, Goto form...", "CFP"],
               ["Handler sequence numbers; Ignore Failure parameter", "CFP"],
               ["Built-in system responses always run last", "CFP"],
               ["From Base Form = False — overriding inherited handlers", "CFP, EXT"],
               ["Only When Current Collection Is — scoping a handler to one collection", "CFP"]],
              [3.0*inch, W-3.0*inch]),
          sp(4)]

    e += [h2("Application Event System (AES) — Automation & Workflows"),
          tbl(["Topic", "Document(s)"],
              [["What the AES is; three components (Event / Handler / Action)", "AES"],
               ["Framework events vs. customer-defined events; Access As identifier", "AES"],
               ["Synchronous vs. asynchronous events and handlers", "AES"],
               ["Suspension — gating a record change on approval; InWorkflow flag", "AES"],
               ["Suspend-validating mode vs. suspend-committing mode", "AES"],
               ["Adjournment and resumption (Prompt, Wait, Sleep action types)", "AES"],
               ["Success, failure, and retry rules; Ignore Failure option", "AES"],
               ["Transactions with synchronous events; rolling back", "AES"],
               ["Setting up the Infor Framework Event Service", "AES"],
               ["Event global constants — GC(), TGC(); use cases", "AES"],
               ["Event variables and initial states — V(), Event Variable Groups form", "AES"],
               ["Event Triggers — condition/time-based firing; retest intervals", "AES"],
               ["New Workflow Wizard — quick notification setup", "AES"],
               ["Predefined workflow event handlers (50+) — Workflow Event Handler Activation form", "AES"],
               ["Event actions: Notify, Prompt, Fail, Finish, Branch, Set Values, Load IDO Row...", "AES"],
               ["Event action parameter syntax — FUNCTION(value); nesting rules", "AES"],
               ["SUBSTITUTE() and CLIENTSUBSTITUTE() for message bodies", "AES"],
               ["PROPERTYMODIFIED() — detecting changes in IdoOnItemUpdate", "AES"],
               ["Requesting approvals (basic) — Prompt + Fail + Suspend pattern", "AES"],
               ["Multi-level approvals — Branch action; chained Prompt + Set Values blocks", "AES"],
               ["Voting rules: Majority, Plurality, MinimumCount, MinimumPercentage, EarliestResponse...", "AES"],
               ["Quorums — automatic calculation; QUORUM() override", "AES"],
               ["Adding information to a record via a Prompt response (free-form)", "AES"],
               ["Generating events from within a WinStudio form", "AES"],
               ["Setting up external email (SMTP + Users form + send flags)", "AES"],
               ["Tracking: Event Status, Event Handler Status, Event Queue, Suspended Updates", "AES"],
               ["Restricting handlers: Event Handler form Active checkbox; Session Access As form", "AES"],
               ["Metadata synchronization — Access As ownership; sequencing; FormSync does NOT cover AES", "AES"],
               ["Event Revisions / Handler Revisions — why old metadata runs", "AES"],
               ["Determining IDO names and property names for event handler setup", "AES"]],
              [3.0*inch, W-3.0*inch]),
          sp(4)]

    e += [h2("Reports"),
          tbl(["Topic", "Document(s)"],
              [["Mongoose reporting architecture overview", "RPT"],
               ["IDO Methods / DataViews — the data supply for reports", "RPT"],
               ["Report Type forms — Form Type = Report", "RPT"],
               ["FlexLayout bands: Report Header, Page Header, Group Header, Detail, Group Footer, Page Footer, Report Footer", "RPT"],
               ["Secondary Collections — child data under parent rows", "RPT"],
               ["Sub-Reports — embedding one report inside another", "RPT"],
               ["Report Criteria forms — collecting parameters before running", "RPT"],
               ["Using standard IDO Collections on reports (no custom DataView needed)", "RPT"],
               ["Output formats: PDF, Excel, CSV, print directly", "RPT"],
               ["Report performance: NOLOCK hints, pre-joining in stored procedure", "RPT"]],
              [3.0*inch, W-3.0*inch]),
          sp(4)]

    e += [h2("Portal Forms — External User Access"),
          tbl(["Topic", "Document(s)"],
              [["Setting 'Display In Portal' on a form", "EXT"],
               ["Restricting fields visible to portal users", "EXT"],
               ["IDO-level row filtering for portal security", "EXT"],
               ["Expense Report portal workflow pattern", "EXT"]],
              [3.0*inch, W-3.0*inch]),
          hr()]

    e += [h1("Learning Path — Recommended Study Order"),
          tbl(["Order", "Document", "Why this order"],
              [["1st", "UI-NAV", "Foundation: you must understand how forms, records, and collections work before customizing them."],
               ["2nd", "CFP", "Form customization: Design Mode, components, bindings, validators — needed by every developer."],
               ["3rd", "AES", "Automation: most implementations need notification/approval workflows early. The AES does not require deep developer knowledge to set up basic workflows."],
               ["4th", "EXT", "Extension: building new entities, extending IDOs, portal forms. Requires solid understanding of the first three."],
               ["5th", "RPT", "Reporting: build reports once the data model is stable. Requires understanding of IDOs and stored procedures."]],
              [0.6*inch, 0.8*inch, W-1.4*inch]),
          hr()]

    e += [h1("Quick Lookup — 'I need to...' Scenarios"),
          tbl(["I need to...", "See document(s)"],
              [["Open a form I can't find in the Explorer", "UI-NAV — Select Form dialog (Ctrl+O)"],
               ["Understand why a field is grayed out", "UI-NAV (form modes) or CFP (Read Only / Enabled When)"],
               ["Make a field read-only for existing records", "CFP — Read Only For Existing Records property"],
               ["Add a dropdown to an existing field", "CFP — List Sources section"],
               ["Send an auto-email when a new customer is added", "AES — Notify action on IdoPostItemInsert"],
               ["Require manager approval before a PO is committed", "AES — Prompt + Fail + Suspend on IdoOnItemInsert"],
               ["Add a custom field to the Customer Order form", "EXT — UET or IDO extension, then CFP for the form component"],
               ["Build a new maintenance form for a custom table", "EXT — New Data Maintenance Wizard"],
               ["Create a report showing open POs by vendor", "RPT — DataView IDO method + Report Type form"],
               ["Let vendors submit data via browser (no Smart Client)", "EXT — Portal forms"],
               ["Move form customizations from dev to production", "CFP/EXT — FormSync (Note: AES and IDO metadata require separate steps)"],
               ["Find out why an approval notification didn't fire", "AES — Event Status form; check that Event Service is running"]],
              [2.5*inch, W-2.5*inch])]

    build(r"c:\Users\iceco\Desktop\Syteline\CSI_Master_Reference_Guide.pdf", e)


if __name__ == '__main__':
    print("Generating study note PDFs...")
    pdf_extending()
    pdf_reports()
    pdf_aes()
    pdf_master()
    print("\nAll four PDFs generated successfully.")
