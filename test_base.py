import unittest
from unittest import TestCase
from unittest.mock import patch
from io import StringIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from firebase_admin import firestore
import cal_setup as cal
import cc_calendar as calendar
import os
import requests
import json
import main
import cc 
import cc_firebase as fb
import datetime
import sys

# db = firestore.client()
# slot_or_event_id = "kZkJLHEMkpAT6JUqpdQx"
# slot_ref = db.collection(u'slots').document(u''+slot_or_event_id)
# slot = slot_ref.get()
# data = slot.to_dict()
# # slot_or_event_id = data['event_id']
# event_id = data['event_id']
maxDiff = None

class TestRobot(unittest.TestCase):

    @patch("sys.stdin", StringIO("lists\n"))
    def test_1_volunteering(self):
        sys.argv[1] = "volunteer"
        sys.argv[2] = "2020-12-15"
        sys.argv.append("12:00")
        args = sys.argv

        expected_output = "Which topic are you going to help with..? A slot on 2020-12-15 at 12:00 was created for lists\n"
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "date_n_time")
            self.assertEqual(fake_out.getvalue(), expected_output)
    

    @patch("sys.stdin", StringIO("lists\n"))
    def test_2_volunteering_for_same_slot(self):
        sys.argv[1] = "volunteer"
        sys.argv[2] = "2020-12-15"
        sys.argv[3] = "12:00"
        args = sys.argv

        expected_output = "Unable to volunteer: You already have a slot at that time!\n"
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "date_n_time")
            self.assertEqual(fake_out.getvalue(), expected_output)


    @patch("sys.stdin", StringIO("lists comprehension\n"))
    def test_3_book_slot_by_date_time_self_booking(self):
        sys.argv[1] = "book-slot"
        sys.argv[2] = "2020-12-15"
        sys.argv[3] = "12:00"
        args = sys.argv
        # here i'm trying to test if i can book a slot that i created. 
        # it should not be possible, i should only book slots by other people
        expected_output = "Unable to book slot: You are unavailable at that time!\n"
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "date_n_time")
            self.assertEqual(fake_out.getvalue(), expected_output)


    @patch("sys.stdin", StringIO("lists comprehension\n"))
    def test_4_book_slot_by_date_time(self):
        self.maxDiff = None
        sys.argv[1] = "book-slot"
        sys.argv[2] = "2020-12-16"
        sys.argv[3] = "15:00"
        args = sys.argv
        expected_output = """Please describe the problem you have: Succesfully booked the slot.
summary:  Code Clinics - demo - zArgQNiMkq85TPyD5Gcb
starts at:  2020-12-16T15:00:00+02:00
ends at:  2020-12-16T15:30:00+02:00\n"""
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "date_n_time")
            self.assertEqual(fake_out.getvalue(), expected_output)


    @patch("sys.stdin", StringIO("lists comprehension\n"))
    def test_5_book_slot_by_id_that_is_taken(self):
        self.maxDiff = None
        sys.argv[1] = "book-slot"
        sys.argv[2] = "zArgQNiMkq85TPyD5Gcb"
        args = sys.argv
        expected_output = """slot already taken\n"""
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "id")
            self.assertEqual(fake_out.getvalue(), expected_output)


    @patch("sys.stdin", StringIO("lists\n"))
    def test_6_cancel_booking_by_event_id(self):
        self.maxDiff = None
        sys.argv[1] = "cancel-booking"
        sys.argv[2] = "zArgQNiMkq85TPyD5Gcb"
        args = sys.argv
        expected_output = """Successfully canceled the booking.\n"""
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "id")
            self.assertEqual(fake_out.getvalue(), expected_output)


    @patch("sys.stdin", StringIO("lists\n"))
    def test_7_cancel_booking_by_time_n_date_(self):
        #this event has been deleted by the last test, so this should test if you can delete a non-existant event 
        self.maxDiff = None
        sys.argv[1] = "cancel-booking"
        sys.argv[2] = "2020-12-16"
        sys.argv[3] = "15:00"
        args = sys.argv
        expected_output = "Unable to delete event: You don't have an event on 2020-12-16 at 15:00.\n"
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "date_n_time")
            self.assertEqual(fake_out.getvalue(), expected_output)


    @patch("sys.stdin", StringIO("lists\n"))
    def test_8_cancel_slot_by_time_n_date_(self):
        #this is free slot that only a host/doctor/mentor can delete only if its not booked. this will test if the current user can delete it  
        self.maxDiff = None
        sys.argv[1] = "cancel-slot"
        sys.argv[2] = "2020-12-15"
        sys.argv[3] = "12:00"
        args = sys.argv
        expected_output = "Successfully deleted a slot.\n"
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "date_n_time")
            self.assertEqual(fake_out.getvalue(), expected_output)


    @patch("sys.stdin", StringIO("lists\n"))
    def test_8_cancel_slot_by_id_that_is_not_yours(self):
        #this is free slot that only a host/doctor/mentor can delete only if its not booked. this will test if the current user can delete a slot that is not theirs  
        self.maxDiff = None
        sys.argv[1] = "cancel-slot"
        sys.argv[2] = "njdhBlWBbV8WxOk0totI"
        args = sys.argv
        expected_output = "\nThis slot doesn't belong to you.\n"
        with patch('sys.stdout', new = StringIO()) as fake_out: 
            cc.run_command(args, {
                "user": "tmakae",
                "time": "2020-12-11 09:11:17.229943"
            }, "id")
            self.assertEqual(fake_out.getvalue(), expected_output)