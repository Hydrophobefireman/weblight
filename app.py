import base64
from io import BytesIO
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup as bs
from flask import Flask, redirect, render_template, request, session, url_for
from htmlmin.minify import html_minify
from PIL import Image

CUSTOM_STYLE = r"""body{margin:0;word-wrap:break-word}img{max-width:100%}[style*="position:relative"]>div:first-child img{min-width:100%;height:auto}table img{max-width:none}table{width:100%}ul,ol{padding-left:25px}form{margin-bottom:0}input.ii{border:0px;background-repeat:no-repeat;background-position:center center}input:not([type="image"]):not([type="radio"]):not(.ii){border:1px solid rgba(0,0,0,0.2)}input:not([type="image"]):not([type="radio"]):not(.ii),select{border-radius:0;-webkit-box-sizing:border-box;box-sizing:border-box;color:rgba(0,0,0,0.87);vertical-align:middle}select{padding:3px}input:not([type="image"]):not(.ii){padding:4px 14px}textarea{height:100px;width:100%}a{color:inherit;text-decoration:inherit}pre{overflow-x:auto}#wl-hdr-orig{background-color:#eee;border-bottom:1px #e0e0e0 solid;color:#626262;display:block;font:13px roboto,sans-serif;padding:6px 7px 6px 12px}#wl-hdr-l{display:inline-block;width:60%}#wl-hdr-r{display:inline-block;float:right}#wl-info-icon{text-decoration:none}#wl-orig{color:#1e88e5;text-decoration:none}#wl-hdr-url{background-color:#eee;border-bottom:1px #9e9e9e solid;color:#9e9e9e;font:11px roboto,sans-serif;overflow-x:auto;padding:3px 10px;white-space:nowrap}#wl-brand-hdr:before{content:"";display:inline-block;height:30px;vertical-align:middle}#wl-brand-hdr{height:30px;padding:6px 6px 6px 16px}#wl-brand{font:bold 18px roboto,sans-serif;width:70%}.wl-ns{color:#e55}.wl-overflow{display:inline-block;overflow:hidden;text-overflow:ellipsis;vertical-align:middle;white-space:nowrap}.content-block{line-height:1.4;padding:2px 8px}table .content-block{padding:2px 4px}.i{display:inline-block}.i.t{vertical-align:top}.i.m{vertical-align:middle}.invis{visibility:hidden}.sf span{display:block;overflow:hidden;padding-right:10px}.sfi{display:inline-block;vertical-align:middle}.sf input[type="submit"]{float:right;font-weight:bold}.ww{width:100%}button{border:0;background-color:transparent}a[style*="background-color"],button span{-webkit-box-shadow:0px 0px 1px #000;box-shadow:0px 0px 1px #000}a[style*="background-color"],a[style*="border"],span[style*="background-color"]{padding:3px 7px;margin:2px 3px 2px 0;display:inline-block}[data-nb]{display:none}.irb{display:none}"""


def fix_html(url, ua):
    soup = bs(requests.Session().get(url, headers={
              'User-Agent': ua}, allow_redirects=True).text, "html.parser")
    style = soup.style
    try:
        style.clear()
    except:
        pass
    st = soup.new_tag("style")
    met = soup.new_tag("meta")
    met['name'] = "viewport"
    met['content'] = "width=device-width, initial-scale=1.0"
    soup.head.append(met)
    st.string = CUSTOM_STYLE
    soup.head.append(st)
    img_tags = soup.findAll("img")
    for e in img_tags:
        i = img_tags.index(e)
        image = ''
        try:
            image = pr_check(soup.findAll("img")[i]["src"], url)
        except KeyError:
            pass
        soup.findAll("img")[i]['src'] = image
        soup.findAll("img")[i]["max-width"] = 2048
        soup.findAll("img")[i]["max-height"] = 2048
    [s.extract() for s in soup("link") if "style" not in str(s)]
    [s.extract() for s in soup("script")]
    [s.extract() for s in soup("video")]
    [s.extract() for s in soup("noscript")]
    return str(soup)


def pr_check(thumb, url):
    data = thumb
    try:
        if str(thumb).startswith("//"):
            thumb = "http:"+thumb
        elif str(thumb).startswith("/"):
            r = url.split("/")[2]
            r = "http://"+r
            thumb = r+thumb
    # if "localhost:" not in request.url_root and "127.0.0.1" not in request.url_root and "0.0.0.0:" not in request.url_root:
        if 1 is 1:
            img = Image.open(requests.get(thumb, stream=True).raw)
            #img = img.resize((240, 180), Image.ANTIALIAS)
            b = None
            b = BytesIO()
            try:
                img.save(b, format='jpeg', quality=90, optimise=True)
            except:
                img.convert("RGB").save(b, format='jpeg',
                                        quality=90, optimise=True)
            data = "data:image/jpeg;base64," + \
                (base64.b64encode(b.getvalue())).decode("ascii")
    except:
        pass
    return data


app = Flask(__name__)


@app.route("/")
def miain():
    return render_template("index.html")


@app.route("/i")
def stuff():
    url = unquote(request.args.get("u"))
    data = fix_html(url, request.headers.get("User-Agent"))
    data = html_minify(str(data))
    return data


if __name__ == "__main__":
    app.run(debug=True)
