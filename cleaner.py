# শুধু pypdf লাগে (pure Python), তাই ফোনে অফলাইনে চলে
from collections import Counter
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ContentStream, TextStringObject, ByteStringObject


def _strip(obj, text):
    if isinstance(obj, TextStringObject):
        return TextStringObject(str(obj).replace(text, ""))
    if isinstance(obj, ByteStringObject):
        return ByteStringObject(bytes(obj).replace(text.encode("latin-1", "ignore"), b""))
    return obj


def _xobjs(page):
    try:
        return page["/Resources"]["/XObject"]
    except Exception:
        return {}


def clean_pdf(inp, out, text="", images=False):
    reader = PdfReader(inp)
    writer = PdfWriter()
    counts = Counter()
    if images:
        for page in reader.pages:
            ids = set()
            for name, ref in _xobjs(page).items():
                if ref.get_object().get("/Subtype") == "/Image":
                    ids.add(ref.idnum)
            counts.update(ids)
    limit = 2 if len(reader.pages) > 1 else 1

    for page in reader.pages:
        contents = page.get_contents()
        if contents is not None:
            cs = ContentStream(contents, reader)
            ops, xo = [], _xobjs(page)
            for operands, op in cs.operations:
                if text and op == b"Tj" and operands:
                    operands[0] = _strip(operands[0], text)
                elif text and op == b"TJ" and operands:
                    operands[0] = [_strip(x, text) if not isinstance(x, (int, float)) else x
                                   for x in operands[0]]
                elif images and op == b"Do" and operands in ([operands[0]],) and operands[0] in xo:
                    raw = xo.raw_get(operands[0])
                    if (raw.get_object().get("/Subtype") == "/Image"
                            and counts[getattr(raw, "idnum", -1)] >= limit):
                        continue
                ops.append((operands, op))
            cs.operations = ops
            page.replace_contents(cs)
        writer.add_page(page)
    with open(out, "wb") as f:
        writer.write(f)
