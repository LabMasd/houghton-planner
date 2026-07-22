import json
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import PDFLayoutAnalyzer
from pdfminer.layout import LTChar, LAParams
from pdfminer.utils import apply_matrix_pt

class OrderDevice(PDFLayoutAnalyzer):
    def __init__(self, rsrcmgr):
        super().__init__(rsrcmgr, laparams=LAParams())
        self.ops = []
    def render_char(self, matrix, font, fontsize, scaling, rise, cid, ncs, graphicstate):
        try: text = font.to_unichr(cid)
        except Exception: text = ''
        item = LTChar(matrix, font, fontsize, scaling, rise, text, font.char_width(cid), font.char_disp(cid), ncs, graphicstate)
        col = getattr(graphicstate, 'ncolor', None)
        self.ops.append(('char', text, round(item.x0,1), round(item.x1,1), round(item.y0,1), round(item.y1,1), repr(col)))
        return item.adv
    def paint_path(self, gstate, stroke, fill, evenodd, path):
        pts = [p for op in path for p in [op[1:]] if len(op) > 1]
        xs = [p[i] for p in pts for i in range(0, len(p), 2)]
        ys = [p[i] for p in pts for i in range(1, len(p), 2)]
        if not xs: return
        # transform via ctm
        cs = [apply_matrix_pt(self.ctm, (x, y)) for x, y in zip(
            [p[i] for p in pts for i in range(0, len(p)-1, 2)],
            [p[i+1] for p in pts for i in range(0, len(p)-1, 2)])]
        X = [c[0] for c in cs]; Y = [c[1] for c in cs]
        self.ops.append(('path', 'F' if fill else 'S', round(min(X),1), round(max(X),1), round(min(Y),1), round(max(Y),1), repr(getattr(gstate,'ncolor',None)) if fill else repr(getattr(gstate,'scolor',None))))

rm = PDFResourceManager()
dev = OrderDevice(rm)
interp = PDFPageInterpreter(rm, dev)
pages_out = []
with open('houghton-timetable.pdf','rb') as f:
    for pno, page in enumerate(PDFPage.get_pages(f)):
        dev.ops = []
        interp.process_page(page)
        pages_out.append({'page': pno+1, 'ops': dev.ops})
json.dump(pages_out, open('pdf_ops.json','w'))
for p in pages_out:
    print(p['page'], len(p['ops']))
