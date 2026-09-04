from http.server import BaseHTTPRequestHandler
import json
import re

# ইউনিকোড ও বিজয় ম্যাপিং তালিকা
MAP_PAIRS = [
    ("c&iv", "প্রা"), ("c&†i", "প্রে"), ("cÖ", "প্র"), ("Î", "ত্র"), ("MÖ", "গ্র"),
    ("`Ö", "দ্র"), ("eÖ", "ব্র"), ("fÖ", "ভ্র"), ("kÖ", "শ্র"), ("mÖ", "স্র"),
    ("nÖ", "হ্র"), ("µ", "ক্র"), ("å", "ভ্র"),

    ("ÿ¥", "ক্ষ্ম"), ("ÿ", "ক্ষ"), ("Á", "জ্ঞ"), ("ò", "ষ্ণ"), ("Â", "ঞ্চ"),
    ("Ã", "ঞ্ছ"), ("Ä", "ঞ্জ"), ("Å", "ঞ্ঝ"), ("¼", "ঙ্ক"), ("½", "ঙ্খ"),
    ("¾", "ঙ্গ"), ("¿", "ঙ্ঘ"), ("”", "চ্চ"), ("•", "চ্ছ"), ("À", "জ্জ"),
    ("Æ", "ট্ট"), ("È", "ণ্ট"), ("É", "ণ্ঠ"), ("Ð", "ণ্ড"), ("Ý", "ণ্ণ"),
    ("Ë¡", "ত্ত্ব"), ("Ë", "ত্ত"), ("Ì", "ত্থ"), ("Í", "ত্ম"), ("Ï", "দ্দ"),
    ("×", "দ্ধ"), ("Ø", "দ্ব"), ("Ù", "দ্ম"), ("Ú", "ন্ঠ"), ("Û", "ন্ড"),
    ("šÍ", "ন্ত্ব"), ("š’", "ন্থ"), ("š^", "ন্ব"), ("š", "ন্ত"), ("›", "ন্দ"),
    ("œ", "ন্ধ"), ("bœ", "ন্ন"), ("Þ", "প্ট"), ("ß", "প্ত"), ("cœ", "প্ন"),
    ("à", "প্প"), ("cø", "প্ল"), ("á", "প্স"), ("ã", "ব্দ"), ("ä", "ব্ধ"),
    ("eŸ", "ব্ব"), ("eø", "ব্ল"), ("gœ", "ম্ন"), ("¤ú", "ম্প"), ("ç", "ম্ফ"),
    ("¤^", "ম্ব"), ("¤¢", "ম্ভ"), ("¤§", "ম্ম"), ("¤ø", "ম্ল"), ("é", "ল্ক"),
    ("ê", "ল্গ"), ("ë", "ল্ট"), ("ì", "ল্ড"), ("í", "ল্প"), ("î", "ল্ফ"),
    ("j¡", "ল্ব"), ("j§", "ল্ম"), ("jø", "ল্ল"), ("ð", "শ্চ"), ("ñ", "শ্ন"),
    ("kœ", "শ্ন"), ("k¦", "শ্ব"), ("k¥", "শ্ম"), ("kø", "শ্ল"), ("ó", "ষ্ট"),
    ("ô", "ষ্ঠ"), ("®ú", "ষ্প"), ("®§", "ষ্ম"), ("÷", "স্ট"), ("ù", "স্ফ"),
    ("¯Í", "স্ত্ব"), ("¯’", "স্থ"), ("mœ", "স্ন"), ("¯ú", "স্প"), ("¯^", "স্ব"),
    ("¯§", "স্ম"), ("mø", "স্ল"), ("¯", "স্ত"), ("nè", "হ্ণ"), ("ý", "হ্ন"),
    ("þ", "হ্ম"), ("n¬", "হ্ল"), ("nŸ", "হ্ব"),

    ("Av", "আ"), ("A", "অ"), ("B", "ই"), ("C", "ঈ"), ("D", "উ"), ("E", "ঊ"),
    ("F", "ঋ"), ("G", "এ"), ("H", "ঐ"), ("I", "ও"), ("J", "ঔ"),

    ("K", "ক"), ("L", "খ"), ("M", "গ"), ("N", "ঘ"), ("O", "ঙ"),
    ("P", "চ"), ("Q", "ছ"), ("R", "জ"), ("S", "ঝ"), ("T", "ঞ"),
    ("U", "ট"), ("V", "ঠ"), ("W", "ড"), ("X", "ঢ"), ("Y", "ণ"),
    ("Z", "ত"), ("_", "থ"), ("`", "দ"), ("a", "ধ"), ("b", "ন"),
    ("c", "প"), ("d", "ফ"), ("e", "ব"), ("f", "ভ"), ("g", "ম"),
    ("h", "য"), ("i", "র"), ("j", "ল"), ("k", "শ"), ("l", "ষ"),
    ("m", "স"), ("n", "হ"), ("o", "ড়"), ("p", "ঢ়"), ("q", "য়"),
    ("r", "ৎ"), ("s", "ং"), ("t", "ঃ"), ("u", "ঁ"),

    ("v", "া"), ("w", "ি"), ("x", "ী"), ("y", "ু"), ("z", "ূ"),
    ("~", "ৃ"), ("†", "ে"), ("‰", "ৈ"), ("Š", "ৌ"), ("&", "্"),

    ("0", "০"), ("1", "১"), ("2", "২"), ("3", "৩"), ("4", "৪"),
    ("5", "৫"), ("6", "৬"), ("7", "৭"), ("8", "৮"), ("9", "৯"),
    ("|", "।")
]

def bijoy_to_unicode(text):
    if not text:
        return ""
    res = text
    res = re.sub(r'†([^†v]+)v', r'\1ো', res)
    res = re.sub(r'†([^†Š]+)Š', r'\1ৌ', res)
    res = res.replace("Av", "আ")
    res = re.sub(r'([A-Za-z0-9_`~&]+)©', r'র্\1', res)
    res = re.sub(r'([w†‰])([A-Za-z0-9_`~&]+)', r'\2\1', res)

    for b, u in MAP_PAIRS:
        res = res.replace(b, u)

    res = res.replace("অা", "আ")
    res = res.replace("Ö", "্র")
    res = res.replace("¨", "্য")
    return res

def unicode_to_bijoy(text):
    if not text:
        return ""
    res = text
    res = re.sub(r'([ক-হড়-য়](?:্[ক-হড়-য়])*(?:[্র্য])?)ো', r'†\1v', res)
    res = re.sub(r'([ক-হড়-য়](?:্[ক-হড়-য়])*(?:[্র্য])?)ৌ', r'†\1Š', res)
    res = re.sub(r'র্([ক-হড়-য়])', r'\1©', res)
    res = re.sub(r'([ক-হড়-য়])্র', r'\1Ö', res)
    res = re.sub(r'([ক-হড়-য়])্য', r'\1¨', res)

    pre_kar_pattern = r'([ক-হড়-য়](?:্[ক-হড়-য়])*(?:[Ö¨])?)([িেৈ])'
    res = re.sub(pre_kar_pattern, r'\2\1', res)

    for b, u in MAP_PAIRS:
        res = res.replace(u, b)

    res = res.replace("য়", "q")
    return res

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            payload = json.loads(post_data) if post_data else {}
        except Exception:
            payload = {}

        text = payload.get('text', '')
        mode = payload.get('mode', 'uni2bijoy')

        if mode == 'uni2bijoy':
            result = unicode_to_bijoy(text)
        elif mode == 'bijoy2uni':
            result = bijoy_to_unicode(text)
        else:
            result = ""

        response_body = json.dumps({'result': result}).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response_body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
