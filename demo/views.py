from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
import json
from django.http import HttpResponse
import grpc
from . import msg_pb2
from . import msg_pb2_grpc
from py2neo import Graph, Node, Relationship
import pandas as pd
import numpy as np
import ahocorasick, sys

graph = Graph('bolt://localhost:7400', username='neo4j', password='1q2w3e')

# Create your views here.

style_dict = {
    "Person": "rgba(111,200,184,1)",
    "Interview": "rgba(255,214,24,1)",
    "Activity": "rgba(47,195,47,1)",
    "Meeting": "rgba(86,185,247,1)",
    "Talking": "rgba(234,180,4,1)",
    "Org": "rgba(222,103,44,1)",
    "Area": "rgba(222,103,44,1)",
    "Adminregion": "rgba(222,103,44,1)",
    "Autoregion": "rgba(222,103,44,1)",
    "Convention": "rgba(222,103,44,1)",
    "Country": "rgba(222,103,44,1)",
    "Municipality": "rgba(222,103,44,1)",
    "Personnel": "rgba(222,103,44,1)",
    "Province": "rgba(222,103,44,1)",
    "Report": "rgba(222,103,44,1)",
    "SubOrg": "rgba(222,103,44,1)",
    "Session": "rgba(222,103,44,1)",
}

B = ahocorasick.Automaton()
get_idiom_list_cql = "match (a:IDIOM) return a.value"
idiom_list = graph.run(get_idiom_list_cql).data()
if len(idiom_list) > 0:
    for idiom in idiom_list:
        phrase = idiom['a.value']
        B.add_word(phrase, phrase)
    B.make_automaton()

A = ahocorasick.Automaton()
get_label_list_cql = "match (a:LABEL) return a.value"
label_list = graph.run(get_label_list_cql).data()
if len(label_list) > 0:
    for label in label_list:
        i = label['a.value']
        A.add_word(i, i)
    A.make_automaton()

def index(request):
    return render(request, 'index.html')


def get_idiom_detail(idioms):
    get_detail_cql = "match (idiom:IDIOM) where idiom.value in %s return idiom.value,idiom.pinyin,idiom.explanation,idiom.source" % str(
        idioms)
    idioms_detail = graph.run(get_detail_cql).data()

    for idiom in idioms_detail:
        get_label_cql = "match (idiom:IDIOM{value:'%s'})-[:tagging]-(label:LABEL)  return label.value" % idiom[
            'idiom.value']
        labels = graph.run(get_label_cql).data()
        label_group = []
        for i in range(len(labels)):
            label_group.append(labels[i]['label.value'])
        idiom['idiom.labels'] = '|'.join(label_group)

    return idioms_detail

def req_recommand(request):
    text = request.GET.get('input_text')

    aa = B.iter(text)
    idiom_found = []

    for item in aa:
        idiom_found.append(item[1])
    idiom_found_detail = get_idiom_detail(idiom_found)

    entities = {}
    for idiom in idiom_found:
        entities[idiom] = ['IDIOM']

    msg = json.dumps({
        'entities': entities,
        'recommand': idiom_found_detail,
    })

    return HttpResponse(msg)

def req_search(request):
    value = request.GET.get('input_text')
    query = "MATCH (e) where e.value = '{0}'return e".format(value)
    res = g.run(query).data()
    entities = {}

    for item in res:
        node = item['e']
        props = dict(node)
        label = list(node.labels)[0]
        entities[node.identity] = {'value': props['value'], 'label': label}

    msg = json.dumps({'entities': entities})
    return HttpResponse(msg)

def req_qa(request):
    text = request.GET.get('input_text')

    aa = A.iter(text)
    label_idiom_group = []
    for item in aa:
        print(item)
        label = item[1]
        label_idiom = {}
        label_idiom['label'] = label

        get_idiom_list_cql = "match (a:LABEL{value:'%s'})-[:tagging]-(idiom:IDIOM) return idiom.value" % label
        idiom_list = graph.run(get_idiom_list_cql).data()
        idioms = []
        for i in idiom_list:
            idioms.append(i['idiom.value'])
        idioms_detail = get_idiom_detail(idioms)
        label_idiom['idioms'] = idioms_detail
        label_idiom_group.append(label_idiom)

    entities = {}
    for idiom in idioms:
        entities[idiom] = ['IDIOM']

    msg = json.dumps({
        'entities': entities,
        'recommand': label_idiom_group,
    })
    return HttpResponse(msg)

def entity_graph(request):
    value = request.GET.get('value')
    label = request.GET.get('label')
    label = label[0].upper() + label[1:]
    query1 = "MATCH (e:{0}) where e.value = '{1}' return e".format(label,value)
    query2 = "MATCH (h)-[r]->(e:{0}) where e.value = '{1}' return h,type(r) as r,r.name as n limit 50".format(label,value)
    query3 = "MATCH (e:{0})-[r]->(t) where e.value = '{1}' return t,type(r) as r,r.name as n limit 50".format(label,value)

    res1 = graph.run(query1).data()
    res2 = graph.run(query2).data()
    res3 = graph.run(query3).data()

    res = {
        "nodes": [],
        "links": [],
    }
    e_id = None

    for item in res1:
        node = item['e']
        props = dict(node)
        label = list(node.labels)[0]
        e_id = node.identity
        res["nodes"].append({
            "id": node.identity,
            "label": label,
            "props": props,
            "style": {"label": node["value"], "fillColor": style_dict[label]if label in style_dict.keys() else "rgba(222,103,44,1)"},
        })

    for item in res2:
        node = item['h']
        rel = item['r']
        rel_name = item['n']
        props = dict(node)
        label = list(node.labels)[0]
        res["nodes"].append({
            "id": node.identity,
            "label": label,
            "props": props,
            "style": {"label": node["value"], "fillColor": style_dict[label]if label in style_dict.keys() else "rgba(222,103,44,1)"},
        })
        res["links"].append({
            "id": str(node.identity) + '-' + str(e_id),
            "from": node.identity,
            "to": e_id,
            "style": {"fillColor":"red", "toDecoration":"arrow", "label": rel},
            "name": rel_name,
        })

    for item in res3:
        node = item['t']
        rel = item['r']
        rel_name = item['n']
        props = dict(node)
        label = list(node.labels)[0]
        res["nodes"].append({
            "id": node.identity,
            "label": label,
            "props": props,
            "style": {"label": node["value"],"fillColor": style_dict[label]if label in style_dict.keys() else "rgba(222,103,44,1)"},
        })
        res["links"].append({
            "id": str(e_id) + '-' + str(node.identity),
            "from": e_id,
            "to": node.identity,
            "style": {"fillColor": "red", "toDecoration": "arrow", "label": rel},
            "name": rel_name,
        })

    msg = json.dumps(res)
    return HttpResponse(msg)
