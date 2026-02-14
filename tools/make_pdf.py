#!/usr/bin/env python3
from pathlib import Path

INPUT = Path('manuscript.tex')
OUTPUT = Path('manuscript.pdf')

PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT = 50
TOP = 740
FONT_SIZE = 9
LEADING = 11
CHARS_PER_LINE = 95
LINES_PER_PAGE = 62

def esc(s: str) -> str:
    return s.replace('\\', r'\\').replace('(', r'\(').replace(')', r'\)')

def wrap_line(line: str, width: int):
    if not line:
        return ['']
    out = []
    while len(line) > width:
        cut = line.rfind(' ', 0, width)
        if cut <= 0:
            cut = width
        out.append(line[:cut])
        line = line[cut:].lstrip()
    out.append(line)
    return out

def build_pdf(pages_text):
    objs = []

    # 1: Catalog, 2: Pages
    objs.append('<< /Type /Catalog /Pages 2 0 R >>')

    # placeholders for page objects and content streams
    page_objs = []
    content_objs = []

    for page_lines in pages_text:
        text_cmds = [f'BT /F1 {FONT_SIZE} Tf {LEFT} {TOP} Td {LEADING} TL']
        first = True
        for ln in page_lines:
            if first:
                text_cmds.append(f'({esc(ln)}) Tj')
                first = False
            else:
                text_cmds.append(f'T* ({esc(ln)}) Tj')
        text_cmds.append('ET')
        stream = '\n'.join(text_cmds).encode('latin-1', errors='replace')
        content_objs.append(stream)

    # object numbering
    # 1 catalog, 2 pages, 3 font, then alternating page/content
    font_obj_num = 3
    current_num = 4
    page_numbers = []
    content_numbers = []
    for _ in pages_text:
        page_numbers.append(current_num)
        content_numbers.append(current_num + 1)
        current_num += 2

    kids = ' '.join(f'{n} 0 R' for n in page_numbers)
    objs.append(f'<< /Type /Pages /Count {len(pages_text)} /Kids [{kids}] >>')
    objs.append('<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>')

    for i, page_lines in enumerate(pages_text):
        pnum = page_numbers[i]
        cnum = content_numbers[i]
        page_obj = (
            f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] '
            f'/Resources << /Font << /F1 {font_obj_num} 0 R >> >> /Contents {cnum} 0 R >>'
        )
        objs.append(page_obj)

        stream = content_objs[i]
        content_obj = f'<< /Length {len(stream)} >>\nstream\n'.encode('latin-1') + stream + b'\nendstream'
        objs.append(content_obj)

    out = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n')
    xref = [0]
    for idx, obj in enumerate(objs, start=1):
        xref.append(len(out))
        out.extend(f'{idx} 0 obj\n'.encode('latin-1'))
        if isinstance(obj, bytes):
            out.extend(obj)
            out.extend(b'\n')
        else:
            out.extend(obj.encode('latin-1'))
            out.extend(b'\n')
        out.extend(b'endobj\n')

    xref_start = len(out)
    out.extend(f'xref\n0 {len(xref)}\n'.encode('latin-1'))
    out.extend(b'0000000000 65535 f \n')
    for off in xref[1:]:
        out.extend(f'{off:010d} 00000 n \n'.encode('latin-1'))

    out.extend(
        f'trailer\n<< /Size {len(xref)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n'.encode('latin-1')
    )
    return out


def main():
    text = INPUT.read_text(encoding='utf-8', errors='replace').splitlines()
    wrapped = []
    for line in text:
        wrapped.extend(wrap_line(line, CHARS_PER_LINE))
    pages = [wrapped[i:i+LINES_PER_PAGE] for i in range(0, len(wrapped), LINES_PER_PAGE)]
    pdf = build_pdf(pages)
    OUTPUT.write_bytes(pdf)
    print(f'Wrote {OUTPUT} with {len(pages)} pages')

if __name__ == '__main__':
    main()
