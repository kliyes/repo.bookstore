#coding=utf-8
#
# Copyright (C) 2013  Kliyes.com  All rights reserved.
#
# author: JingYang.
#
# This file is part of BookStore.

from django.utils import unittest
from django.test.client import Client

from profiles.forms import ProfileForm
from profiles.models import City, Area

class CityTest(unittest.TestCase):
    def testGetAllAreas4city(self):
        cityId = 2
        city = City.objects.getById(id=cityId)
        print "city:", city.name
         
        areas = city.getAllAreas()
        print "area len:", len(areas)
        for i in range(0, len(areas)):
            print "areas: \n", areas[i].name 
        
    def testGetAllAreas(self):
        cityId = 11
        city = City.objects.getById(id=cityId)
        print "city:", city.name
         
        areas = City.objects.getAllAreas(city)
        print "area len:", len(areas)
        for i in range(0, len(areas)):
            print "areas: \n", areas[i].name
        
        

class ProfileFormTest(unittest.TestCase):
    def testForm(self):
        f = ProfileForm()
        f.website = "  Hello    "
        #print "website:", f.cleaned_data.get("website", None)
        print f
        
    def testSpacename(self):
        pf = ProfileForm()
        pf.spacename = "   adfadfad   "
        print "spacename:", pf.clean_spacename

class SimpleTest(unittest.TestCase):
    def setUp(self):
        # Every test needs a client.
        self.client = Client()

    def test_details(self):
        # Issue a GET request.
        response = self.client.get('/account/login/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Check that the rendered context contains 5 customers.
        # self.assertEqual(len(response.cookies), 5)
        print response.cookies['csrftoken']
 
def test_something(self):
    session = self.client.session
    session['somekey'] = 'test'
    session.save() 
    
class HelloTest(unittest.TestCase):
    '''This is a sample test'''
    
    def testAdd(self):  ## test method names begin 'test*'
        self.assertEqual((1 + 2), 3)
        self.assertEqual(0 + 1, 1)
        
    def testMultiply(self):
        self.assertEqual((0 * 10), 0)
        self.assertEqual((5 * 8), 40)
        
    def setUp(self):
        pass
            
    def tearDown(self):   
        pass 

        