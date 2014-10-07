#!/usr/bin/env python
import os, sys
import logging
import unittest

logging.disable(logging.CRITICAL)

import django.core.mail
from django.test import TestCase
from django.test.client import Client

from constants import kegg_database
from parser.keggpathway import PathwayNetwork
from parser.reaction import Reaction
from view.foundations import *
from view.json import Json
from models import Task

def touch(fnames, times=None):
    for fname in fnames:
        with open('user_file/' + fname, 'a'):
            os.utime('user_file/' + fname, times)

# TODO: make cleanup a generic function that can live
# outside Django, so watch dog can cleanup files after
# task mail is sent.
def cleanup(fnames):
    for f in fnames:
        os.remove('user_file/' + f)

def get_task_uuid(client):
    response = client.get('/task/list/')
    return response.content.split(',')[-2]

def cleanup_task(testcase):
    response = testcase.client.get('/task/list/')
    testcase.assertEquals(1, len(response.content.split('\n')))
    task = response.content.split(',')
    uuid = task[-2]
    tid = task[0]
    response = testcase.client.get('/task/cleanup/', {"tid":tid})
    testcase.assertTrue('Cleaned up files:' in response.content)

class PathwayTest(TestCase):
    def setUp(self):
        self.kegg_database = kegg_database
        self.bacname = "det"
        self.pathway = PathwayNetwork(self.kegg_database, self.bacname)
        self.pathway.read_metabolisms()

    def tearDown(self):
        self.pathway = None

    def test_create(self):
        print "\nTest     | PathwayNetwork  | metabolism\t",
        self.assertTrue(self.pathway.total_gene > 0)

    def test_reactions(self):
        print "\nTest     | PathwayNetwork  | reactions\t",
        self.assertEqual(len(self.pathway.reactions), 363)

    def test_reactions_fetch(self):
        print "\nTest     | PathwayNetwork  | fetch reactions\t",
        self.assertIn('R00093', self.pathway.reactions)

    def test_pathway_add(self):
        print "\nTest     | PathwayNetwork  | pathway_add\t",
        self.pathway.add_pathway('R19999', False, "TestL", "1", "TestR", "BIOMASS")
        self.assertEqual(self.pathway.reactions['R19999'].ko, False)

    def test_pathway_update(self):
        print "\nTest     | PathwayNetwork  | pathway_update\t",
        self.pathway.update_pathway('R01229', True, "TestL", "1", "TestR", "det01100")
        self.assertTrue(self.pathway.reactions['R01229'].ko)
        self.assertTrue(self.pathway.reactions['R01229'].name, "R01229")


class ReactionTest(TestCase):
    def test_reaction(self):
        print "\nTest     | ReactionObject  | GetJson\t",
        r = Reaction("Test")
        r.reversible = False
        r.products = ["A", "B"]
        r.substrates = ["C", "D"]
        r.stoichiometry = {"A":1, "B":2, "C":3, "D":4}
        r.longname_map = {"A":"LongA", "B":"LongB", "C":"LongC", "D":"LongD"}
        r.ko = False
        expected = '{"reactionid":"Test","reactants":"3 LongC + 4 LongD","products":"1 LongA + 2 LongB","arrow":"===>","ko":false}'
        result = r.getJson().__repr__()
        self.assertEquals(expected, result)

class JsonTest(TestCase):
    def setUp(self):
        self.json = Json()

    def test_json_bool(self):
        print "\nTest     | JsonObject      | bool as json value\t",
        self.json.set_value(True)
        self.assertEquals("true", repr(self.json))
        self.json.set_value(False)
        self.assertEquals("false", repr(self.json))

    def test_json_number(self):
        print "\nTest     | JsonObject      | number as json value\t",
        self.json.set_value(2.5)
        self.assertEquals("2.5", repr(self.json))

    def test_json_obj(self):
        print "\nTest     | JsonObject      | object pairs\t",
        self.json.type = "object"
        self.json.add_pair("eric", 123)
        self.json.add_pair("eric_eric", True)
        self.json.add_pair("random", "random")
        self.assertEquals ("""{"eric":123,"eric_eric":true,"random":"random"}""", repr(self.json))

class UserViewTest(TestCase):
    fixtures = ['test/users.json', ]

    def test_add(self):
        print "\nTest     | UserView        | /user/add/\t",
        response = self.client.post('/user/add/', {'username': 'new_eric', 'password': '123'})
        self.assertEquals(200, response.status_code)
        self.assertEqual("Successfully added", response.content)

    def test_login(self):
        print "\nTest     | UserView        | /user/login/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Successfully Login") != -1)

    def test_logout(self):
        print "\nTest     | UserView        | /user/logout/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/user/logout/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Logout successfully") != 1)
        response = self.client.get('/user/summary/')
        self.assertRedirects(response, 'http://testserver/?next=/user/summary/')

    def test_summary(self):
        print "\nTest     | UserView        | /user/summary/\t",
        return # this test is skipped for now.
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/collection/create/', {'collection_name': 'summary', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/pathway/fetch/',{"_startRow":0, "_endRow":"100"})
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/model/sv/fetch/', {"_startRow":0, "_endRow":"100"})
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/model/bound/fetch/', {"_startRow":0, "_endRow":"100"})
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/model/objective/fetch/', {"_startRow":0, "_endRow":"100"})
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/collection/save/', {})
        self.assertTrue(response.content.find("Collection saved") != -1)
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/collection/select/', {'collection_name': 'summary'})
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/model/optimization/?obj_type=0')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/user/summary/?callback=test')
        self.assertEquals(response.status_code, 200)

    def test_change_pwd(self):
        print "\nTest     | UserView        | /user/password/change/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        self.assertEquals(response.status_code, 200)
        response = self.client.post('/user/password/change/', {'newpassword':'1234'})
        response = self.client.get('/user/logout/')
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '1234'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Successfully Login") != -1)

    def test_retrieve_pwd(self):
        print "\nTest     | UserView        | /user/password/retrieve\t",
        self.assertTrue(True)

class CollectionViewTest(TestCase):
    fixtures = ['test/users.json', ]

    def test_collection_create(self):
        print "\nTest     | CollectionView  | /collection/create/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Collection created") != -1)

    def test_collection_duplicated_create(self):
        print "\nTest     | CollectionView  | /collection/create/[duplicated collection names]\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Collection created") != -1)

        response = self.client.get('/collection/save/', {})
        self.assertTrue(response.content.find("Collection saved") != -1)
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Collection name is already in use") != -1)

    def test_collection_info(self):
        print "\nTest     | CollectionView  | /pathway/stat/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes','email':'test_email@noreply.com'})
        response = self.client.get('/pathway/stat/', {'collection_name': 'demo'})
        self.assertEquals(response.status_code, 200)
        expected = \
        '[{"name":"Name of the pathway","value":"demo"},{"name":"Name of the organism","value":"det"},{"name":"Number of all genes/orthologs","value":"2809"},{"name":"Number of annotated genes/orthologs","value":"478"},{"name":"Number of all pathways","value":"363"},{"name":"Number of active pathways","value":"363"}]'
        self.assertEquals(response.content, expected)

    def test_collection_save(self):
        print "\nTest     | CollectionView  | /collection/save/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes','email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Collection saved") != -1)

    def test_collection_save_as(self):
        print "\nTest     | CollectionView  | /collection/saveas/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes','email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/saveas/', {'new_name':'newname'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Collection renamed") != -1)

    def test_collection_select(self):
        print "\nTest     | CollectionView  | /collection/select/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'demo'})
        self.assertEquals(response.status_code, 200)
        self.assertTrue(response.content.find("Collection selected ") != -1)

class PathwayViewTest(TestCase):
    fixtures = ['test/users.json', ]

    def test_pathway_add(self):
        print "\nTest     | PathwayView     | /pathway/add/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'demo'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'BIOMASS', 'products':'BIOMASS', 'reactants':'TEST', 'ko':'false'})
        expected = """{response:{status:0,data:{"pk":"100001","reactionid":"R100001","ko":"false","reactants":"TEST","arrow":"0","products":"BIOMASS","pathway":"BIOMASS"}}}"""
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Inflow', 'products':'C11111', 'reactants':'C22222+C11122', 'ko':'false'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Outflow', 'products':'C22222', 'reactants':'D2222', 'ko':'false'})
        response = self.client.get('/pathway/add/', {'arrow': '1', 'pathway': 'Heterologous Pathways', 'products':'C22223', 'reactants':'D2223', 'ko':'true'})

    def test_pathway_update(self):
        print "\nTest     | PathwayView     | /pathway/update/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'demo'})
        response = self.client.get('/pathway/update/', {'arrow': '1', 'pathway': 'det00670', 'products':'2 C00234', 'reactants':'1 C00445', 'ko':'true', 'pk':'1655', 'reactionid':'R01655'})
        expected = """{response:{status:0,data:{"pk":"1655","reactionid":"R01655","ko":"true","reactants":"1 C00445","arrow":"===>","products":"2 C00234","pathway":"det00670"}}}"""
        self.assertEquals(response.content, expected)

    def test_pathway_fetch(self):
        print "\nTest     | PathwayView     | /pathway/fetch/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        self.assertEquals(response.status_code, 200)
        expected = """{"reactants":"1 C00092","products":"1 C04006","arrow":"1","reactionid":"R07324","pk":"07324","pathway":"det01100"}"""
        self.assertTrue(response.content.find(expected) != 1)
        pass

    def test_pathway_add_fetch(self):
        print "\nTest     | PathwayView     | /pathway/add and fetch\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'demo'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'BIOMASS', 'products':'BIOMASS', 'reactants':'TEST', 'ko':'false'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        self.assertEquals(response.status_code, 200)
        pass

# Usually skip this test because it is time-consuming.
# We have to populate the whole compound table...
"""
class PathwayView_AddCheckTest(TestCase):
    fixtures = ['test/users.json', 'test/cdata.json']
    def SetUp(self):
        self.client = Client()

    def test_pathway_add_check(self):
        print "\nTest     | PathwayView     | /pathway/check \t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'tex Thermoanaerobacter_X514', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'demo'})
        response = self.client.get('/pathway/check/', {'arrow': '0', 'pathway': 'BIOMASS', 'products':'H2O', 'reactants':'D-Fructose', 'ko':'false'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "'Invalid'")
        # D-Fructose is invalid because there are duplicated names
        response = self.client.get('/pathway/check/', {'arrow': '0', 'pathway': 'BIOMASS', 'reactants':'random_wrong_name', 'products':'Ethylmalonyl-CoA', 'ko':'false'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "'Invalid'")

    def test_pathway_add_check2(self):
        print "\nTest     | PathwayView     | /pathway/check \t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'tex Thermoanaerobacter_X514', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'demo'})
        response = self.client.get('/pathway/check/', {'arrow': '0', 'pathway': 'BIOMASS', 'products':'H2O', 'reactants':'C00257', 'ko':'false'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "'Valid'")
"""


class MoreBugCheck(TestCase):
    """ For bugs reported after Sept 1, 2011"""
    fixtures = ['test/users.json', ]

    """ If you do editing to a pathway and save it, when you reload it, it should not change """
    def test_pathway_add_save_knockout(self):
        print "\nTest     | MoreBugCheck     | misc knockout\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'pathway_ko', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'pathway_ko'})
        response = self.client.get('/pathway/update/', {'arrow': '0', 'pathway': 'det00670', 'products':'2 C00234', 'reactants':'1 C00445', 'ko':'false', 'pk':'1655', 'reactionid':'R01655'})
        expected = """{response:{status:0,data:{"pk":"1655","reactionid":"R01655","ko":"false","reactants":"1 C00445","arrow":"<===>","products":"2 C00234","pathway":"det00670"}}}"""
        self.assertEquals(response.content, expected)
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'pathway_ko'})
        response = self.client.get('/model/objective/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})

class ModelViewObjectiveTest(TestCase):
    fixtures = ['test/users.json', ]

    def SetUp(self):
        self.client = Client()

    def test_objective_fetch(self):
        print "\nTest     | ModelViewObjective   | /model/objective/fetch/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'obj_fetch', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/model/objective/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})
        expected1 = 'eric({response:{status:0,startRow:0,endRow:362,totalRows:363,data:['
        expected2 = 'r":"R00425","w":"1"}'
        self.assertContains(response, expected1)
        self.assertContains(response, expected2)

    def test_objective_update(self):
        print "\nTest     | ModelViewObjective   | /model/objective/update/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'obj_update', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/model/objective/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})
        response = self.client.get('/model/objective/update/', {"pk":"299", "r":"R00299", "w":"0.4"})
        expected = """{response:{status:0,data:{"pk":"299","r":"R00299","w":"0.4"}}}"""
        self.assertEquals(expected, response.content)


class TaskTest(TestCase):
    def test_task_add(self):
        print "\nTest     | TaskView   | /task/add/\t",
        response = self.client.get('/task/add/', {"type":"fba", "task":"test", "email":"test_email@noreply.com", "file":"NULL"})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/task/add/', {"type":"dfba", "task":"test", "email":"test_email@noreply.com", "file":"NULL"})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/task/add/', {"type":"dfba", "task":"test", "email":"test_email2@noreply.com", "file":"one_more"})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/task/add/', {"type":"svg", "task":"test", "email":"test_email@noreply.com", "file":"NULL"})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/task/list/')
        ## Model name (seen by user), model_type, email for results, task status.
        expected_str = [ 'test,fba,test_email@noreply.com,TODO',
                         'test,dfba,test_email@noreply.com,TODO',
                         'test,dfba,test_email2@noreply.com,TODO',
                         'test,svg,test_email@noreply.com,TODO']
        for expected in expected_str:
            self.assertTrue(expected in response.content)

    def test_task_remove(self):
        print "\nTest     | TaskView   | /task/remove/\t",
        response = self.client.get('/task/add/', {"type":"t1", "task":"test", "email":"test_email@noreply.com", "file":"NULL"})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/task/add/', {"type":"t2", "task":"ttest2", "email":"test_email@noreply.com", "file":"NULL"})
        response = self.client.get('/task/list/')
        self.assertEquals(response.status_code, 200)

        tid = response.content[0]
        response = self.client.get('/task/remove/', {"tid":tid})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "Task Removed")

        response = self.client.get('/task/list/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(str(int(tid)+1) +",ttest2,t2,test_email@noreply.com,TODO" in response.content)

    def test_task_mark(self):
        print "\nTest     | TaskView   | /task/mark/\t",
        response = self.client.get('/task/add/', {"type":"type1", "task":"test_task_add", "email":"test_email@noreply.com", "file":"NULL"})
        response = self.client.get('/task/list/')
        self.assertEquals(response.status_code, 200)
        tid = response.content[0]

        response = self.client.get('/task/mark/', {"tid":tid})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "Task Marked")
        response = self.client.get('/task/list/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(tid + ",test_task_add,type1,test_email@noreply.com,CLOUD" in response.content)

    def test_task_mark_customized(self):
        print "\nTest     | TaskView   | /task/mark/?status=custom_label\t",
        response = self.client.get('/task/add/', {"type":"type1", "task":"test_task_add", "email":"test_email@noreply.com", "file":"NULL"})
        response = self.client.get('/task/list/')
        tid = response.content[0]

        response = self.client.get('/task/mark/', {"tid":tid, "status":"SomeStatus"})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, "Task Marked")
        response = self.client.get('/task/list/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(tid + ",test_task_add,type1,test_email@noreply.com,SomeStatus" in response.content)

    def test_task_mail(self):
        print "\nTest     | TaskView   | /task/mail/\t",
        name = "test_task_mail"

        response = self.client.get('/task/add/', {"type":"dfba", "task": name, "email":"test@noreply.com", "file":"NULL"})
        response = self.client.get('/task/list/')
        uuid = get_task_uuid(self.client)
        files = [ uuid + suffix for suffix in ['.ampl', '.map', '.result', '.header']]
        touch(files)

        self.assertEquals(response.status_code, 200)
        tid = response.content[0]
        response = self.client.get('/task/mail/', {"tid":tid})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, " Mail sent ")
        self.assertEquals(1, len(django.core.mail.outbox))
        email = django.core.mail.outbox[0]
        self.assertTrue('Mail from MicrobesFlux --dFBA' in email.subject)
        self.assertTrue('test@noreply.com' in email.to)
        self.assertEquals('test_task_mail_dfba_report.txt', email.attachments[0][0])
        response = self.client.get('/task/mail/', {"tid":tid})
        self.assertEquals(response.status_code, 200)
        cleanup_task(self)

class ModelViewBoundTest(TestCase):
    fixtures = ['test/users.json', ]
    def test_bound_update(self):
        print "\nTest     | ModelViewObjective   | /model/objective/update/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'bound_update', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/model/bound/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/model/bound/update/', {"pk":"01354", "r":"R01354", "l":"4.9", "u":"5.5"})
        self.assertEquals(response.status_code, 200)

class ModelViewOptimization(TestCase):
    fixtures = ['test/users.json', ]

    def SetUp(self):
        self.client = Client()

    def test_add_pathway_should_appear(self):
        print "\nTest     | ModelViewObjective   | /add pathway verify\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'model_view_opt', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})

        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Heterologous Pathways', 'products':'ADP', 'reactants':'ATP', 'ko':'false'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Heterologous Pathways', 'products':'ATP', 'reactants':'ADP', 'ko':'false'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/model/objective/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})
        self.assertEquals(response.status_code, 200)

    def test_fba_job_submit0(self):
        print "\nTest     | ModelViewObjective   | /optimization/ for user\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'test_fba', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})

        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/model/objective/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})

        response = self.client.get('/model/bound/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/model/sv/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})
        self.assertEquals(response.status_code, 200)
        response = self.client.get("/model/optimization/?obj_type=0")
        cleanup_task(self)

    def test_fba_job_submit1(self):
        print "\nTest     | ModelViewObjective   | /optimization for biomass\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'test_fba_biomass', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})

        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/model/objective/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})

        response = self.client.get('/model/bound/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/model/sv/fetch/', {"_startRow":0, "_endRow":1000, "callback":"eric"})
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'BIOMASS', 'products':'BIOMASS', 'reactants':'899 C00200', 'ko':'false'})

        response = self.client.get("/model/optimization/?obj_type=1")# biomass
        cleanup_task(self)

class UploadTest(TestCase):
    fixtures = ['test/users.json', ]

    def test_upload(self):
        print "\nTest     | UploadTest   | /model/upload/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'demo', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'BIOMASS', 'products':'BIOMASS', 'reactants':'1 ATP', 'ko':'false'})
        expected = """{response:{status:0,data:{"pk":"100001","reactionid":"R100001","ko":"false","reactants":"1 ATP","arrow":"0","products":"BIOMASS","pathway":"BIOMASS"}}}"""
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Inflow', 'products':'C01111', 'reactants':'C02222', 'ko':'false'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Outflow', 'products':'C02222', 'reactants':'C02223', 'ko':'false'})

        f = open("test/toupload.txt")
        response = self.client.post('/model/upload/', {'uploadFormElement': f} )
        f.close()
        self.assertTrue(response.content.find("Successfully Uploaded") != -1)
        file_key = response.content.split()[-1]
        cleanup(['dfba/' + file_key])

class TestSbml(TestCase):
    fixtures = ['test/users.json', ]

    def test_sbml(self):
        print "\nTest     | TestSbml   | /model/sbml/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'test_sbml', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        response = self.client.get('/pathway/update/', {'arrow': '1', 'pathway': 'det00670', 'products':'2 C00234', 'reactants':'1 C00445', 'ko':'true', 'pk':'1655', 'reactionid':'R01655'})
        response = self.client.get('/pathway/add/', {'arrow': '1', 'pathway': 'BIOMASS', 'products':'BIOMASS', 'reactants':'1 ATP', 'ko':'true'})
        response = self.client.get('/model/sbml/')
        # TODO(xuy): sbml should get cleaned up the moment the email is out.
        cleanup(['test_sbml.sbml',])

class TestDFBA(TestCase):
    fixtures = ['test/users.json', ]

    def test_dfba(self):
        print "\nTest     | TestDFBA   | /model/dfba/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'test_dfba', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'BIOMASS', 'products':'BIOMASS', 'reactants':'1 ATP', 'ko':'false'})
        expected = 'response:{status:0,data:{"pk":"100001","reactionid":"R100001","ko":"false","reactants":"1 ATP","arrow":"0","products":"BIOMASS","pathway":"BIOMASS"}}}'
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Inflow', 'products':'C01111', 'reactants':'C02222', 'ko':'false'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Outflow', 'products':'C02222', 'reactants':'C02223', 'ko':'false'})
        f = open("test/toupload.txt")
        response = self.client.post('/model/upload/', {'uploadFormElement': f} )
        f.close()
        self.assertTrue(response.content.find("Successfully Uploaded") != -1)
        response = self.client.get('/model/dfba/', {'obj_type':'1','provided_email':'test_email@noreply.com',})
        cleanup_task(self)
        # uuid = get_task_uuid(self.client)
        # cleanup([uuid + suffix for suffix in ['.ampl', '.map', '.header']])

class TestSvg(TestCase):
    fixtures = ['test/users.json', ]

    def test_svg(self):
        print "\nTest     | TestSvg   | /model/svg/\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'test_svg', 'bacteria': 'det D.ethenogenes', 'email':'test@noreply.com'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        response = self.client.get('/model/svg/')
        tasks = Task.objects.all()
        self.assertEquals(1, len(tasks))
        task = tasks[0]
        self.assertEquals(task.task_type, 'svg')
        self.assertEquals(task.main_file, 'test_svg')
        self.assertEquals(task.email, 'test@noreply.com')
        self.assertEquals(task.status, 'TODO')
        uuid = get_task_uuid(self.client)
        # Simulate the svg emailing logic.
        files = [ uuid + suffix for suffix in ['.svg']]

        touch(files)
        response = self.client.get('/task/mail/', {"tid":task.task_id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, " Mail sent ")
        self.assertEquals(1, len(django.core.mail.outbox))
        email = django.core.mail.outbox[0]
        self.assertTrue('Mail from MicrobesFlux -- SVG test_svg' in email.subject)
        self.assertTrue('test@noreply.com' in email.to)
        self.assertEquals('test_svg.svg', email.attachments[0][0])
        cleanup_task(self)
        # files.append(uuid + '.adjlist')
        # cleanup(files)

""" The following tests are ignored from this release
class TestOpt(TestCase):
    def test_opt(self):
        print "\nTest     | TestOpt   | /model/optimization/\t",
        response = self.client.get('/collection/create/', {'collection_name': 'test_opt', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        response = self.client.get('/model/optimization/?obj_type=0')
        # response = self.client.get('/task/mail/', {'tid':'2011-03-30-14:19:24.919410'})
        self.assertEquals(response.status_code, 200)

"""
from view.collection_view import get_pathway_by_name
from view.collection_view import save_collection

from django.contrib.auth.models import User

class CollectionLogicTest(TestCase):
    fixtures = ['test/users.json', ]

    def test_collection_save_load(self):
        print "\nTest	  | CollectionLogicTest	| get_pathway_by_name\t",
        self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        obj = [1, 2, 3]
        u = User.objects.get(email = "eric")
        save_collection(u, "test", obj)
        o = get_pathway_by_name(u, "test")
        self.assertEquals(obj, o)

class BoundKnockOutTest(TestCase):
    fixtures = ['test/users.json', ]

    def test_back_and_forth_switch(self):
        print "\nTest     | TestBoundKnockout   | /misc/bugs/\t",
        self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'test_bound', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        response = self.client.get('/model/objective/fetch/',  {'_startRow':0, '_endRow':1000})
        self.assertEquals(200, response.status_code)
        response = self.client.get('/model/bound/fetch/',  {'_startRow':0, '_endRow':1000})

        response = self.client.get('/pathway/update/', {'arrow': '1', 'pathway': 'det00670', 'products':'2 C00234', 'reactants':'1 C00445', 'ko':'true', 'pk':'386', 'reactionid':'R01867'})
        # {"pk":386,"r":"R01867","l":"-100.0","u":"100.0"},
        response = self.client.get('/model/bound/fetch/',  {'_startRow':0, '_endRow':1000})


class OtherBugTest(TestCase):
    fixtures = ['test/users.json', ]

    def test_back_and_forth_switch(self):
        print "\nTest     | TestBug   | /misc/bugs/\t",
        self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'other_bugs', 'bacteria': 'det D.ethenogenes', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        response = self.client.get('/model/objective/fetch/',  {'_startRow':0, '_endRow':1000})
        self.assertEquals(200, response.status_code)
        response = self.client.get('/model/bound/fetch/',  {'_startRow':0, '_endRow':1000})
        self.assertEquals(200, response.status_code)
        response = self.client.get('/model/sv/fetch/',  {'_startRow':0, '_endRow':1000})
        self.assertEquals(200, response.status_code)
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        self.assertEquals(200, response.status_code)


class TestToy(TestCase):
    fixtures = ['test/users.json', ]

    def test_toy_construct(self):
        print "\nTest	  | TestToy	| /pathway/fetch for TOY\t",
        self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'toy_fetch', 'bacteria': 'TOY A.Toy.Example', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})

""" This tests the TOY example """
class TestToyOptimization(TestCase):
    fixtures = ['test/users.json', ]
    def test_toy_dfba(self):
        print "\nTest	  | TestToyOptimization	| dfba for TOY\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'toyd', 'bacteria': 'TOY A.Toy.Example', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Inflow', 'products':'c_g6p', 'reactants':'1 c_glucose', 'ko':'false'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Outflow', 'products':'c_Acetate', 'reactants':'1 c_accoa', 'ko':'false'})
        response = self.client.get('/pathway/fetch/', {'_startRow':0, '_endRow':1000})
        f = open("test/toy_dfba_upload.txt")
        response = self.client.post('/model/upload/', {'uploadFormElement': f} )
        f.close()
        self.assertTrue(response.content.find("Successfully Uploaded") != -1)
        response = self.client.get('/model/dfba/?obj_type=1')
        cleanup_task(self)
        # uuid = get_task_uuid(self.client)
        # cleanup([uuid + suffix for suffix in ['.ampl', '.map', '.header']])

    def test_toy_fba(self):
        print "\nTest	  | TestToyOptimization	| fba for TOY\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'toyf', 'bacteria': 'TOY A.Toy.Example', 'email':'test_email@noreply.com'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Inflow', 'products':'c_g6p', 'reactants':'1 c_glucose', 'ko':'false'})
        response = self.client.get('/pathway/add/', {'arrow': '0', 'pathway': 'Outflow', 'products':'c_Acetate', 'reactants':'1 c_accoa', 'ko':'false'})
        response = self.client.get('/model/bound/update/', {"pk":"2", "r":"Outflow2", "l":"6.4", "u":"6.4"})
        response = self.client.get('/model/bound/update/', {"pk":"9", "r":"Inflow1", "l":"11.0", "u":"11.0"})
        response = self.client.get('/model/optimization/?obj_type=1')
        cleanup_task(self)
        # uuid = get_task_uuid(self.client)
        # cleanup([uuid + suffix for suffix in ['.ampl', '.map', '.header']])

""" This tests the report composition module """
class TestReportGenerate(TestCase):
    def test_report_generate(self):
        ## We already have something called Demoxx
        print "\nTest	  | TestReportGeneration	| test report generation \t",
        name = 'test_report_generation'

        response = self.client.get('/task/add/', {"type":"fba", "task": name, "email":"test_email@noreply.com", "file":"NULL"})
        self.assertEquals(response.status_code, 200)
        tasks = Task.objects.all()
        self.assertEquals(1, len(tasks))

        uuid = get_task_uuid(self.client)
        files = [ uuid + suffix for suffix in ['.ampl', '.map', '.result', '.header']]
        touch(files)

        response = self.client.get('/task/mail/', {"tid":tasks[0].task_id})
        cleanup_task(self)
        # files.append(uuid + '.report')
        # cleanup(files)

class MoreBugCheck(TestCase):
    """ For bugs reported after Sept 1, 2011"""
    fixtures = ['test/users.json', ]
    """ If you do editing to a pathway and save it, when you reload it, it should not change """
    def test_pathway_add_save_knockout(self):
        print "\nTest     | MoreBugCheck     | misc knockout\t",
        response = self.client.post('/user/login/', {'username': 'eric', 'password': '123'})
        response = self.client.get('/collection/create/', {'collection_name': 'newdemo', 'bacteria': 'tex Thermoanaerobacter_X514', 'email':'test_email@noreply.com'})
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'newdemo'})
        expected = '{"reactionid":"R05132","reactants":"1 Protein-N(pi)-phospho-L-histidine + 1 Arbutin","products":"1 Protein-histidine + 1 Arbutin-6-phosphate","arrow":"===>","ko":false,"pathway":"path:tex00010"}'
        # Assure that the reaction is correct.
        response = self.client.get('/pathway/query/', {'reaction':'R05132'})
        self.assertEquals(expected, response.content)
        # Now update the reaction.
        response = self.client.get('/pathway/update/', {'arrow': '<==>', 'pathway': 'path:tex00010', 'products':'1 Protein-histidine + 1 Arbutin-6-phosphate', 'reactants':'1 Protein-N(pi)-phospho-L-histidine + 1 Arbutin', 'ko':'false', 'pk':'1655', 'reactionid':'R01655'})
        expected_update = '{response:{status:0,data:{"pk":"1655","reactionid":"R01655","ko":"false","reactants":"1 Protein-N(pi)-phospho-L-histidine + 1 Arbutin","arrow":"<==>","products":"1 Protein-histidine + 1 Arbutin-6-phosphate","pathway":"path:tex00010"}}}'
        self.assertEquals(response.content, expected_update)
        response = self.client.get('/collection/save/', {})
        response = self.client.get('/collection/select/', {'collection_name': 'newdemo'})
        response = self.client.get('/pathway/query/', {'reaction':'R05132'})
        self.assertEquals(expected, response.content)
        response = self.client.get('/pathway/fetch/',{"_startRow":0, "_endRow":1000, "callback":"eric"})

"""
class BoundaryHackForXueyang(TestCase):
    def test_set_boundary(self):
	response = self.client.post('/user/login/', {'username': 'xueyang.feng@gmail.com', 'password': '150436'})
        response = self.client.get('/collection/select/', {'collection_name': 'tex_MicrobesFlux_F2'})
        response = self.client.get('/collection/save/', {})
"""
