from django.contrib.auth import get_user_model
from django.test import TestCase
from http import HTTPStatus

from notes.forms import NoteForm
from notes.models import Note
from .shared_test_input import SharedTestInputMixin
from .shared_urls import (
    NOTE_LIST_URL,
    NOTES_ADD_URL,
    NOTES_EDIT_URL
)

User = get_user_model()


class Notelistpage(SharedTestInputMixin, TestCase):

    def test_notes_list_display(self):
        self.login_author()
        self.generate_note_list_author()
        self.assertIsNotNone(Note.objects.first())
        self.assertIn(
            Note.objects.first(),
            self.client_author.get(NOTE_LIST_URL).context['object_list']
        )

    def test_user_cant_see_others_notes(self):
        self.generate_note_list_author()
        self.login_another()
        response = self.client_another.get(NOTE_LIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        author_notes = Note.objects.filter(author=self.user_author).all()
        for author_note in author_notes:
            self.assertNotIn(author_note, response.context['object_list'])

    def test_create_edit_page(self):
        self.generate_single_note()
        self.login_author()
        for name in (NOTES_ADD_URL, NOTES_EDIT_URL):
            with self.subTest(name=name):
                response = self.client_author.get(name)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsNotNone(form)
                self.assertIsInstance(form, NoteForm)
