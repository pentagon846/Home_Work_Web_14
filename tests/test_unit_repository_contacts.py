import asyncio
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from src.database.models import User, ContactModel
from src.repository.contacts import (get_contacts, get_contact_by_id, create)
from src.schemas import ContactModel


class TestContactManagement(unittest.TestCase):
    def setUp(self):
        
        self.user = User(id=1, username="testuser")
        self.db = MagicMock()

        
        self.contact_data = {'first_name': 'John', 'second_name': 'Doe', 'email': 'johndoe@example.com',
                             'phone': '1234567890', 'birth_date': '2002-12-12', 'created_at': datetime.now(),
                             'updated_at': datetime.now()}

        
        self.contact = ContactModel(id=1, user_id=1, **self.contact_data)

    # def test_get_contacts(self):
    #     # Set up the mock for query
    #     self.db.query.return_value.filter.return_value.limit.return_value.offset.return_value.all.return_value = [
    #         self.contact]
    #
    #     
    #     contacts = asyncio.run(get_contacts(10, 0, self.user, self.db))
    #
    #     # Assertions to check the correct contacts are returned
    #     self.assertEqual(len(contacts), 1)
    #     self.assertIsInstance(contacts[0], ContactModel)
    #     self.db.query.assert_called_with(ContactModel)

    # def test_get_contact_by_id(self):
    #     
    #     self.db.query.return_value.filter.return_value.first.return_value = self.contact
    #
    #    
    #     contact = asyncio.run(get_contact_by_id(1, self.user, self.db))
    #
    #     
    #     self.assertEqual(contact, self.contact)

    def test_create(self):
        # Setup the mock
        contact_model = ContactModel(**self.contact_data)
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()

       
        created_contact = asyncio.run(create(contact_model, self.user, self.db))

        # Assertions
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(created_contact)

  
