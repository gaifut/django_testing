from http import HTTPStatus

from django.contrib.auth import get_user_model


from notes.forms import NoteForm
from notes.models import Note
from .shared_test_input import SharedTestInput
from .shared_urls import (
    NOTE_LIST_URL,
    NOTES_ADD_URL,
    NOTES_EDIT_URL
)

User = get_user_model()


class Notelistpage(SharedTestInput):

    def test_notes_list_display(self):
        self.generate_note_list_author()
        self.assertIn(
            Note.objects.first(),
            self.client_author.get(NOTE_LIST_URL).context['object_list']
        )

    def test_user_cant_see_others_notes(self):
        self.generate_single_note()
        response = self.client_another.get(NOTE_LIST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_create_edit_page(self):
        self.generate_single_note()
        for url in (NOTES_ADD_URL, NOTES_EDIT_URL):
            with self.subTest(name=url):
                response = self.client_author.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
