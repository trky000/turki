\
# -*- coding: utf-8 -*-
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.utils import get_column_letter

FONT_NAME = "Arial"
BLUE = Font(name=FONT_NAME, color="0000FF")
BLUE_B = Font(name=FONT_NAME, color="0000FF", bold=True)
BLACK = Font(name=FONT_NAME, color="000000")
GREEN = Font(name=FONT_NAME, color="008000")
HDR_FONT = Font(name=FONT_NAME, bold=True, color="FFFFFF")
TITLE_FONT = Font(name=FONT_NAME, bold=True, size=16, color="1F4E78")
SUB_FONT = Font(name=FONT_NAME, bold=True, size=11, color="1F4E78")
NOTE_FONT = Font(name=FONT_NAME, italic=True, size=9, color="808080")
HDR_FILL = PatternFill("solid", fgColor="1F4E78")
SUBHDR_FILL = PatternFill("solid", fgColor="D9E1F2")
YELLOW_FILL = PatternFill("solid", fgColor="FFFF00")
GREY_FILL = PatternFill("solid", fgColor="F2F2F2")
TOTAL_FILL = PatternFill("solid", fgColor="BDD7EE")
RED_FILL = PatternFill("solid", fgColor="FFC7CE")
GREEN_FILL = PatternFill("solid", fgColor="C6EFCE")
thin = Side(style="thin", color="B7B7B7")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="right", vertical="center", wrap_text=True)  # RTL -> "right" is start
MONEY = '#,##0.00;(#,##0.00);-'
MONEY0 = '#,##0;(#,##0);-'
PCT = '0.0%'

wb = Workbook()
wb.remove(wb.active)

def new_sheet(name, tab_color=None):
    ws = wb.create_sheet(name)
    ws.sheet_view.rightToLeft = True
    ws.sheet_view.showGridLines = False
    if tab_color:
        ws.sheet_properties.tabColor = tab_color
    return ws

def title_block(ws, title, subtitle=None, span=8):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    c = ws.cell(row=1, column=1, value=title)
    c.font = TITLE_FONT
    c.alignment = LEFT
    ws.row_dimensions[1].height = 26
    r = 2
    if subtitle:
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
        c2 = ws.cell(row=2, column=1, value=subtitle)
        c2.font = NOTE_FONT
        c2.alignment = LEFT
        r = 3
    return r + 1  # first free row

def header_row(ws, row, headers, widths=None, start_col=1):
    for i, h in enumerate(headers):
        col = start_col + i
        c = ws.cell(row=row, column=col, value=h)
        c.font = HDR_FONT
        c.fill = HDR_FILL
        c.alignment = CENTER
        c.border = BORDER
        if widths:
            ws.column_dimensions[get_column_letter(col)].width = widths[i]
    ws.row_dimensions[row].height = 22
    ws.freeze_panes = ws.cell(row=row + 1, column=1).coordinate

def style_cell(ws, row, col, value=None, font=BLACK, fmt=None, fill=None, align=CENTER, border=True):
    c = ws.cell(row=row, column=col)
    if value is not None:
        c.value = value
    c.font = font
    c.alignment = align
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if border:
        c.border = BORDER
    return c

def legend(ws, row, col=1, span=6):
    ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + span - 1)
    c = ws.cell(row=row, column=col, value="دليل الألوان:  أزرق = خلية إدخال يعدّلها المستخدم  |  أسود = صيغة محسوبة تلقائياً  |  أصفر = افتراض/معلمة تدريبية رئيسية  |  رمادي = عمود مساعد للحسابات (لا يُعدّل)")
    c.font = NOTE_FONT
    c.alignment = LEFT

TODAY = "2026-01-31"
START = "2026-01-01"

# =========================================================
# 1. Company Profile
# =========================================================
ws = new_sheet("Company Profile", "1F4E78")
r = title_block(ws, "ملف الشركة - Company Profile", "نموذج تدريبي على دورة القيد المحاسبي المزدوج - أرقام وهمية لأغراض التدريب فقط")
ws.column_dimensions["A"].width = 32
ws.column_dimensions["B"].width = 30
ws.column_dimensions["C"].width = 55

rows = [
    ("اسم الشركة", "شركة التدريب المحاسبي النموذجية", BLUE, None),
    ("العملة", "ريال سعودي (SAR)", BLUE, None),
    ("تاريخ بداية المحاكاة", START, BLUE, None),
    ("تاريخ التقرير الحالي", TODAY, BLUE, None),
    ("رأس المال المدفوع", 20000000, BLUE, MONEY0),
    ("نسبة ضريبة الدخل التدريبية", 0.15, BLUE, PCT),
]
for i, (label, val, font, fmt) in enumerate(rows):
    rr = r + i
    style_cell(ws, rr, 1, label, BLACK, align=LEFT, fill=SUBHDR_FILL)
    style_cell(ws, rr, 2, val, font, fmt=fmt, fill=YELLOW_FILL, align=LEFT)
CP_TAX_ROW = r + len(rows) - 1  # نسبة ضريبة الدخل التدريبية
r2 = r + len(rows) + 1
ws.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=3)
ws.cell(row=r2, column=1, value="تعليمات التسجيل والمتابعة").font = SUB_FONT
ws.cell(row=r2, column=1).alignment = LEFT
instr = [
    "1. سجّل كل عملية مالية كقيد مزدوج في ورقة (Journal) بحيث يتساوى إجمالي المدين مع إجمالي الدائن لكل قيد.",
    "2. استخدم أرقام الحسابات المعتمدة في ورقة (COA) فقط عند التسجيل، ولا تُنشئ أرقام حسابات جديدة دون تحديثها هناك أولاً.",
    "3. تابع رصيد كل حساب أولاً بأول من ورقة (General Ledger) عبر اختيار رقم الحساب من القائمة المنسدلة.",
    "4. تأكد من توازن ورقة (Trial Balance) قبل إعداد القوائم المالية (Income Statement / Balance Sheet).",
    "5. راجع أعمار الذمم في (AR/AP) وسوّ حساب البنك في (Bank) بشكل دوري.",
    "6. سجّل أي مقترح تسوية في (Adjustments) وحدّث حالته بعد ترحيله كقيد في اليومية.",
    "7. حدّث ورقة (Training Progress) بعد إنجاز كل موضوع تدريبي، ودوّن أي حدث مهم في (Company Log).",
]
for i, line in enumerate(instr):
    rr = r2 + 1 + i
    ws.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=6)
    c = ws.cell(row=rr, column=1, value=line)
    c.font = BLACK
    c.alignment = LEFT
legend(ws, r2 + len(instr) + 2)

# =========================================================
# 2. COA
# =========================================================
ws = new_sheet("COA", "1F4E78")
r = title_block(ws, "دليل الحسابات - Chart of Accounts")
headers = ["رقم الحساب", "اسم الحساب", "نوع الحساب", "طبيعة الرصيد", "ملاحظات"]
widths = [12, 34, 16, 14, 34]
header_row(ws, r, headers, widths)
coa = [
    (1100, "البنك", "أصل", "مدين", "حساب بنكي رئيسي واحد للتدريب"),
    (1200, "العملاء (المدينون)", "أصل", "مدين", "مرتبط بتفاصيل ورقة Customers"),
    (1300, "المخزون", "أصل", "مدين", ""),
    (1400, "معدات وأجهزة", "أصل", "مدين", "أصول ثابتة - انظر Fixed Assets"),
    (1450, "مجمع إهلاك المعدات", "أصل مقابل (Contra)", "دائن", "يخصم من 1400"),
    (1500, "مصروفات مدفوعة مقدماً", "أصل", "مدين", ""),
    (1600, "ضريبة القيمة المضافة - مدخلات", "أصل", "مدين", "انظر ورقة VAT"),
    (2100, "الموردون (الدائنون)", "التزام", "دائن", "مرتبط بتفاصيل ورقة Suppliers"),
    (2200, "مصروفات مستحقة", "التزام", "دائن", ""),
    (2300, "ضريبة القيمة المضافة - مخرجات", "التزام", "دائن", "انظر ورقة VAT"),
    (2400, "ضريبة الدخل مستحقة", "التزام", "دائن", ""),
    (2500, "قرض قصير الأجل", "التزام", "دائن", ""),
    (3100, "رأس المال", "حقوق ملكية", "دائن", "رأس المال المدفوع"),
    (3200, "الأرباح المحتجزة", "حقوق ملكية", "دائن", "ترحّل إليه الأرباح عند الإقفال"),
    (3300, "مسحوبات / توزيعات أرباح", "حقوق ملكية", "مدين", ""),
    (4100, "إيرادات المبيعات", "إيراد", "دائن", ""),
    (4200, "إيرادات أخرى", "إيراد", "دائن", ""),
    (5100, "تكلفة البضاعة المباعة", "مصروف", "مدين", ""),
    (5200, "رواتب وأجور", "مصروف", "مدين", ""),
    (5300, "إيجار", "مصروف", "مدين", ""),
    (5400, "خدمات (كهرباء واتصالات)", "مصروف", "مدين", ""),
    (5500, "مصروفات تسويق", "مصروف", "مدين", ""),
    (5600, "مصروفات إدارية عامة", "مصروف", "مدين", ""),
    (5700, "إهلاك", "مصروف", "مدين", "يقابله 1450"),
    (5800, "مصروفات تمويل (فوائد بنكية)", "مصروف", "مدين", ""),
]
assert len(coa) == 25
COA_FIRST, COA_LAST = r + 1, r + len(coa)
for i, row in enumerate(coa):
    rr = r + 1 + i
    for j, val in enumerate(row):
        style_cell(ws, rr, j + 1, val, BLACK, align=LEFT if j in (1, 4) else CENTER,
                   fill=GREY_FILL if i % 2 else None)
legend(ws, COA_LAST + 2)

# =========================================================
# 3. Opening Balances
# =========================================================
ws = new_sheet("Opening Balances", "1F4E78")
r = title_block(ws, "الأرصدة الافتتاحية - Opening Balances", "بداية المحاكاة: 1 يناير 2026")
headers = ["رقم الحساب", "اسم الحساب", "مدين", "دائن"]
widths = [12, 34, 18, 18]
header_row(ws, r, headers, widths)
ob_rows = [(1100, 20000000, 0), (3100, 0, 20000000)]
OB_FIRST = r + 1
for i, (acc, dr, cr) in enumerate(ob_rows):
    rr = r + 1 + i
    style_cell(ws, rr, 1, acc, BLUE_B, fill=YELLOW_FILL)
    style_cell(ws, rr, 2, f'=IFERROR(INDEX(COA!$B${COA_FIRST}:$B${COA_LAST},MATCH(A{rr},COA!$A${COA_FIRST}:$A${COA_LAST},0)),"")', BLACK, align=LEFT)
    style_cell(ws, rr, 3, dr, BLUE_B, fmt=MONEY0, fill=YELLOW_FILL)
    style_cell(ws, rr, 4, cr, BLUE_B, fmt=MONEY0, fill=YELLOW_FILL)
OB_LAST = r + len(ob_rows)
tot_row = OB_LAST + 1
style_cell(ws, tot_row, 1, "الإجمالي", BLACK, fill=TOTAL_FILL, align=LEFT)
ws.merge_cells(start_row=tot_row, start_column=1, end_row=tot_row, end_column=2)
style_cell(ws, tot_row, 3, f"=SUM(C{OB_FIRST}:C{OB_LAST})", BLACK, fmt=MONEY0, fill=TOTAL_FILL)
style_cell(ws, tot_row, 4, f"=SUM(D{OB_FIRST}:D{OB_LAST})", BLACK, fmt=MONEY0, fill=TOTAL_FILL)
chk_row = tot_row + 1
style_cell(ws, chk_row, 1, "حالة التوازن", BLACK, align=LEFT)
ws.merge_cells(start_row=chk_row, start_column=1, end_row=chk_row, end_column=2)
style_cell(ws, chk_row, 3, f'=IF(C{tot_row}=D{tot_row},"متوازن","غير متوازن")', BLACK)
ws.merge_cells(start_row=chk_row, start_column=3, end_row=chk_row, end_column=4)
ws.conditional_formatting.add(f"C{chk_row}:D{chk_row}", CellIsRule(operator="equal", formula=['"غير متوازن"'], fill=RED_FILL))
legend(ws, chk_row + 2)

# =========================================================
# 4. Journal
# =========================================================
ws = new_sheet("Journal", "C00000")
r = title_block(ws, "دفتر اليومية - General Journal", "سجّل كل قيد بحيث يتساوى مجموع المدين مع مجموع الدائن لنفس رقم القيد", span=12)
headers = ["م", "رقم القيد", "التاريخ", "رقم الحساب", "اسم الحساب", "كود الطرف (عميل/مورد) - اختياري",
           "البيان", "مدين", "دائن", "حالة توازن القيد", "ترتيب الحساب (مساعد)", "مفتاح البحث (مساعد)"]
widths = [5, 10, 12, 12, 30, 16, 32, 16, 16, 14, 14, 14]
header_row(ws, r, headers, widths)
J_FIRST = r + 1
N_JOURNAL_ROWS = 60
J_LAST = J_FIRST + N_JOURNAL_ROWS - 1
for i in range(N_JOURNAL_ROWS):
    rr = J_FIRST + i
    style_cell(ws, rr, 1, i + 1, BLACK)
    style_cell(ws, rr, 2, None, BLUE, fill=YELLOW_FILL if i == 0 else None)
    style_cell(ws, rr, 3, None, BLUE)
    style_cell(ws, rr, 4, None, BLUE, fill=YELLOW_FILL if i == 0 else None)
    style_cell(ws, rr, 5, f'=IF(D{rr}="","",IFERROR(INDEX(COA!$B${COA_FIRST}:$B${COA_LAST},MATCH(D{rr},COA!$A${COA_FIRST}:$A${COA_LAST},0)),"# غير موجود"))', BLACK, align=LEFT)
    style_cell(ws, rr, 6, None, BLUE, align=LEFT)
    style_cell(ws, rr, 7, None, BLUE, align=LEFT)
    style_cell(ws, rr, 8, None, BLUE, fmt=MONEY)
    style_cell(ws, rr, 9, None, BLUE, fmt=MONEY)
    style_cell(ws, rr, 10, f'=IF(B{rr}="","",IF(ROUND(SUMIF($B${J_FIRST}:$B${J_LAST},B{rr},$H${J_FIRST}:$H${J_LAST})-SUMIF($B${J_FIRST}:$B${J_LAST},B{rr},$I${J_FIRST}:$I${J_LAST}),2)=0,"متوازن","غير متوازن"))', BLACK)
    style_cell(ws, rr, 11, f'=IF(D{rr}="","",COUNTIFS($D${J_FIRST}:D{rr},D{rr}))', BLACK, fill=GREY_FILL)
    style_cell(ws, rr, 12, f'=IF(D{rr}="","",D{rr}*1000+K{rr})', BLACK, fill=GREY_FILL)
ws.conditional_formatting.add(f"J{J_FIRST}:J{J_LAST}", CellIsRule(operator="equal", formula=['"غير متوازن"'], fill=RED_FILL))
dv_acc = DataValidation(type="list", formula1=f"=COA!$A${COA_FIRST}:$A${COA_LAST}", allow_blank=True)
ws.add_data_validation(dv_acc)
dv_acc.add(f"D{J_FIRST}:D{J_LAST}")
legend(ws, J_LAST + 2, span=8)
ws.merge_cells(start_row=J_LAST + 3, start_column=1, end_row=J_LAST + 3, end_column=8)
ws.cell(row=J_LAST + 3, column=1, value="مثال: قيد رقم 1 بتاريخ 2026-01-05 - إيداع دفعة مقدمة من عميل: 1100 مدين 5,000 / 4100 دائن 5,000 (رقم القيد نفسه لكل من طرفي القيد)").font = NOTE_FONT
ws.cell(row=J_LAST + 3, column=1).alignment = LEFT

# =========================================================
# 5. General Ledger
# =========================================================
ws = new_sheet("General Ledger", "1F4E78")
r = title_block(ws, "دفتر الأستاذ - General Ledger", span=6)
ws.column_dimensions["A"].width = 22
ws.column_dimensions["B"].width = 20
style_cell(ws, r, 1, "اختر رقم الحساب:", BLACK, align=LEFT, fill=SUBHDR_FILL, border=False)
SEL = r
style_cell(ws, r, 2, COA_FIRST and 1100, BLUE_B, fill=YELLOW_FILL)
dv_acc2 = DataValidation(type="list", formula1=f"=COA!$A${COA_FIRST}:$A${COA_LAST}", allow_blank=True)
ws.add_data_validation(dv_acc2)
dv_acc2.add(f"B{r}")
style_cell(ws, r + 1, 1, "اسم الحساب:", BLACK, align=LEFT, border=False)
style_cell(ws, r + 1, 2, f'=IFERROR(INDEX(COA!$B${COA_FIRST}:$B${COA_LAST},MATCH(B{SEL},COA!$A${COA_FIRST}:$A${COA_LAST},0)),"")', BLACK, align=LEFT)
style_cell(ws, r + 2, 1, "نوع الحساب:", BLACK, align=LEFT, border=False)
style_cell(ws, r + 2, 2, f'=IFERROR(INDEX(COA!$C${COA_FIRST}:$C${COA_LAST},MATCH(B{SEL},COA!$A${COA_FIRST}:$A${COA_LAST},0)),"")', BLACK, align=LEFT)
NAT_CELL_ROW = r + 3
style_cell(ws, NAT_CELL_ROW, 1, "طبيعة الرصيد:", BLACK, align=LEFT, border=False)
style_cell(ws, NAT_CELL_ROW, 2, f'=IFERROR(INDEX(COA!$D${COA_FIRST}:$D${COA_LAST},MATCH(B{SEL},COA!$A${COA_FIRST}:$A${COA_LAST},0)),"")', BLACK, align=LEFT)

sumrow = NAT_CELL_ROW + 2
headers = ["الرصيد الافتتاحي", "إجمالي حركة مدين", "إجمالي حركة دائن", "الرصيد الختامي"]
header_row(ws, sumrow, headers, [20, 20, 20, 20])
OPEN_D = f'SUMIF(\'Opening Balances\'!$A${OB_FIRST}:$A${OB_LAST},$B${SEL},\'Opening Balances\'!$C${OB_FIRST}:$C${OB_LAST})'
OPEN_C = f'SUMIF(\'Opening Balances\'!$A${OB_FIRST}:$A${OB_LAST},$B${SEL},\'Opening Balances\'!$D${OB_FIRST}:$D${OB_LAST})'
data_row = sumrow + 1
style_cell(ws, data_row, 1, f'=IF($B${NAT_CELL_ROW}="مدين",{OPEN_D}-{OPEN_C},{OPEN_C}-{OPEN_D})', BLACK, fmt=MONEY)
OPEN_BAL_CELL = f"A{data_row}"
style_cell(ws, data_row, 2, f'=SUMIF(Journal!$D${J_FIRST}:$D${J_LAST},$B${SEL},Journal!$H${J_FIRST}:$H${J_LAST})', BLACK, fmt=MONEY)
MVD_CELL = f"B{data_row}"
style_cell(ws, data_row, 3, f'=SUMIF(Journal!$D${J_FIRST}:$D${J_LAST},$B${SEL},Journal!$I${J_FIRST}:$I${J_LAST})', BLACK, fmt=MONEY)
MVC_CELL = f"C{data_row}"
style_cell(ws, data_row, 4, f'=IF($B${NAT_CELL_ROW}="مدين",{OPEN_BAL_CELL}+{MVD_CELL}-{MVC_CELL},{OPEN_BAL_CELL}+{MVC_CELL}-{MVD_CELL})', BLACK, fmt=MONEY)

det_title_row = data_row + 2
ws.merge_cells(start_row=det_title_row, start_column=1, end_row=det_title_row, end_column=6)
ws.cell(row=det_title_row, column=1, value="تفاصيل حركة الحساب المرحّلة من دفتر اليومية").font = SUB_FONT
ws.cell(row=det_title_row, column=1).alignment = LEFT
det_hdr_row = det_title_row + 1
headers = ["التاريخ", "رقم القيد", "البيان", "مدين", "دائن", "الرصيد المتحرك"]
header_row(ws, det_hdr_row, headers, [14, 12, 34, 16, 16, 18])
N_DET = 40
det_first = det_hdr_row + 1
for i in range(N_DET):
    rr = det_first + i
    rank = i + 1
    key = f'$B${SEL}*1000+{rank}'
    style_cell(ws, rr, 1, f'=IFERROR(INDEX(Journal!$C${J_FIRST}:$C${J_LAST},MATCH({key},Journal!$L${J_FIRST}:$L${J_LAST},0)),"")', BLACK)
    style_cell(ws, rr, 2, f'=IFERROR(INDEX(Journal!$B${J_FIRST}:$B${J_LAST},MATCH({key},Journal!$L${J_FIRST}:$L${J_LAST},0)),"")', BLACK)
    style_cell(ws, rr, 3, f'=IFERROR(INDEX(Journal!$G${J_FIRST}:$G${J_LAST},MATCH({key},Journal!$L${J_FIRST}:$L${J_LAST},0)),"")', BLACK, align=LEFT)
    style_cell(ws, rr, 4, f'=IFERROR(INDEX(Journal!$H${J_FIRST}:$H${J_LAST},MATCH({key},Journal!$L${J_FIRST}:$L${J_LAST},0)),"")', BLACK, fmt=MONEY)
    style_cell(ws, rr, 5, f'=IFERROR(INDEX(Journal!$I${J_FIRST}:$I${J_LAST},MATCH({key},Journal!$L${J_FIRST}:$L${J_LAST},0)),"")', BLACK, fmt=MONEY)
    cum_d = f'SUMIFS(Journal!$H${J_FIRST}:$H${J_LAST},Journal!$D${J_FIRST}:$D${J_LAST},$B${SEL},Journal!$K${J_FIRST}:$K${J_LAST},"<="&{rank})'
    cum_c = f'SUMIFS(Journal!$I${J_FIRST}:$I${J_LAST},Journal!$D${J_FIRST}:$D${J_LAST},$B${SEL},Journal!$K${J_FIRST}:$K${J_LAST},"<="&{rank})'
    style_cell(ws, rr, 6, f'=IF(D{rr}="","",IF($B${NAT_CELL_ROW}="مدين",{OPEN_BAL_CELL}+{cum_d}-{cum_c},{OPEN_BAL_CELL}+{cum_c}-{cum_d}))', BLACK, fmt=MONEY)
legend(ws, det_first + N_DET + 1, span=6)

# =========================================================
# 6. Trial Balance
# =========================================================
ws = new_sheet("Trial Balance", "1F4E78")
r = title_block(ws, "ميزان المراجعة - Trial Balance", f"كما في {TODAY}", span=9)
headers = ["رقم الحساب", "اسم الحساب", "افتتاحي مدين", "افتتاحي دائن", "حركة مدين", "حركة دائن", "ختامي مدين", "ختامي دائن"]
widths = [12, 30, 16, 16, 16, 16, 16, 16]
header_row(ws, r, headers, widths)
TB_FIRST = r + 1
for i in range(len(coa)):
    rr = TB_FIRST + i
    acc_ref = f"COA!$A${COA_FIRST + i}"
    style_cell(ws, rr, 1, f"={acc_ref}", BLACK)
    style_cell(ws, rr, 2, f"=COA!$B${COA_FIRST + i}", BLACK, align=LEFT)
    od = f"SUMIF('Opening Balances'!$A${OB_FIRST}:$A${OB_LAST},A{rr},'Opening Balances'!$C${OB_FIRST}:$C${OB_LAST})"
    oc = f"SUMIF('Opening Balances'!$A${OB_FIRST}:$A${OB_LAST},A{rr},'Opening Balances'!$D${OB_FIRST}:$D${OB_LAST})"
    md = f"SUMIF(Journal!$D${J_FIRST}:$D${J_LAST},A{rr},Journal!$H${J_FIRST}:$H${J_LAST})"
    mc = f"SUMIF(Journal!$D${J_FIRST}:$D${J_LAST},A{rr},Journal!$I${J_FIRST}:$I${J_LAST})"
    style_cell(ws, rr, 3, f"={od}", BLACK, fmt=MONEY0)
    style_cell(ws, rr, 4, f"={oc}", BLACK, fmt=MONEY0)
    style_cell(ws, rr, 5, f"={md}", BLACK, fmt=MONEY0)
    style_cell(ws, rr, 6, f"={mc}", BLACK, fmt=MONEY0)
    cv = f"(C{rr}+E{rr})-(D{rr}+F{rr})"
    style_cell(ws, rr, 7, f"=IF({cv}>=0,{cv},0)", BLACK, fmt=MONEY0)
    style_cell(ws, rr, 8, f"=IF({cv}<0,-({cv}),0)", BLACK, fmt=MONEY0)
TB_LAST = TB_FIRST + len(coa) - 1
tot_row = TB_LAST + 1
style_cell(ws, tot_row, 1, "الإجمالي", BLACK, fill=TOTAL_FILL, align=LEFT)
ws.merge_cells(start_row=tot_row, start_column=1, end_row=tot_row, end_column=2)
for col in range(3, 9):
    letter = get_column_letter(col)
    style_cell(ws, tot_row, col, f"=SUM({letter}{TB_FIRST}:{letter}{TB_LAST})", BLACK, fmt=MONEY0, fill=TOTAL_FILL)
chk_row = tot_row + 1
style_cell(ws, chk_row, 1, "حالة التوازن (افتتاحي/حركة/ختامي)", BLACK, align=LEFT)
ws.merge_cells(start_row=chk_row, start_column=1, end_row=chk_row, end_column=2)
chk_formula = f'=IF(AND(ROUND(C{tot_row}-D{tot_row},2)=0,ROUND(E{tot_row}-F{tot_row},2)=0,ROUND(G{tot_row}-H{tot_row},2)=0),"متوازن","غير متوازن")'
style_cell(ws, chk_row, 3, chk_formula, BLACK)
ws.merge_cells(start_row=chk_row, start_column=3, end_row=chk_row, end_column=8)
ws.conditional_formatting.add(f"C{chk_row}", CellIsRule(operator="equal", formula=['"غير متوازن"'], fill=RED_FILL))
legend(ws, chk_row + 2, span=8)

# =========================================================
# 7. Customers
# =========================================================
ws = new_sheet("Customers", "1F4E78")
r = title_block(ws, "العملاء - Customers", span=6)
headers = ["الرمز", "اسم العميل", "رقم الهاتف", "أجل السداد الافتراضي (يوم)", "ملاحظات"]
widths = [10, 26, 16, 22, 26]
header_row(ws, r, headers, widths)
CUST_FIRST = r + 1
customers = [f"عميل تدريبي رقم {i+1}" for i in range(10)]
for i in range(10):
    rr = CUST_FIRST + i
    style_cell(ws, rr, 1, f"C{i+1:03d}", BLUE_B, fill=YELLOW_FILL if i == 0 else None)
    style_cell(ws, rr, 2, customers[i], BLUE, align=LEFT)
    style_cell(ws, rr, 3, "05xxxxxxxx", BLUE)
    style_cell(ws, rr, 4, 30, BLUE, fmt="0")
    style_cell(ws, rr, 5, "", BLACK, align=LEFT)
CUST_LAST = CUST_FIRST + 9
legend(ws, CUST_LAST + 2, span=5)

# =========================================================
# 8. Suppliers
# =========================================================
ws = new_sheet("Suppliers", "1F4E78")
r = title_block(ws, "الموردون - Suppliers", span=6)
headers = ["الرمز", "اسم المورد", "التخصص", "أجل السداد الافتراضي (يوم)", "ملاحظات"]
widths = [10, 26, 20, 22, 26]
header_row(ws, r, headers, widths)
SUP_FIRST = r + 1
suppliers = [
    ("مورد المعدات", "معدات"),
    ("مورد الأجهزة", "أجهزة"),
    ("مورد خدمات الربط والاتصالات", "ربط واتصالات"),
    ("المؤجّر - عقد الإيجار", "إيجار"),
    ("مورد الخدمات العامة", "خدمات"),
]
for i, (name, spec) in enumerate(suppliers):
    rr = SUP_FIRST + i
    style_cell(ws, rr, 1, f"S{i+1:03d}", BLUE_B, fill=YELLOW_FILL if i == 0 else None)
    style_cell(ws, rr, 2, name, BLUE, align=LEFT)
    style_cell(ws, rr, 3, spec, BLUE, align=LEFT)
    style_cell(ws, rr, 4, 30, BLUE, fmt="0")
    style_cell(ws, rr, 5, "", BLACK, align=LEFT)
SUP_LAST = SUP_FIRST + len(suppliers) - 1
legend(ws, SUP_LAST + 2, span=5)

# =========================================================
# 9. AR / AP
# =========================================================
ws = new_sheet("AR_AP", "1F4E78")
ws.title = "AR AP"
r = title_block(ws, "أعمار الذمم - العملاء والموردون (AR / AP)", span=6)
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
ws.cell(row=r, column=1, value="ذمم العملاء (مدينون)").font = SUB_FONT
ws.cell(row=r, column=1).alignment = LEFT
r += 1
headers = ["الرمز", "اسم العميل", "مدين", "دائن", "الرصيد"]
widths = [10, 26, 16, 16, 16]
header_row(ws, r, headers, widths)
AR_FIRST = r + 1
for i in range(10):
    rr = AR_FIRST + i
    style_cell(ws, rr, 1, f"=Customers!A{CUST_FIRST + i}", BLACK)
    style_cell(ws, rr, 2, f"=Customers!B{CUST_FIRST + i}", BLACK, align=LEFT)
    style_cell(ws, rr, 3, f"=SUMIFS(Journal!$H${J_FIRST}:$H${J_LAST},Journal!$F${J_FIRST}:$F${J_LAST},A{rr})", BLACK, fmt=MONEY0)
    style_cell(ws, rr, 4, f"=SUMIFS(Journal!$I${J_FIRST}:$I${J_LAST},Journal!$F${J_FIRST}:$F${J_LAST},A{rr})", BLACK, fmt=MONEY0)
    style_cell(ws, rr, 5, f"=C{rr}-D{rr}", BLACK, fmt=MONEY0)
AR_LAST = AR_FIRST + 9
tot1 = AR_LAST + 1
style_cell(ws, tot1, 1, "الإجمالي", BLACK, fill=TOTAL_FILL, align=LEFT)
ws.merge_cells(start_row=tot1, start_column=1, end_row=tot1, end_column=2)
for col in (3, 4, 5):
    letter = get_column_letter(col)
    style_cell(ws, tot1, col, f"=SUM({letter}{AR_FIRST}:{letter}{AR_LAST})", BLACK, fmt=MONEY0, fill=TOTAL_FILL)

r2 = tot1 + 2
ws.merge_cells(start_row=r2, start_column=1, end_row=r2, end_column=5)
ws.cell(row=r2, column=1, value="ذمم الموردين (دائنون)").font = SUB_FONT
ws.cell(row=r2, column=1).alignment = LEFT
r2 += 1
header_row(ws, r2, headers, widths)
AP_FIRST = r2 + 1
for i in range(len(suppliers)):
    rr = AP_FIRST + i
    style_cell(ws, rr, 1, f"=Suppliers!A{SUP_FIRST + i}", BLACK)
    style_cell(ws, rr, 2, f"=Suppliers!B{SUP_FIRST + i}", BLACK, align=LEFT)
    style_cell(ws, rr, 3, f"=SUMIFS(Journal!$H${J_FIRST}:$H${J_LAST},Journal!$F${J_FIRST}:$F${J_LAST},A{rr})", BLACK, fmt=MONEY0)
    style_cell(ws, rr, 4, f"=SUMIFS(Journal!$I${J_FIRST}:$I${J_LAST},Journal!$F${J_FIRST}:$F${J_LAST},A{rr})", BLACK, fmt=MONEY0)
    style_cell(ws, rr, 5, f"=D{rr}-C{rr}", BLACK, fmt=MONEY0)
AP_LAST = AP_FIRST + len(suppliers) - 1
tot2 = AP_LAST + 1
style_cell(ws, tot2, 1, "الإجمالي", BLACK, fill=TOTAL_FILL, align=LEFT)
ws.merge_cells(start_row=tot2, start_column=1, end_row=tot2, end_column=2)
for col in (3, 4, 5):
    letter = get_column_letter(col)
    style_cell(ws, tot2, col, f"=SUM({letter}{AP_FIRST}:{letter}{AP_LAST})", BLACK, fmt=MONEY0, fill=TOTAL_FILL)
legend(ws, tot2 + 2, span=5)

# =========================================================
# 10. Bank
# =========================================================
ws = new_sheet("Bank", "1F4E78")
r = title_block(ws, "البنك - Bank Reconciliation", f"حساب 1100 - كما في {TODAY}", span=5)
ws.column_dimensions["A"].width = 34
ws.column_dimensions["B"].width = 20
style_cell(ws, r, 1, "رصيد الدفاتر (حساب 1100)", BLACK, align=LEFT, border=False)
style_cell(ws, r, 2, f"='Trial Balance'!G{TB_FIRST}-'Trial Balance'!H{TB_FIRST}", BLACK, fmt=MONEY0)
BANK_BOOKS = f"B{r}"
style_cell(ws, r + 1, 1, "رصيد كشف الحساب البنكي", BLACK, align=LEFT, border=False)
style_cell(ws, r + 1, 2, 20000000, BLUE_B, fmt=MONEY0, fill=YELLOW_FILL)
BANK_STMT = f"B{r+1}"
style_cell(ws, r + 2, 1, "زائد: إيداعات بالطريق (لم تظهر بالكشف)", BLACK, align=LEFT, border=False)
style_cell(ws, r + 2, 2, 0, BLUE, fmt=MONEY0)
DEP_TRANSIT = f"B{r+2}"
style_cell(ws, r + 3, 1, "ناقص: مدفوعات معلقة (لم تظهر بالكشف)", BLACK, align=LEFT, border=False)
style_cell(ws, r + 3, 2, 0, BLUE, fmt=MONEY0)
OUT_PAY = f"B{r+3}"
style_cell(ws, r + 4, 1, "رصيد الدفاتر المعدّل", BLACK, align=LEFT, border=False, fill=SUBHDR_FILL)
style_cell(ws, r + 4, 2, f"={BANK_BOOKS}+{DEP_TRANSIT}-{OUT_PAY}", BLACK, fmt=MONEY0, fill=SUBHDR_FILL)
ADJ_BOOKS = f"B{r+4}"
style_cell(ws, r + 5, 1, "فرق المطابقة (يجب أن يكون صفراً)", BLACK, align=LEFT, border=False)
style_cell(ws, r + 5, 2, f"={ADJ_BOOKS}-{BANK_STMT}", BLACK, fmt=MONEY0)
DIFF_CELL = f"B{r+5}"
ws.conditional_formatting.add(DIFF_CELL, CellIsRule(operator="notEqual", formula=["0"], fill=RED_FILL))
ws.conditional_formatting.add(DIFF_CELL, CellIsRule(operator="equal", formula=["0"], fill=GREEN_FILL))
legend(ws, r + 7, span=5)

# =========================================================
# 11. VAT
# =========================================================
ws = new_sheet("VAT", "1F4E78")
r = title_block(ws, "ضريبة القيمة المضافة - VAT", span=5)
ws.column_dimensions["A"].width = 36
ws.column_dimensions["B"].width = 20
style_cell(ws, r, 1, "المعدل التدريبي لضريبة القيمة المضافة", BLACK, align=LEFT, border=False)
style_cell(ws, r, 2, 0.15, BLUE_B, fmt=PCT, fill=YELLOW_FILL)
style_cell(ws, r + 1, 1, "ضريبة المدخلات (حساب 1600)", BLACK, align=LEFT, border=False)
row_1600 = TB_FIRST + 6
style_cell(ws, r + 1, 2, f"='Trial Balance'!G{row_1600}-'Trial Balance'!H{row_1600}", BLACK, fmt=MONEY0)
style_cell(ws, r + 2, 1, "ضريبة المخرجات (حساب 2300)", BLACK, align=LEFT, border=False)
row_2300 = TB_FIRST + 9
style_cell(ws, r + 2, 2, f"='Trial Balance'!H{row_2300}-'Trial Balance'!G{row_2300}", BLACK, fmt=MONEY0)
style_cell(ws, r + 3, 1, "صافي الفرق (مخرجات - مدخلات = مستحق للسداد)", BLACK, align=LEFT, border=False, fill=SUBHDR_FILL)
style_cell(ws, r + 3, 2, f"=B{r+2}-B{r+1}", BLACK, fmt=MONEY0, fill=SUBHDR_FILL)
legend(ws, r + 5, span=5)

# =========================================================
# 12. Fixed Assets
# =========================================================
ws = new_sheet("Fixed Assets", "1F4E78")
r = title_block(ws, "الأصول الثابتة - Fixed Assets", "لا توجد أصول مضافة عند بداية المحاكاة", span=9)
headers = ["كود الأصل", "اسم الأصل", "تاريخ الشراء", "التكلفة", "العمر الإنتاجي (سنوات)", "طريقة الإهلاك", "الإهلاك الشهري", "مجمع الإهلاك", "صافي القيمة الدفترية"]
widths = [10, 24, 14, 16, 16, 16, 16, 16, 18]
header_row(ws, r, headers, widths)
FA_FIRST = r + 1
N_FA = 15
for i in range(N_FA):
    rr = FA_FIRST + i
    style_cell(ws, rr, 1, None, BLUE)
    style_cell(ws, rr, 2, None, BLUE, align=LEFT)
    style_cell(ws, rr, 3, None, BLUE)
    style_cell(ws, rr, 4, None, BLUE, fmt=MONEY0)
    style_cell(ws, rr, 5, None, BLUE, fmt="0")
    style_cell(ws, rr, 6, None, BLUE, align=LEFT)
    style_cell(ws, rr, 7, f'=IF(OR(D{rr}="",E{rr}="",E{rr}=0),"",D{rr}/(E{rr}*12))', BLACK, fmt=MONEY0)
    style_cell(ws, rr, 8, None, BLUE, fmt=MONEY0)
    style_cell(ws, rr, 9, f'=IF(D{rr}="","",D{rr}-IF(H{rr}="",0,H{rr}))', BLACK, fmt=MONEY0)
FA_LAST = FA_FIRST + N_FA - 1
legend(ws, FA_LAST + 2, span=9)

# =========================================================
# 13. Adjustments
# =========================================================
ws = new_sheet("Adjustments", "1F4E78")
r = title_block(ws, "التسويات - Adjustments", span=7)
headers = ["رقم التسوية", "التاريخ", "الوصف", "المستند المرجعي", "الحالة", "رقم القيد المرتبط", "ملاحظات"]
widths = [12, 14, 30, 20, 16, 16, 26]
header_row(ws, r, headers, widths)
ADJ_FIRST = r + 1
N_ADJ = 15
for i in range(N_ADJ):
    rr = ADJ_FIRST + i
    style_cell(ws, rr, 1, i + 1, BLACK)
    style_cell(ws, rr, 2, None, BLUE)
    style_cell(ws, rr, 3, None, BLUE, align=LEFT)
    style_cell(ws, rr, 4, None, BLUE, align=LEFT)
    style_cell(ws, rr, 5, None, BLUE)
    style_cell(ws, rr, 6, None, BLUE)
    style_cell(ws, rr, 7, None, BLACK, align=LEFT)
ADJ_LAST = ADJ_FIRST + N_ADJ - 1
dv_status = DataValidation(type="list", formula1='"قيد الانتظار,معتمد,مرفوض"', allow_blank=True)
ws.add_data_validation(dv_status)
dv_status.add(f"E{ADJ_FIRST}:E{ADJ_LAST}")
ws.conditional_formatting.add(f"E{ADJ_FIRST}:E{ADJ_LAST}", CellIsRule(operator="equal", formula=['"معتمد"'], fill=GREEN_FILL))
legend(ws, ADJ_LAST + 2, span=7)

# =========================================================
# 14. Income Statement
# =========================================================
ws = new_sheet("Income Statement", "1F4E78")
r = title_block(ws, "قائمة الدخل - Income Statement", f"للفترة من {START} إلى {TODAY}", span=4)
ws.column_dimensions["A"].width = 36
ws.column_dimensions["B"].width = 20
rev_cr = f"SUMIFS(Journal!$I${J_FIRST}:$I${J_LAST},Journal!$D${J_FIRST}:$D${J_LAST},\">=4100\",Journal!$D${J_FIRST}:$D${J_LAST},\"<5000\")"
rev_dr = f"SUMIFS(Journal!$H${J_FIRST}:$H${J_LAST},Journal!$D${J_FIRST}:$D${J_LAST},\">=4100\",Journal!$D${J_FIRST}:$D${J_LAST},\"<5000\")"
exp_dr = f"SUMIFS(Journal!$H${J_FIRST}:$H${J_LAST},Journal!$D${J_FIRST}:$D${J_LAST},\">=5100\",Journal!$D${J_FIRST}:$D${J_LAST},\"<6000\")"
exp_cr = f"SUMIFS(Journal!$I${J_FIRST}:$I${J_LAST},Journal!$D${J_FIRST}:$D${J_LAST},\">=5100\",Journal!$D${J_FIRST}:$D${J_LAST},\"<6000\")"
style_cell(ws, r, 1, "إجمالي الإيرادات", BLACK, align=LEFT, border=False)
style_cell(ws, r, 2, f"={rev_cr}-{rev_dr}", BLACK, fmt=MONEY0)
REV_CELL = f"B{r}"
style_cell(ws, r + 1, 1, "إجمالي المصروفات", BLACK, align=LEFT, border=False)
style_cell(ws, r + 1, 2, f"={exp_dr}-{exp_cr}", BLACK, fmt=MONEY0)
EXP_CELL = f"B{r+1}"
style_cell(ws, r + 2, 1, "صافي الربح قبل الضريبة", BLACK, align=LEFT, border=False, fill=SUBHDR_FILL)
style_cell(ws, r + 2, 2, f"={REV_CELL}-{EXP_CELL}", BLACK, fmt=MONEY0, fill=SUBHDR_FILL)
EBT_CELL = f"B{r+2}"
style_cell(ws, r + 3, 1, "ضريبة الدخل (بمعدل ورقة Company Profile)", BLACK, align=LEFT, border=False)
style_cell(ws, r + 3, 2, f"=IF({EBT_CELL}>0,{EBT_CELL}*'Company Profile'!B{CP_TAX_ROW},0)", BLACK, fmt=MONEY0)
TAX_CELL = f"B{r+3}"
style_cell(ws, r + 4, 1, "صافي الربح بعد الضريبة", BLACK, align=LEFT, border=False, fill=TOTAL_FILL)
style_cell(ws, r + 4, 2, f"={EBT_CELL}-{TAX_CELL}", BLACK, fmt=MONEY0, fill=TOTAL_FILL)
# ملاحظة: يُنقل صافي الربح قبل الضريبة (وليس بعدها) إلى قائمة المركز المالي كحقوق ملكية،
# لأن الضريبة هنا مجرد تقدير؛ تصبح مستحقة فعلياً فقط بعد ترحيل قيد تسوية إلى حساب 2400
# (انظر ورقة Adjustments) يعكسها Balance Sheet تلقائياً بعد ذلك.
NI_CELL = f"'Income Statement'!B{r+2}"
ws.merge_cells(start_row=r + 6, start_column=1, end_row=r + 6, end_column=4)
note_cell = ws.cell(row=r + 6, column=1, value="ملاحظة: تُعرض الضريبة هنا كتقدير فقط. تصبح مستحقة فعلياً على قائمة المركز المالي بعد تسجيل قيد تسوية بضريبة الدخل (Dr مصروف الضريبة / Cr 2400) في ورقة Journal.")
note_cell.font = NOTE_FONT
note_cell.alignment = LEFT
legend(ws, r + 8, span=4)

# =========================================================
# 15. Balance Sheet
# =========================================================
ws = new_sheet("Balance Sheet", "1F4E78")
r = title_block(ws, "قائمة المركز المالي - Balance Sheet", f"كما في {TODAY}", span=4)
ws.column_dimensions["A"].width = 36
ws.column_dimensions["B"].width = 20
assets_d = f"SUMIFS('Trial Balance'!$G${TB_FIRST}:$G${TB_LAST},'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\">=1000\",'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\"<2000\")"
assets_c = f"SUMIFS('Trial Balance'!$H${TB_FIRST}:$H${TB_LAST},'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\">=1000\",'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\"<2000\")"
liab_c = f"SUMIFS('Trial Balance'!$H${TB_FIRST}:$H${TB_LAST},'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\">=2000\",'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\"<3000\")"
liab_d = f"SUMIFS('Trial Balance'!$G${TB_FIRST}:$G${TB_LAST},'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\">=2000\",'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\"<3000\")"
eq_c = f"SUMIFS('Trial Balance'!$H${TB_FIRST}:$H${TB_LAST},'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\">=3000\",'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\"<4000\")"
eq_d = f"SUMIFS('Trial Balance'!$G${TB_FIRST}:$G${TB_LAST},'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\">=3000\",'Trial Balance'!$A${TB_FIRST}:$A${TB_LAST},\"<4000\")"
style_cell(ws, r, 1, "إجمالي الأصول", BLACK, align=LEFT, border=False, fill=SUBHDR_FILL)
style_cell(ws, r, 2, f"={assets_d}-{assets_c}", BLACK, fmt=MONEY0, fill=SUBHDR_FILL)
ASSETS_CELL = f"B{r}"
style_cell(ws, r + 1, 1, "إجمالي الالتزامات", BLACK, align=LEFT, border=False)
style_cell(ws, r + 1, 2, f"={liab_c}-{liab_d}", BLACK, fmt=MONEY0)
LIAB_CELL = f"B{r+1}"
style_cell(ws, r + 2, 1, "حقوق الملكية (رأس المال والأرباح المحتجزة)", BLACK, align=LEFT, border=False)
style_cell(ws, r + 2, 2, f"={eq_c}-{eq_d}", BLACK, fmt=MONEY0)
EQ_BASE_CELL = f"B{r+2}"
style_cell(ws, r + 3, 1, "زائد: صافي ربح الفترة الحالية (قبل تسوية الضريبة)", BLACK, align=LEFT, border=False)
style_cell(ws, r + 3, 2, f"={NI_CELL}", GREEN, fmt=MONEY0)
NI_PERIOD_CELL = f"B{r+3}"
style_cell(ws, r + 4, 1, "إجمالي حقوق الملكية", BLACK, align=LEFT, border=False, fill=SUBHDR_FILL)
style_cell(ws, r + 4, 2, f"={EQ_BASE_CELL}+{NI_PERIOD_CELL}", BLACK, fmt=MONEY0, fill=SUBHDR_FILL)
TOTAL_EQ_CELL = f"B{r+4}"
style_cell(ws, r + 5, 1, "إجمالي الالتزامات وحقوق الملكية", BLACK, align=LEFT, border=False, fill=TOTAL_FILL)
style_cell(ws, r + 5, 2, f"={LIAB_CELL}+{TOTAL_EQ_CELL}", BLACK, fmt=MONEY0, fill=TOTAL_FILL)
LE_CELL = f"B{r+5}"
style_cell(ws, r + 6, 1, "حالة التوازن (الأصول = الالتزامات + حقوق الملكية)", BLACK, align=LEFT, border=False)
style_cell(ws, r + 6, 2, f'=IF(ROUND({ASSETS_CELL}-{LE_CELL},2)=0,"متوازن","غير متوازن")', BLACK)
ws.conditional_formatting.add(f"B{r+6}", CellIsRule(operator="equal", formula=['"غير متوازن"'], fill=RED_FILL))
legend(ws, r + 8, span=4)

# =========================================================
# 16. Training Progress
# =========================================================
ws = new_sheet("Training Progress", "1F4E78")
r = title_block(ws, "تقدم التدريب - Training Progress", span=6)
headers = ["م", "الموضوع التدريبي", "الحالة", "تاريخ البدء", "تاريخ الانتهاء", "ملاحظات"]
widths = [5, 40, 16, 14, 14, 26]
header_row(ws, r, headers, widths)
topics = [
    "1. أساسيات المدين والدائن وقاعدة القيد المزدوج",
    "2. تسجيل القيود في دفتر اليومية (Journal)",
    "3. الترحيل إلى دفتر الأستاذ وإعداد ميزان المراجعة",
    "4. العملاء والموردون وأعمار الذمم (AR/AP)",
    "5. مطابقة البنك، ضريبة القيمة المضافة، والأصول الثابتة",
    "6. التسويات الجردية وإقفال الحسابات وإعداد القوائم المالية",
]
TP_FIRST = r + 1
for i, topic in enumerate(topics):
    rr = TP_FIRST + i
    style_cell(ws, rr, 1, i + 1, BLACK)
    style_cell(ws, rr, 2, topic, BLACK, align=LEFT)
    style_cell(ws, rr, 3, "لم يبدأ", BLUE)
    style_cell(ws, rr, 4, None, BLUE)
    style_cell(ws, rr, 5, None, BLUE)
    style_cell(ws, rr, 6, "", BLACK, align=LEFT)
TP_LAST = TP_FIRST + len(topics) - 1
dv_tp = DataValidation(type="list", formula1='"لم يبدأ,قيد التنفيذ,مكتمل"', allow_blank=True)
ws.add_data_validation(dv_tp)
dv_tp.add(f"C{TP_FIRST}:C{TP_LAST}")
ws.conditional_formatting.add(f"C{TP_FIRST}:C{TP_LAST}", CellIsRule(operator="equal", formula=['"مكتمل"'], fill=GREEN_FILL))
ws.conditional_formatting.add(f"C{TP_FIRST}:C{TP_LAST}", CellIsRule(operator="equal", formula=['"قيد التنفيذ"'], fill=YELLOW_FILL))
legend(ws, TP_LAST + 2, span=6)

# =========================================================
# 17. Company Log
# =========================================================
ws = new_sheet("Company Log", "1F4E78")
r = title_block(ws, "سجل الشركة - Company Log", span=5)
headers = ["التاريخ", "الإصدار", "الإجراء", "الوصف", "الخطوة التالية"]
widths = [14, 10, 24, 40, 40]
header_row(ws, r, headers, widths)
rr = r + 1
style_cell(ws, rr, 1, START, BLACK)
style_cell(ws, rr, 2, "1.0", BLACK)
style_cell(ws, rr, 3, "تأسيس الملف", BLACK, align=LEFT)
style_cell(ws, rr, 4, "إنشاء نموذج المحاكاة المحاسبية التدريبي بكامل أوراقه (دليل الحسابات، اليومية، الأستاذ، القوائم المالية، والعملاء والموردون).", BLACK, align=LEFT)
style_cell(ws, rr, 5, "بدء الحالة التدريبية الأولى ومناقشة المستندات المؤيدة للقيود.", BLACK, align=LEFT)
ws.row_dimensions[rr].height = 42
for i in range(1, 20):
    rr2 = rr + i
    for c in range(1, 6):
        style_cell(ws, rr2, c, None, BLACK, align=LEFT)
legend(ws, rr + 21, span=5)

# order sheets per spec
order = ["Company Profile", "COA", "Opening Balances", "Journal", "General Ledger", "Trial Balance",
         "Customers", "Suppliers", "AR AP", "Bank", "VAT", "Fixed Assets", "Adjustments",
         "Income Statement", "Balance Sheet", "Training Progress", "Company Log"]
wb._sheets = [wb[name] for name in order]
wb.active = 0

OUT = "/tmp/claude-0/-home-user-turki/e721fdb4-a640-5a77-9976-42bce4895f00/scratchpad/build/Accounting_Simulation_Training_Model.xlsx"
wb.save(OUT)
print("saved", OUT)
