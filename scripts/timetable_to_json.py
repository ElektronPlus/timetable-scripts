import json, sys, time, html, requests, string
from requests.auth import HTTPBasicAuth


# -*- coding: utf-8 -*-
def planLekcji(response):
    plan = {"godziny": [], "tydzien": []}
    r = response.split('<table border="1"')[1].split('</table>')[0]
    r = ''.join(r.split("\r\n"))
    r = ''.join(r.split("\t"))
    r = ''.join(r.split("    "))
    r = ''.join(r.split("   "))
    r = ''.join(r.split("\u00a0"))
    t = r.split('<tr>')[1].split('</tr>')[0]
    for d in t.split('<th>')[3:]:
        name = d.split('</th>')[0]
        if name == "Poniedzialek":
            name = "Poniedziałek"
        elif name == "Sroda":
            name = "Środa"
        elif name == "Piatek":
            name = "Piątek"
        plan['tydzien'].append({'name': name, 'lekcje': []})
    for h in r.split('<tr>')[2:]:
        h = h.split('</tr>')[0]
        index = h.split('<td class="nr">')[1].split('</td>')[0]
        plan['godziny'].append(''.join(
            h.split('<td class="g">')[1].split('</td>')[0].split(' ')))
        for i, l in enumerate(h.split('<td class="l">')[1:]):
            l = l.split('</td>')[0]
            l = '\n'.join(l.split('<br>'))
            for ic in range(1, len(l.split('<'))):
                l = l.split('<')[0] + ('>'.join(l.split('>')[1:]))

            while l.endswith(' '):
                l = l[:-1]
            while l.endswith('\n'):
                l = l[:-1]
            while l.endswith(' '):
                l = l[:-1]

            plan['tydzien'][i]['lekcje'].append({
                'index': int(index),
                'data': l
            })
    for i in list(plan['tydzien']):
        if len(i['lekcje']) == 0:
            plan['tydzien'].remove(i)
    return plan


class v1():

    def kategorie(self, response):
        return enumerate(
            response.split('<p>')[1].split('</p')[0].split('<select')[1:])

    def kategoriaName(self, kategoria):
        sel = kategoria.split('</select>')[0]
        sel = '>'.join(sel.split('>')[1:]).lower()
        return sel.split('<option>')[1].split('</option>')[0].lower()

    def opcje(self, kategoria):
        sel = kategoria.split('</select>')[0]
        sel = '>'.join(sel.split('>')[1:]).lower()
        #sel = sel.split('<')[1]
        return sel.split('<option')[2:]

    def optionName(self, opcja):
        return opcja.split('</option>')[0].split('>')[1].split('<')[0]

    def optionValue(self, opcja, katName):
        return opcja.split('</option>')[0].split('value="')[1].split('"')[0]


class v2():

    def kategorie(self, response):
        return enumerate(
            response.split('<body>')[1].split('</body>')[0].split('<h4>')[1:])

    def kategoriaName(self, kategoria):
        sel = kategoria.split('</ul>')[0]
        return sel.split('</h4>')[0].lower()

    def opcje(self, kategoria):
        sel = kategoria.split('</ul>')[0]
        sel = sel.split('<ul>')[1]
        #sel = '>'.join(sel.split('>')[1:])
        return sel.split('<li>')[1:]

    def optionName(self, opcja):
        return opcja.split('</li>')[0].split('>')[1].split('<')[0]

    def optionValue(self, opcja, katName):
        return opcja.split('</li>')[0].split('href="')[1].split('"')[0].split(
            '/' + katName[0].lower())[1].split('.html')[0]


def getons(response):
    ons = {}
    print(response)
    if len(response.split('<p>')) > 1:
        print('v1\n')
        v = v1()
    else:
        print('v2\n')
        v = v2()
    for i, kategoria in v.kategorie(response):
        options = []
        katName = v.kategoriaName(kategoria)
        for option in v.opcje(kategoria):
            name = v.optionName(option)
            value = v.optionValue(option, katName)
            if i == 0:
                name = name.split(' ')[0] + ' ' + '-'.join(name.split('-')[1:])
            elif i == 2:
                if name == "czyt czytelnia":
                    name = "czytelnia"
                elif name == "sg1 sala gimnastyczna 1":
                    name = "sala gimnastyczna 1"
                elif name == "sg2 sala gimnastyczna 2":
                    name = "sala gimnastyczna 2"

            options.append({"name": name, "value": value})
            #options.append(value)
        ons[katName] = {'id': katName[0], 'options': options}
    return ons


s = requests.Session()
url = "http://zseis.zgora.pl/plan/lista.html"
r = s.get(url, auth=HTTPBasicAuth('ckziu', 'zseis'))
encoding = 'utf-8' if input(
    'Podaj encoding ("u" dla utf-8 lub "i" dla iso-8859-2) -> ') in [
        'u', 'utf-8'
    ] else 'iso-8859-2'
r.encoding = encoding
r = getons(html.unescape(r.text))

plany = {'legend': r, 'plany': {}}
for key, value in r.items():
    for i in value['options']:
        id = value['id'] + i['value']
        print(id)
        r = s.get("http://zseis.zgora.pl/plan/plany/" + id + ".html",
                  auth=HTTPBasicAuth('ckziu', 'zseis'))
        r.encoding = encoding
        plany['plany'][id] = planLekcji(html.unescape(r.text))
print(plany)
with open('C:\\Users\\Krystian Wybranowski\\Desktop\\planyLekcji.json',
          'w') as outfile:
    json.dump(plany, outfile)
print("zapisano")
