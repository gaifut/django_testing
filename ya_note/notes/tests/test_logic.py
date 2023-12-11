from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestNoteCreate(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user_author = User.objects.create(username='user author')
        cls.url = reverse('notes:add')
        cls.url_success = reverse('notes:success')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user_author)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'note text',
            'slug': 'zagolovok'
        }

    def test_anonymous_user_cannot_create_note(self):
        self.client.post(self.url, data=self.form_data)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.url_success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    @classmethod
    def tearDownClass(cls):
        pass


class TestNotesEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'text'
    NOTE_SLUG = 'zagolovok'
    NEW_NOTE_TITLE = 'Заголовок2'
    NEW_NOTE_TEXT = 'note text2'
    NEW_NOTE_SLUG = 'zagolovok2'

    @classmethod
    def setUpClass(cls):
        cls.user_author = User.objects.create(username='author')
        cls.user_another = User.objects.create(username='another')
        cls.url_success = reverse('notes:success')
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            author=cls.user_author,
            slug=cls.NOTE_SLUG,
        )
        cls.url_note = reverse('notes:detail', args=(cls.note.slug,))
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)
        cls.another_client = Client()
        cls.another_client.force_login(cls.user_another)
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.add_url = reverse('notes:add')
        cls.form_data = {
            'title': cls.NEW_NOTE_TITLE,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.NEW_NOTE_SLUG,
        }
        cls.form_data_same_slug = {
            'title': 'Заголовок3',
            'text': 'note text3',
            'slug': cls.NOTE_SLUG,
        }
        cls.form_data_without_slug = {
            'title': 'Заголовок444',
            'text': 'note text444',
            'slug': ''
        }

    def test_author_can_delete_note(self):
        self.author_client.delete(self.delete_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        self.another_client.delete(self.delete_url)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_author_can_edit_note(self):
        self.author_client.post(self.edit_url, data=self.form_data)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NEW_NOTE_SLUG)

    def test_user_can_edit_note_of_another_user(self):
        response = self.another_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)
        self.assertEqual(self.note.slug, self.NOTE_SLUG)

    def test_cannot_create_note_with_duplicate_slug(self):
        response = self.author_client.post(
            self.add_url,
            data=self.form_data_same_slug
        )
        self.assertNotEqual(
            response.status_code,
            HTTPStatus.FOUND,
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_can_create_note_without_slug(self):
        response = self.author_client.post(
            self.add_url,
            data=self.form_data_without_slug
        )
        self.assertRedirects(response, self.url_success)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 2)
        created_note = Note.objects.get(
            title=self.form_data_without_slug['title']
        )
        expected_slug = slugify(self.form_data_without_slug['title'])
        self.assertEqual(created_note.slug, expected_slug)

    @classmethod
    def tearDownClass(cls):
        pass
