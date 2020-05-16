from flask import Flask, render_template, request
import requests
import random

MOVES = ["U", "B", "R", "L", "F", "D"]


def delete_html(string):
    not_html = True
    new_str = ''
    for i in string:
        if i == "<":
            not_html = False
        elif i == ">":
            not_html = True
            continue
        if not_html:
            new_str += i
    return new_str


def href(string):
    skobki = 0
    hreff = ""
    for i in string:
        if i == "\"":
            skobki += 1
            continue
        if skobki == 1:
            hreff += i
    return hreff


def find_product(product):
    url = f"https://kubik.in.ua/search/?q={'+'.join(product.split())}&s="
    resp = requests.get(url).text
    if 'Сожалеем, но ничего не найдено.' in resp:
        return []
    data = []
    js = False
    code = lambda i: False if ('<' not in i and '>' not in i and '=' not in i and '{' not in i) else True
    for i in resp.split('\n'):
        if '<script>' in i and '</script>' not in i:
            js = True
        elif '</sript>' in i:
            js = False
        if not js:
            if '''<div class="product-item''' in i:
                data.append({'name': '', 'status': '', 'price': '', 'url': ''})
            elif '''<span class="ribbon''' in i:
                data[-1]['status'] += delete_html(i).strip()
            elif not code(i) and i.strip() != "":
                data[-1]['name'] = i.strip()
            elif '''<span class="elem_item_price_cur">''' in i:
                data[-1]['price'] = delete_html(i).strip()
            elif i.strip() == '''<span class="avail_mark online"></span>''':
                if data[-1]['status'] != "":
                    data[-1]['status'] += ", "
                data[-1]['status'] += "В наличии"
            elif i.strip() == '''<span class="avail_mark offline"></span>''':
                if data[-1]['status'] != "":
                    data[-1]['status'] += ", "
                data[-1]['status'] += "Не в наличии"
            elif '''<a href="/catalog''' in i and '''class="elem_item_name"''' in i:
                data[-1]['url'] = f"https://kubik.in.ua{href(i)}"
    return data



def make_scramble(length=20):
    scramble = []
    while len(scramble) < length:
        move = random.choice(MOVES)
        index = MOVES.index(move)
        if len(scramble) > 0 and move == scramble[-1][0]:
            continue
        if len(scramble) > 1 and index + MOVES.index(scramble[-1][0]) + 1 == len(MOVES):
            continue
        rand = random.randint(1, 3)
        if rand == 1:
            move += "'"
        elif rand == 2:
            move += "2"
        scramble.append(move)
    return " ".join(scramble)


app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/scramble", methods=['GET', 'POST'])
def generator():
    if request.method == 'POST':
        n = request.form['scrambles']
        if n.isdigit():
            n = int(n)
            if 0 < n <= 100:
                data = []
                for i in range(int(n)):
                    data.append(make_scramble())
                if n >= 20:
                    return render_template("scramble-generator.html", scrambles=data, up_button=True)
                return render_template("scramble-generator.html", scrambles=data)
    return render_template("scramble-generator.html")

@app.route("/contacts")
def contacts():
    return render_template("contacts.html")

@app.route("/oll")
def oll():
    return render_template("oll.html")

@app.route("/pll")
def pll():
    return render_template("pll.html")

@app.route("/shop", methods=['GET', 'POST'])
def shop():
    if request.method == "POST":
        product = request.form["product"]
        data = find_product(product)
        if data == []:
            return render_template("shop.html", message="Сожалеем, но по вашому запросу ничего не найдено.")
        return render_template("shop.html", data=find_product(product))
    return render_template("shop.html")

app.run(port=5001, debug=True)