import asyncio
import unittest
from datetime import datetime
from unittest.mock import MagicMock

from src.database.models import User, ContactModel
from src.repository.contacts import (get_contacts, get_contact_by_id, create)
from src.schemas import ContactModel


class TestContactManagement(unittest.TestCase):
    def setUp(self):
        # Mock the User and Session objects
        self.user = User(id=1, username="testuser")
        self.db = MagicMock()

        # Sample contact data
        self.contact_data = {'first_name': 'John', 'second_name': 'Doe', 'email': 'johndoe@example.com',
                             'phone': '1234567890', 'birth_date': '2002-12-12', 'created_at': datetime.now(),
                             'updated_at': datetime.now()}

        # Mock a Contact object
        self.contact = ContactModel(id=1, user_id=1, **self.contact_data)

    # def test_get_contacts(self):
    #     # Set up the mock for query
    #     self.db.query.return_value.filter.return_value.limit.return_value.offset.return_value.all.return_value = [
    #         self.contact]
    #
    #     # Run the test
    #     contacts = asyncio.run(get_contacts(10, 0, self.user, self.db))
    #
    #     # Assertions to check the correct contacts are returned
    #     self.assertEqual(len(contacts), 1)
    #     self.assertIsInstance(contacts[0], ContactModel)
    #     self.db.query.assert_called_with(ContactModel)

    # def test_get_contact_by_id(self):
    #     # Setup the mock
    #     self.db.query.return_value.filter.return_value.first.return_value = self.contact
    #
    #     # Run the test
    #     contact = asyncio.run(get_contact_by_id(1, self.user, self.db))
    #
    #     # Assertions to ensure correct contact is returned
    #     self.assertEqual(contact, self.contact)

    def test_create(self):
        # Setup the mock
        contact_model = ContactModel(**self.contact_data)
        self.db.add = MagicMock()
        self.db.commit = MagicMock()
        self.db.refresh = MagicMock()

        # Run the test
        created_contact = asyncio.run(create(contact_model, self.user, self.db))

        # Assertions
        self.db.add.assert_called_once()
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(created_contact)

    # Add more tests for each function following the similar pattern

# if __name__ == "__main__":
#     unittest.main()


# import unittest
# from unittest.mock import AsyncMock
# from datetime import date
# from src.database.models import User, Contact
# from src.schemas import ContactModel
# from src.repository.contacts import get_contacts, get_contact_by_id, create
#
#
# class TestContactManagement(unittest.IsolatedAsyncioTestCase):
#     async def asyncSetUp(self):
#         self.db = AsyncMock()
#         self.user = User(id=1)
#         self.contact_data = ContactModel(first_name="John", second_name="Doe", email="john.doe@example.com",
#                                          phone="1234567890", birth_date=date(1990, 1, 1))
#
#     async def test_get_contacts(self):
#         # Setup
#         self.db.query.return_value.filter.return_value.limit.return_value.offset.return_value.all.return_value = [
#             Contact(first_name="John")]
#
#         # Execution
#         contacts = await get_contacts(10, 0, self.user, self.db)
#
#         # Assertion
#         self.db.query.assert_called_with(Contact)
#         self.assertEqual(len(contacts), 1)
#         self.assertIsInstance(contacts[0], Contact)
#
#     async def test_get_contact_by_id(self):
#         # Setup
#         contact_id = 5
#         self.db.query.return_value.filter.return_value.first.return_value = Contact(id=contact_id, first_name="John")
#
#         # Execution
#         contact = await get_contact_by_id(contact_id, self.user, self.db)
#
#         # Assertion
#         self.db.query.assert_called_with(Contact)
#         self.assertEqual(contact.id, contact_id)
#         self.assertEqual(contact.first_name, "John")
#
#     async def test_create_contact(self):
#         # Setup
#         self.db.add = AsyncMock()
#         self.db.commit = AsyncMock()
#         self.db.refresh = AsyncMock()
#
#         # Execution
#         new_contact = await create(self.contact_data, self.user, self.db)
#
#         # Assertion
#         self.db.add.assert_called()
#         self.db.commit.assert_called()
#         self.db.refresh.assert_called_with(new_contact)
#         self.assertEqual(new_contact.user, self.user)
#
#
# if __name__ == '__main__':
#     unittest.main()
